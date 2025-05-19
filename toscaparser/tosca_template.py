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

from copy import deepcopy
from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTemplateVersion
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import ValidationError
from toscaparser.elements.entity_type import update_definitions
from toscaparser.extensions.exttools import ExtTools
import toscaparser.imports
from toscaparser.prereq.csar import CSAR
from toscaparser.repositories import Repository
from toscaparser.topology_template import TopologyTemplate
from toscaparser.tpl_relationship_graph import ToscaGraph
from toscaparser.utils.gettextutils import _
import toscaparser.utils.yamlparser


# TOSCA template key names
SECTIONS = (DEFINITION_VERSION, DEFAULT_NAMESPACE, TEMPLATE_NAME,
            TOPOLOGY_TEMPLATE, TEMPLATE_AUTHOR, TEMPLATE_VERSION,
            DESCRIPTION, IMPORTS, DSL_DEFINITIONS, NODE_TYPES,
            RELATIONSHIP_TYPES, RELATIONSHIP_TEMPLATES,
            CAPABILITY_TYPES, ARTIFACT_TYPES, DATA_TYPES, INTERFACE_TYPES,
            POLICY_TYPES, GROUP_TYPES, REPOSITORIES) = \
           ('tosca_definitions_version', 'tosca_default_namespace',
            'template_name', 'topology_template', 'template_author',
            'template_version', 'description', 'imports', 'dsl_definitions',
            'node_types', 'relationship_types', 'relationship_templates',
            'capability_types', 'artifact_types', 'data_types',
            'interface_types', 'policy_types', 'group_types', 'repositories')
# Sections that are specific to individual template definitions
SPECIAL_SECTIONS = (METADATA) = ('metadata')

