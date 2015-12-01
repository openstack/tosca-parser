#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os.path
import requests
import shutil
import six
import tempfile
import yaml
import zipfile

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import URLException
from toscaparser.common.exception import ValidationError
from toscaparser.imports import ImportsLoader
from toscaparser.utils.gettextutils import _
from toscaparser.utils.urlutils import UrlUtils

try:  # Python 2.x
    from BytesIO import BytesIO
except ImportError:  # Python 3.x
    from io import BytesIO


class CSAR(object):

    def __init__(self, csar_file, a_file=True):
        self.path = csar_file
        self.a_file = a_file
        self.is_validated = False
        self.error_caught = False
        self.csar = None
        self.temp_dir = None

    def validate(self):
        """Validate the provided CSAR file."""

        self.is_validated = True

        # validate that the file or URL exists
        missing_err_msg = (_('"%s" does not exist.') % self.path)
        if self.a_file:
            if not os.path.isfile(self.path):
                ExceptionCollector.appendException(
                    ValidationError(message=missing_err_msg))
                return False
            else:
                self.csar = self.path
        else:  # a URL
            if not UrlUtils.validate_url(self.path):
                ExceptionCollector.appendException(
                    ValidationError(message=missing_err_msg))
                return False
            else:
                response = requests.get(self.path)
                self.csar = BytesIO(response.content)

        # validate that it is a valid zip file
        if not zipfile.is_zipfile(self.csar):
            err_msg = (_('"%s" is not a valid zip file.') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that it contains the metadata file in the correct location
        self.zfile = zipfile.ZipFile(self.csar, 'r')
        filelist = self.zfile.namelist()
        if 'TOSCA-Metadata/TOSCA.meta' not in filelist:
            err_msg = (_('"%s" is not a valid CSAR as it does not contain the '
                         'required file "TOSCA.meta" in the folder '
                         '"TOSCA-Metadata".') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that 'Entry-Definitions' property exists in TOSCA.meta
        data = self.zfile.read('TOSCA-Metadata/TOSCA.meta')
        invalid_yaml_err_msg = (_('The file "TOSCA-Metadata/TOSCA.meta" in '
                                  'the CSAR "%s" does not contain valid YAML '
                                  'content.') % self.path)
        try:
            meta = yaml.load(data)
            if type(meta) is dict:
                self.metadata = meta
            else:
                ExceptionCollector.appendException(
                    ValidationError(message=invalid_yaml_err_msg))
                return False
        except yaml.YAMLError:
            ExceptionCollector.appendException(
                ValidationError(message=invalid_yaml_err_msg))
            return False

        if 'Entry-Definitions' not in self.metadata:
            err_msg = (_('The CSAR "%s" is missing the required metadata '
                         '"Entry-Definitions" in '
                         '"TOSCA-Metadata/TOSCA.meta".')
                       % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that 'Entry-Definitions' metadata value points to an
        # existing file in the CSAR
        entry = self.metadata.get('Entry-Definitions')
        if entry and entry not in filelist:
            err_msg = (_('The "Entry-Definitions" file defined in the '
                         'CSAR "%s" does not exist.') % self.path)
            ExceptionCollector.appendException(
                ValidationError(message=err_msg))
            return False

        # validate that external references in the main template actually
        # exist and are accessible
        self._validate_external_references()
        return not self.error_caught

    def get_metadata(self):
        """Return the metadata dictionary."""

        # validate the csar if not already validated
        if not self.is_validated:
            self.validate()

        # return a copy to avoid changes overwrite the original
        return dict(self.metadata) if self.metadata else None

    def _get_metadata(self, key):
        if not self.is_validated:
            self.validate()
        return self.metadata.get(key)

    def get_author(self):
        return self._get_metadata('Created-By')

    def get_version(self):
        return self._get_metadata('CSAR-Version')

    def get_main_template(self):
        entry_def = self._get_metadata('Entry-Definitions')
        if entry_def in self.zfile.namelist():
            return entry_def

    def get_main_template_yaml(self):
        main_template = self.get_main_template()
        if main_template:
            data = self.zfile.read(main_template)
            invalid_tosca_yaml_err_msg = (
                _('The file "%(template)s" in the CSAR "%(csar)s" does not '
                  'contain valid TOSCA YAML content.') %
                {'template': main_template, 'csar': self.path})
            try:
                tosca_yaml = yaml.load(data)
                if type(tosca_yaml) is not dict:
                    ExceptionCollector.appendException(
                        ValidationError(message=invalid_tosca_yaml_err_msg))
                return tosca_yaml
            except Exception:
                ExceptionCollector.appendException(
                    ValidationError(message=invalid_tosca_yaml_err_msg))

    def get_description(self):
        desc = self._get_metadata('Description')
        if desc is not None:
            return desc

        self.metadata['Description'] = \
            self.get_main_template_yaml().get('description')
        return self.metadata['Description']

    def decompress(self):
        if not self.is_validated:
            self.validate()
        self.temp_dir = tempfile.NamedTemporaryFile().name
        with zipfile.ZipFile(self.csar, "r") as zf:
            zf.extractall(self.temp_dir)

    def _validate_external_references(self):
        """Extracts files referenced in the main template

        These references are currently supported:
        * imports
        * interface implementations
        * artifacts
        """
        try:
            self.decompress()
            main_tpl_file = self.get_main_template()
            if not main_tpl_file:
                return
            main_tpl = self.get_main_template_yaml()

            if 'imports' in main_tpl:
                ImportsLoader(main_tpl['imports'],
                              os.path.join(self.temp_dir, main_tpl_file))

            if 'topology_template' in main_tpl:
                topology_template = main_tpl['topology_template']

                if 'node_templates' in topology_template:
                    node_templates = topology_template['node_templates']

                    for node_template_key in node_templates:
                        node_template = node_templates[node_template_key]
                        if 'artifacts' in node_template:
                            artifacts = node_template['artifacts']
                            for artifact_key in artifacts:
                                artifact = artifacts[artifact_key]
                                if isinstance(artifact, six.string_types):
                                    self._validate_external_reference(
                                        main_tpl_file,
                                        artifact)
                                elif isinstance(artifact, dict):
                                    if 'file' in artifact:
                                        self._validate_external_reference(
                                            main_tpl_file,
                                            artifact['file'])
                                else:
                                    ExceptionCollector.appendException(
                                        ValueError(_('Unexpected artifact '
                                                     'definition for "%s".')
                                                   % artifact_key))
                                    self.error_caught = True
                        if 'interfaces' in node_template:
                            interfaces = node_template['interfaces']
                            for interface_key in interfaces:
                                interface = interfaces[interface_key]
                                for opertation_key in interface:
                                    operation = interface[opertation_key]
                                    if isinstance(operation, six.string_types):
                                        self._validate_external_reference(
                                            main_tpl_file,
                                            operation,
                                            False)
                                    elif isinstance(operation, dict):
                                        if 'implementation' in operation:
                                            self._validate_external_reference(
                                                main_tpl_file,
                                                operation['implementation'])
        finally:
            if self.temp_dir:
                shutil.rmtree(self.temp_dir)

    def _validate_external_reference(self, tpl_file, resource_file,
                                     raise_exc=True):
        """Verify that the external resource exists

        If resource_file is a URL verify that the URL is valid.
        If resource_file is a relative path verify that the path is valid
        considering base folder (self.temp_dir) and tpl_file.
        Note that in a CSAR resource_file cannot be an absolute path.
        """
        if UrlUtils.validate_url(resource_file):
            msg = (_('The resource at "%s" cannot be accessed.') %
                   resource_file)
            try:
                if UrlUtils.url_accessible(resource_file):
                    return
                else:
                    ExceptionCollector.appendException(
                        URLException(what=msg))
                    self.error_caught = True
            except Exception:
                ExceptionCollector.appendException(
                    URLException(what=msg))
                self.error_caught = True

        if os.path.isfile(os.path.join(self.temp_dir,
                                       os.path.dirname(tpl_file),
                                       resource_file)):
            return

        if raise_exc:
            ExceptionCollector.appendException(
                ValueError(_('The resource "%s" does not exist.')
                           % resource_file))
            self.error_caught = True
