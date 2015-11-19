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

import logging
import os

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import ValidationError
from toscaparser.utils.gettextutils import _
import toscaparser.utils.urlutils
import toscaparser.utils.yamlparser

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml
log = logging.getLogger("tosca")


class ImportsLoader(object):

    IMPORTS_SECTION = (FILE, REPOSITORY, NAMESPACE_URI, NAMESPACE_PREFIX) = \
                      ('file', 'repository', 'namespace_uri',
                       'namespace_prefix')

    def __init__(self, importslist, path, type_definition_list=None):
        self.importslist = importslist
        self.custom_defs = {}
        if not path:
            msg = _('Input tosca template is not provided.')
            log.warning(msg)
            ExceptionCollector.appendException(ValidationError(message=msg))
        self.path = path
        self.type_definition_list = []
        if type_definition_list:
            if isinstance(type_definition_list, list):
                self.type_definition_list = type_definition_list
            else:
                self.type_definition_list.append(type_definition_list)
        self._validate_and_load_imports()

    def get_custom_defs(self):
        return self.custom_defs

    def _validate_and_load_imports(self):
        imports_names = set()

        if not self.importslist:
            msg = _('"imports" keyname is defined without including '
                    'templates.')
            log.error(msg)
            ExceptionCollector.appendException(ValidationError(message=msg))
            return

        for import_def in self.importslist:
            if isinstance(import_def, dict):
                for import_name, import_uri in import_def.items():
                    if import_name in imports_names:
                        msg = (_('Duplicate import name "%s" was found.') %
                               import_name)
                        log.error(msg)
                        ExceptionCollector.appendException(
                            ValidationError(message=msg))
                    imports_names.add(import_name)

                    custom_type = self._load_import_template(import_name,
                                                             import_uri)
                    self._update_custom_def(custom_type)
            else:  # old style of imports
                custom_type = self._load_import_template(None,
                                                         import_def)
                if custom_type:
                    self._update_custom_def(custom_type)

    def _update_custom_def(self, custom_type):
        outer_custom_types = {}
        for type_def in self.type_definition_list:
            outer_custom_types = custom_type.get(type_def)
            if outer_custom_types:
                if type_def == "imports":
                    self.custom_defs.update({'imports': outer_custom_types})
                else:
                    self.custom_defs.update(outer_custom_types)

    def _validate_import_keys(self, import_name, import_uri_def):
        if self.FILE not in import_uri_def.keys():
            log.warning(_('Missing keyname "file" in import "%(name)s".')
                        % {'name': import_name})
            ExceptionCollector.appendException(
                MissingRequiredFieldError(
                    what='Import of template "%s"' % import_name,
                    required=self.FILE))
        for key in import_uri_def.keys():
            if key not in self.IMPORTS_SECTION:
                log.warning(_('Unknown keyname "%(key)s" error in '
                              'imported definition "%(def)s".')
                            % {'key': key, 'def': import_name})
                ExceptionCollector.appendException(
                    UnknownFieldError(
                        what='Import of template "%s"' % import_name,
                        field=key))

    def _load_import_template(self, import_name, import_uri_def):
        """Handle custom types defined in imported template files

        This method loads the custom type definitions referenced in "imports"
        section of the TOSCA YAML template by determining whether each import
        is specified via a file reference (by relative or absolute path) or a
        URL reference.

        Possibilities:
        +----------+--------+------------------------------+
        | template | import | comment                      |
        +----------+--------+------------------------------+
        | file     | file   | OK                           |
        | file     | URL    | OK                           |
        | URL      | file   | file must be a relative path |
        | URL      | URL    | OK                           |
        +----------+--------+------------------------------+
        """

        short_import_notation = False
        if isinstance(import_uri_def, dict):
            self._validate_import_keys(import_name, import_uri_def)
            file_name = import_uri_def.get(self.FILE)
            repository = import_uri_def.get(self.REPOSITORY)
            namespace_uri = import_uri_def.get(self.NAMESPACE_URI)
            # TODO(anyone) : will be extended this namespace_prefix in
            # the next patch after design discussion with PTL.
            # namespace_prefix = import_uri_def.get(self.NAMESPACE_PREFIX)
        else:
            file_name = import_uri_def
            namespace_uri = None
            short_import_notation = True

        if not file_name:
            msg = (_('A template file name is not provided with import '
                     'definition "%(import_name)s".')
                   % {'import_name': import_name})
            log.error(msg)
            ExceptionCollector.appendException(ValidationError(message=msg))
            return

        if toscaparser.utils.urlutils.UrlUtils.validate_url(file_name):
            return YAML_LOADER(file_name, False)
        elif not namespace_uri:
            import_template = None
            a_file = True
            main_a_file = os.path.isfile(self.path)
            if main_a_file:
                if os.path.isfile(file_name):
                    import_template = file_name
                else:
                    full_path = os.path.join(
                        os.path.dirname(os.path.abspath(self.path)),
                        file_name)
                    if os.path.isfile(full_path):
                        import_template = full_path
            else:  # main_a_url
                if os.path.isabs(file_name):
                    msg = (_('Absolute file name "%(name)s" cannot be used '
                             'in a URL-based input template "%(template)s".')
                           % {'name': file_name, 'template': self.path})
                    log.error(msg)
                    ExceptionCollector.appendException(ImportError(msg))
                    return
                import_template = toscaparser.utils.urlutils.UrlUtils.\
                    join_url(self.path, file_name)
                a_file = False
            if not import_template:
                log.error(_('Import "%(name)s" is not valid.') %
                          {'name': import_uri_def})
                ExceptionCollector.appendException(
                    ImportError(_('Import "%s" is not valid.') %
                                import_uri_def))
                return
            return YAML_LOADER(import_template, a_file)

        if short_import_notation:
            log.error(_('Import "%(name)s" is not valid.') % import_uri_def)
            ExceptionCollector.appendException(
                ImportError(_('Import "%s" is not valid.') % import_uri_def))

        # Remove leading, ending spaces and strip the last character if "/"
        namespace_uri = ((namespace_uri).strip()).rstrip("//")

        if toscaparser.utils.urlutils.UrlUtils.validate_url(namespace_uri):
            full_url = None
            if repository:
                repository = ((repository).strip()).rstrip("//")
                full_url = namespace_uri + "/" + repository + "/" + file_name
            else:
                full_url = namespace_uri + "/" + file_name
            return YAML_LOADER(full_url, False)
        else:
            msg = (_('namespace_uri "%(n_uri)s" is not valid in import '
                     'definition "%(tpl)s".')
                   % {'n_uri': namespace_uri, 'tpl': import_name})
            log.error(msg)
            ExceptionCollector.appendException(ImportError(msg))
