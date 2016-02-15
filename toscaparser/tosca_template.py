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
from toscaparser.common.exception import InvalidTemplateVersion
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import ValidationError
from toscaparser.elements.entity_type import update_definitions
from toscaparser.extensions.exttools import ExtTools
import toscaparser.imports
from toscaparser.prereq.csar import CSAR
from toscaparser.topology_template import TopologyTemplate
from toscaparser.tpl_relationship_graph import ToscaGraph
from toscaparser.utils.gettextutils import _
import toscaparser.utils.yamlparser


# TOSCA template key names
SECTIONS = (DEFINITION_VERSION, DEFAULT_NAMESPACE, TEMPLATE_NAME,
            TOPOLOGY_TEMPLATE, TEMPLATE_AUTHOR, TEMPLATE_VERSION,
            DESCRIPTION, IMPORTS, DSL_DEFINITIONS, NODE_TYPES,
            RELATIONSHIP_TYPES, RELATIONSHIP_TEMPLATES,
            CAPABILITY_TYPES, ARTIFACT_TYPES, DATA_TYPES,
            POLICY_TYPES, GROUP_TYPES, REPOSITORIES) = \
           ('tosca_definitions_version', 'tosca_default_namespace',
            'template_name', 'topology_template', 'template_author',
            'template_version', 'description', 'imports', 'dsl_definitions',
            'node_types', 'relationship_types', 'relationship_templates',
            'capability_types', 'artifact_types', 'data_types',
            'policy_types', 'group_types', 'repositories')
# Sections that are specific to individual template definitions
SPECIAL_SECTIONS = (METADATA) = ('metadata')