log = logging.getLogger("tosca.model")

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class ToscaTemplate(object):
    exttools = ExtTools()

    MAIN_TEMPLATE_VERSIONS = ['tosca_simple_yaml_1_0',
                              'tosca_simple_yaml_1_2',
                              'tosca_simple_yaml_1_3']

    VALID_TEMPLATE_VERSIONS = MAIN_TEMPLATE_VERSIONS + exttools.get_versions()

    ADDITIONAL_SECTIONS = {'tosca_simple_yaml_1_0': SPECIAL_SECTIONS,
                           'tosca_simple_yaml_1_2': SPECIAL_SECTIONS,
                           'tosca_simple_yaml_1_3': SPECIAL_SECTIONS}

    ADDITIONAL_SECTIONS.update(exttools.get_sections())

    '''Load the template data.'''
    def __init__(self, path=None, parsed_params=None, a_file=True,
                 yaml_dict_tpl=None, local_defs=None):

        ExceptionCollector.start()
        self.a_file = a_file
        self.input_path = None
        self.path = None
        self.tpl = None
        self.nested_tosca_tpls_with_topology = {}
        self.nested_tosca_templates_with_topology = []
        self.local_defs = local_defs

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
            self.repositories = self._tpl_repositories()
            if self.topology_template.tpl:
                self.inputs = self._inputs()
                self.relationship_templates = self._relationship_templates()
                self.nodetemplates = self._nodetemplates()
                self.outputs = self._outputs()
                self.policies = self._policies()
                self._handle_nested_tosca_templates_with_topology()
                self.graph = ToscaGraph(self.nodetemplates)
                self._validate_relationship_occurences()

        ExceptionCollector.stop()
        self.verify_template()

    def _validate_relationship_occurences(self):
        for tpl in self.nodetemplates:
            # Check if the requirements has a correct number of occurrences
            tpl._validate_relationship_occurrences()

    def _topology_template(self):
        return TopologyTemplate(self._tpl_topology_template(),
                                self._get_all_custom_defs(),
                                self.relationship_types,
                                self.parsed_params,
                                None)

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

    def _tpl_repositories(self):
        repositories = self.tpl.get(REPOSITORIES)
        reposit = []
        if repositories:
            for name, val in repositories.items():
                reposits = Repository(name, val)
                reposit.append(reposits)
        return reposit

    def _tpl_relationship_types(self):
        custom_rel, _ = self._get_custom_types(RELATIONSHIP_TYPES)
        return custom_rel

    def _tpl_relationship_templates(self):
        topology_template = self._tpl_topology_template()
        return topology_template.get(RELATIONSHIP_TEMPLATES)

    def _tpl_topology_template(self):
        return self.tpl.get(TOPOLOGY_TEMPLATE)

    def _policies(self):
        return self.topology_template.policies

    def _get_all_custom_defs(self, imports=None, path=None):
        types = [IMPORTS, NODE_TYPES, CAPABILITY_TYPES, RELATIONSHIP_TYPES,
                 DATA_TYPES, INTERFACE_TYPES, POLICY_TYPES, GROUP_TYPES]
        custom_defs_final = {}

        custom_defs, nested_imports = self._get_custom_types(
            types, imports, path)
        if custom_defs:
            custom_defs_final.update(custom_defs)
            if nested_imports:
                for a_file, nested_import in nested_imports.items():
                    import_defs = self._get_all_custom_defs(
                        nested_import, a_file)
                    custom_defs_final.update(import_defs)

        # As imports are not custom_types, removing from the dict
        custom_defs_final.pop(IMPORTS, None)
        return custom_defs_final

    def _get_custom_types(self, type_definitions, imports=None,
                          path=None):
        """Handle custom types defined in imported template files

        This method loads the custom type definitions referenced in "imports"
        section of the TOSCA YAML template.
        """

        custom_defs = {}
        nested_imports = None
        type_defs = []
        if not isinstance(type_definitions, list):
            type_defs.append(type_definitions)
        else:
            type_defs = type_definitions

        if not imports:
            imports = self._tpl_imports()
        if not path:
            path = self.path

        if imports:
            custom_service = toscaparser.imports.\
                ImportsLoader(imports, path, type_defs, self.tpl,
                              self.local_defs)

            nested_tosca_tpls = custom_service.get_nested_tosca_tpls()
            self._update_nested_tosca_tpls_with_topology(nested_tosca_tpls)

            nested_imports = custom_service.get_nested_imports()
            custom_defs = custom_service.get_custom_defs()
            if not custom_defs:
                return None, None

        # Handle custom types defined in current template file
        for type_def in type_defs:
            if type_def != IMPORTS:
                inner_custom_types = self.tpl.get(type_def) or {}
                if inner_custom_types:
                    custom_defs.update(inner_custom_types)
        return custom_defs, nested_imports

    def _update_nested_tosca_tpls_with_topology(self, nested_tosca_tpls):
        for tpl in nested_tosca_tpls:
            filename, tosca_tpl = list(tpl.items())[0]
            if (tosca_tpl.get(TOPOLOGY_TEMPLATE) and
                filename not in list(
                    self.nested_tosca_tpls_with_topology.keys())):
                self.nested_tosca_tpls_with_topology.update(tpl)

    def _handle_nested_tosca_templates_with_topology(self):
        for fname, tosca_tpl in self.nested_tosca_tpls_with_topology.items():
            for nodetemplate in self.nodetemplates:
                if self._is_sub_mapped_node(nodetemplate, tosca_tpl):
                    parsed_params = self._get_params_for_nested_template(
                        nodetemplate)
                    topology_tpl = tosca_tpl.get(TOPOLOGY_TEMPLATE)
                    topology_with_sub_mapping = TopologyTemplate(
                        topology_tpl,
                        self._get_all_custom_defs(),
                        self.relationship_types,
                        parsed_params,
                        nodetemplate)
                    if topology_with_sub_mapping.substitution_mappings:
                        # Record nested topo templates in top level template
                        self.nested_tosca_templates_with_topology.\
                            append(topology_with_sub_mapping)
                        # Set substitution mapping object for mapped node
                        nodetemplate.sub_mapping_tosca_template = \
                            topology_with_sub_mapping.substitution_mappings

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
                    valid_versions='", "'. join(self.VALID_TEMPLATE_VERSIONS)))
        else:
            if version not in self.MAIN_TEMPLATE_VERSIONS:
                update_definitions(version)

    def _get_path(self, path):
        if path.lower().endswith('.yaml') or path.lower().endswith('.yml'):
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

    def _is_sub_mapped_node(self, nodetemplate, tosca_tpl):
        """Return True if the nodetemple is substituted."""
        # NOTE(ueha): Since condition "not nodetemplate.sub_mapping_tosca_\
        #             template" was deleted as a fix for bug/1883220, there is
        #             some possibility of breaking something on translator side
        #             that current tests not coverd.
        #             And this enhancement does not align with TOSCA standard
        #             but needed for ETSI NFV-SOL 001.
        if (nodetemplate and
                self.get_sub_mapping_node_type(tosca_tpl) == nodetemplate.type
                and len(nodetemplate.interfaces) < 1):
            return True
        else:
            return False

    def _get_params_for_nested_template(self, nodetemplate):
        """Return total params for nested_template."""
        parsed_params = deepcopy(self.parsed_params) \
            if self.parsed_params else {}
        if nodetemplate:
            for pname in nodetemplate.get_properties():
                parsed_params.update({pname:
                                      nodetemplate.get_property_value(pname)})
        return parsed_params

    def get_sub_mapping_node_type(self, tosca_tpl):
        """Return substitution mappings node type."""
        if tosca_tpl:
            return TopologyTemplate.get_sub_mapping_node_type(
                tosca_tpl.get(TOPOLOGY_TEMPLATE))

    def _has_substitution_mappings(self):
        """Return True if the template has valid substitution mappings."""
        return self.topology_template is not None and \
            self.topology_template.substitution_mappings is not None

    def has_nested_templates(self):
        """Return True if the tosca template has nested templates."""
        return self.nested_tosca_templates_with_topology is not None and \
            len(self.nested_tosca_templates_with_topology) >= 1
