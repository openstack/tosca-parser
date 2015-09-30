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
import six
import tempfile
import yaml
import zipfile

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
        self.csar_file = csar_file
        self.a_file = a_file
        self.is_validated = False

    def validate(self):
        """Validate the provided CSAR file."""

        self.is_validated = True

        # validate that the file exists
        if self.a_file and not os.path.isfile(self.csar_file):
            err_msg = (_('The file %s does not exist.') % self.csar_file)
            raise ValidationError(message=err_msg)

        if not self.a_file:  # a URL
            if not UrlUtils.validate_url(self.csar_file):
                err_msg = (_('The URL %s does not exist.') % self.csar_file)
                raise ValidationError(message=err_msg)
            else:
                response = requests.get(self.csar_file)
                self.csar_file = BytesIO(response.content)

        # validate that it is a valid zip file
        if not zipfile.is_zipfile(self.csar_file):
            err_msg = (_('The file %s is not a valid zip file.')
                       % self.csar_file)
            raise ValidationError(message=err_msg)

        # validate that it contains the metadata file in the correct location
        self.zfile = zipfile.ZipFile(self.csar_file, 'r')
        filelist = self.zfile.namelist()
        if 'TOSCA-Metadata/TOSCA.meta' not in filelist:
            err_msg = (_('The file %s is not a valid CSAR as it does not '
                         'contain the required file "TOSCA.meta" in the '
                         'folder "TOSCA-Metadata".') % self.csar_file)
            raise ValidationError(message=err_msg)

        # validate that 'Entry-Definitions' property exists in TOSCA.meta
        data = self.zfile.read('TOSCA-Metadata/TOSCA.meta')
        invalid_yaml_err_msg = (_('The file "TOSCA-Metadata/TOSCA.meta" in %s '
                                  'does not contain valid YAML content.') %
                                self.csar_file)
        try:
            meta = yaml.load(data)
            if type(meta) is not dict:
                raise ValidationError(message=invalid_yaml_err_msg)
            self.metadata = meta
        except yaml.YAMLError:
            raise ValidationError(message=invalid_yaml_err_msg)

        if 'Entry-Definitions' not in self.metadata:
            err_msg = (_('The CSAR file "%s" is missing the required metadata '
                         '"Entry-Definitions" in "TOSCA-Metadata/TOSCA.meta".')
                       % self.csar_file)
            raise ValidationError(message=err_msg)

        # validate that 'Entry-Definitions' metadata value points to an
        # existing file in the CSAR
        entry = self.metadata['Entry-Definitions']
        if entry not in filelist:
            err_msg = (_('The "Entry-Definitions" file defined in the CSAR '
                         '"%s" does not exist.') % self.csar_file)
            raise ValidationError(message=err_msg)

        # validate that external references in the main template actually exist
        # and are accessible
        self._validate_external_references()

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
        return self.metadata[key] if key in self.metadata else None

    def get_author(self):
        return self._get_metadata('Created-By')

    def get_version(self):
        return self._get_metadata('CSAR-Version')

    def get_main_template(self):
        return self._get_metadata('Entry-Definitions')

    def get_main_template_yaml(self):
        main_template = self.get_main_template()
        data = self.zfile.read(main_template)
        invalid_tosca_yaml_err_msg = (
            _('The file %(template)s in %(csar)s does not contain valid TOSCA '
              'YAML content.') % {'template': main_template,
                                  'csar': self.csar_file})
        try:
            tosca_yaml = yaml.load(data)
            if type(tosca_yaml) is not dict:
                raise ValidationError(message=invalid_tosca_yaml_err_msg)
            return tosca_yaml
        except Exception:
            raise ValidationError(message=invalid_tosca_yaml_err_msg)

    def get_description(self):
        desc = self._get_metadata('Description')
        if desc is not None:
            return desc

        self.metadata['Description'] = \
            self.get_main_template_yaml()['description']
        return self.metadata['Description']

    def decompress(self):
        if not self.is_validated:
            self.validate()
        folder = tempfile.NamedTemporaryFile().name
        with zipfile.ZipFile(self.csar_file, "r") as zf:
            zf.extractall(folder)
        return folder

    def _validate_external_references(self):
        """Extracts files referenced in the main template

        These references are currently supported:
        * imports
        * interface implementations
        * artifacts
        """
        temp_dir = self.decompress()
        main_tpl_file = self.get_main_template()
        main_tpl = self.get_main_template_yaml()

        if 'imports' in main_tpl:
            ImportsLoader(main_tpl['imports'],
                          os.path.join(temp_dir, main_tpl_file))

        if 'topology_template' not in main_tpl:
            return
        topology_template = main_tpl['topology_template']

        if 'node_templates' not in topology_template:
            return
        node_templates = topology_template['node_templates']

        for node_template_key in node_templates:
            node_template = node_templates[node_template_key]
            if 'artifacts' in node_template:
                artifacts = node_template['artifacts']
                for artifact_key in artifacts:
                    artifact = artifacts[artifact_key]
                    if isinstance(artifact, six.string_types):
                        self._validate_external_reference(temp_dir,
                                                          main_tpl_file,
                                                          artifact)
                    elif isinstance(artifact, dict):
                        if 'file' in artifact:
                            self._validate_external_reference(temp_dir,
                                                              main_tpl_file,
                                                              artifact['file'])
                    else:
                        raise ValueError(_('Unexpected artifact definition '
                                           'for %s.') % artifact_key)
            if 'interfaces' in node_template:
                interfaces = node_template['interfaces']
                for interface_key in interfaces:
                    interface = interfaces[interface_key]
                    for opertation_key in interface:
                        operation = interface[opertation_key]
                        if isinstance(operation, six.string_types):
                            self._validate_external_reference(temp_dir,
                                                              main_tpl_file,
                                                              operation,
                                                              False)
                        elif isinstance(operation, dict):
                            if 'implementation' in operation:
                                self._validate_external_reference(
                                    temp_dir, main_tpl_file,
                                    operation['implementation'])

    def _validate_external_reference(self, base_dir, tpl_file, resource_file,
                                     raise_exc=True):
        """Verify that the external resource exists

        If resource_file is a URL verify that the URL is valid.
        If resource_file is a relative path verify that the path is valid
        considering base_dir and tpl_file.
        Note that in a CSAR resource_file cannot be an absolute path.
        """
        if UrlUtils.validate_url(resource_file):
            msg = (_('The resource at %s cannot be accessed') % resource_file)
            try:
                if UrlUtils.url_accessible(resource_file):
                    return
                else:
                    raise URLException(what=msg)
            except Exception:
                raise URLException(what=msg)

        if os.path.isfile(os.path.join(base_dir,
                                       os.path.dirname(tpl_file),
                                       resource_file)):
            return

        if raise_exc:
            raise ValueError(_('The resource %s does not exist.')
                             % resource_file)