log = logging.getLogger("tosca.model")

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class ToscaTemplate(object):
    exttools = ExtTools()

    VALID_TEMPLATE_VERSIONS = ['tosca_simple_yaml_1_0']

    VALID_TEMPLATE_VERSIONS.extend(exttools.get_versions())

    ADDITIONAL_SECTIONS = {'tosca_simple_yaml_1_0': SPECIAL_SECTIONS}

    ADDITIONAL_SECTIONS.update(exttools.get_sections())

    '''Load the template data.'''
    def __init__(self, path=None, parsed_params=None, a_file=True,
                 yaml_dict_tpl=None):
        ExceptionCollector.start()
        self.a_file = a_file
        self.input_path = None
        self.path = None
        self.tpl = None
        if path:
            self.input_path = path
            self.path = self._get_path(path)
            if self.path:
                self.tpl = YAML_LOADER(self.path, self.a_file)
            if yaml_dict_tpl:
                msg = (_('Both path and yaml_dict_tpl arguments were '
                         'provided. Using path and ignoring yaml_dict_tpl.'))
                log.info(msg)
                print(msg)
        else:
            if yaml_dict_tpl:
                self.tpl = yaml_dict_tpl
            else:
                ExceptionCollector.appendException(
                    ValueError(_('No path or yaml_dict_tpl was provided. '
                                 'There is nothing to parse.')))

        if self.tpl:
            self.parsed_params = parsed_params
            self._validate_field()
            self.version = self._tpl_version()
            self.relationship_types = self._tpl_relationship_types()
            self.description = self._tpl_description()
            self.topology_template = self._topology_template()
            if self.topology_template.tpl:
                self.inputs = self._inputs()
                self.relationship_templates = self._relationship_templates()
                self.nodetemplates = self._nodetemplates()
                self.outputs = self._outputs()
                self.graph = ToscaGraph(self.nodetemplates)

        ExceptionCollector.stop()
        self.verify_template()

    def _topology_template(self):
        return TopologyTemplate(self._tpl_topology_template(),
                                self._get_all_custom_defs(),
                                self.relationship_types,
                                self.parsed_params)

    def _inputs(self):
        return self.topology_template.inputs

    def _nodetemplates(self):
        return self.topology_template.nodetemplates

    def _relationship_templates(self):
        return self.topology_template.relationship_templates

    def _outputs(self):
        return self.topology_template.outputs

    def _tpl_version(self):
        return self.tpl.get(DEFINITION_VERSION)

    def _tpl_description(self):
        desc = self.tpl.get(DESCRIPTION)
        if desc:
            return desc.rstrip()

    def _tpl_imports(self):
        return self.tpl.get(IMPORTS)

    def _tpl_relationship_types(self):
        return self._get_custom_types(RELATIONSHIP_TYPES)

    def _tpl_relationship_templates(self):
        topology_template = self._tpl_topology_template()
        return topology_template.get(RELATIONSHIP_TEMPLATES)

    def _tpl_topology_template(self):
        return self.tpl.get(TOPOLOGY_TEMPLATE)

    def _get_all_custom_defs(self, imports=None):
        types = [IMPORTS, NODE_TYPES, CAPABILITY_TYPES, RELATIONSHIP_TYPES,
                 DATA_TYPES, POLICY_TYPES, GROUP_TYPES]
        custom_defs_final = {}
        custom_defs = self._get_custom_types(types, imports)
        if custom_defs:
            custom_defs_final.update(custom_defs)
            if custom_defs.get(IMPORTS):
                import_defs = self._get_all_custom_defs(
                    custom_defs.get(IMPORTS))
                custom_defs_final.update(import_defs)

        # As imports are not custom_types, removing from the dict
        custom_defs_final.pop(IMPORTS, None)
        return custom_defs_final

    def _get_custom_types(self, type_definitions, imports=None):
        """Handle custom types defined in imported template files

        This method loads the custom type definitions referenced in "imports"
        section of the TOSCA YAML template.
        """

        custom_defs = {}
        type_defs = []
        if not isinstance(type_definitions, list):
            type_defs.append(type_definitions)
        else:
            type_defs = type_definitions

        if not imports:
            imports = self._tpl_imports()

        if imports:
            custom_defs = toscaparser.imports.\
                ImportsLoader(imports, self.path,
                              type_defs, self.tpl).get_custom_defs()
            if not custom_defs:
                return

        # Handle custom types defined in current template file
        for type_def in type_defs:
            if type_def != IMPORTS:
                inner_custom_types = self.tpl.get(type_def) or {}
                if inner_custom_types:
                    custom_defs.update(inner_custom_types)
        return custom_defs

    def _validate_field(self):
        version = self._tpl_version()
        if not version:
            ExceptionCollector.appendException(
                MissingRequiredFieldError(what='Template',
                                          required=DEFINITION_VERSION))
        else:
            self._validate_version(version)
            self.version = version

        for name in self.tpl:
            if (name not in SECTIONS and
               name not in self.ADDITIONAL_SECTIONS.get(version, ())):
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Template', field=name))

    def _validate_version(self, version):
        if version not in self.VALID_TEMPLATE_VERSIONS:
            ExceptionCollector.appendException(
                InvalidTemplateVersion(
                    what=version,
                    valid_versions=', '. join(self.VALID_TEMPLATE_VERSIONS)))
        else:
            if version != 'tosca_simple_yaml_1_0':
                update_definitions(version)

    def _get_path(self, path):
        if path.lower().endswith('.yaml'):
            return path
        elif path.lower().endswith(('.zip', '.csar')):
            # a CSAR archive
            csar = CSAR(path, self.a_file)
            if csar.validate():
                csar.decompress()
                self.a_file = True  # the file has been decompressed locally
                return os.path.join(csar.temp_dir, csar.get_main_template())
        else:
            ExceptionCollector.appendException(
                ValueError(_('"%(path)s" is not a valid file.')
                           % {'path': path}))

    def verify_template(self):
        if ExceptionCollector.exceptionsCaught():
            if self.input_path:
                raise ValidationError(
                    message=(_('\nThe input "%(path)s" failed validation with '
                               'the following error(s): \n\n\t')
                             % {'path': self.input_path}) +
                    '\n\t'.join(ExceptionCollector.getExceptionsReport()))
            else:
                raise ValidationError(
                    message=_('\nThe pre-parsed input failed validation with '
                              'the following error(s): \n\n\t') +
                    '\n\t'.join(ExceptionCollector.getExceptionsReport()))
        else:
            if self.input_path:
                msg = (_('The input "%(path)s" successfully passed '
                         'validation.') % {'path': self.input_path})
            else:
                msg = _('The pre-parsed input successfully passed validation.')

            log.info(msg)
