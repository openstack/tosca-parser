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

from toscaparser.common.exception import InvalidTemplateVersion
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
import toscaparser.imports
from toscaparser.prereq.csar import CSAR
from toscaparser.topology_template import TopologyTemplate
from toscaparser.tpl_relationship_graph import ToscaGraph
import toscaparser.utils.yamlparser


# TOSCA template key names
SECTIONS = (DEFINITION_VERSION, DEFAULT_NAMESPACE, TEMPLATE_NAME,
            TOPOLOGY_TEMPLATE, TEMPLATE_AUTHOR, TEMPLATE_VERSION,
            DESCRIPTION, IMPORTS, DSL_DEFINITIONS, NODE_TYPES,
            RELATIONSHIP_TYPES, RELATIONSHIP_TEMPLATES,
            CAPABILITY_TYPES, ARTIFACT_TYPES, DATATYPE_DEFINITIONS) = \
           ('tosca_definitions_version', 'tosca_default_namespace',
            'template_name', 'topology_template', 'template_author',
            'template_version', 'description', 'imports', 'dsl_definitions',
            'node_types', 'relationship_types', 'relationship_templates',
            'capability_types', 'artifact_types', 'datatype_definitions')
# Special key names
SPECIAL_SECTIONS = (METADATA) = ('metadata')

log = logging.getLogger("tosca.model")

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class ToscaTemplate(object):

    VALID_TEMPLATE_VERSIONS = ['tosca_simple_yaml_1_0']

    '''Load the template data.'''
    def __init__(self, path, parsed_params=None, a_file=True):
        self.a_file = a_file
        self.path = self._get_path(path)
        self.tpl = YAML_LOADER(self.path, self.a_file)
        self.parsed_params = parsed_params
        self._validate_field()
        self.version = self._tpl_version()
        self.relationship_types = self._tpl_relationship_types()
        self.description = self._tpl_description()
        self.topology_template = self._topology_template()
        self.inputs = self._inputs()
        self.relationship_templates = self._relationship_templates()
        self.nodetemplates = self._nodetemplates()
        self.outputs = self._outputs()
        self.graph = ToscaGraph(self.nodetemplates)

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
        return self.tpl[DEFINITION_VERSION]

    def _tpl_description(self):
        return self.tpl[DESCRIPTION].rstrip()

    def _tpl_imports(self):
        if IMPORTS in self.tpl:
            return self.tpl[IMPORTS]

    def _tpl_relationship_types(self):
        return self._get_custom_types(RELATIONSHIP_TYPES)

    def _tpl_relationship_templates(self):
        topology_template = self._tpl_topology_template()
        if RELATIONSHIP_TEMPLATES in topology_template.keys():
            return topology_template[RELATIONSHIP_TEMPLATES]
        else:
            return None

    def _tpl_topology_template(self):
        return self.tpl.get(TOPOLOGY_TEMPLATE)

    def _get_all_custom_defs(self):
        types = [NODE_TYPES, CAPABILITY_TYPES, RELATIONSHIP_TYPES,
                 DATATYPE_DEFINITIONS]
        custom_defs = {}
        for type in types:
            custom_def = self._get_custom_types(type)
            if custom_def:
                custom_defs.update(custom_def)
        return custom_defs

    def _get_custom_types(self, type_definition):
        """Handle custom types defined in imported template files

        This method loads the custom type definitions referenced in "imports"
        section of the TOSCA YAML template.
        """

        custom_defs = {}
        imports = self._tpl_imports()
        if imports:
            custom_defs = toscaparser.imports.\
                ImportsLoader(imports, self.path,
                              type_definition).get_custom_defs()

        # Handle custom types defined in current template file
        inner_custom_types = self.tpl.get(type_definition) or {}
        if inner_custom_types:
            custom_defs.update(inner_custom_types)
        return custom_defs

    def _validate_field(self):
        try:
            version = self._tpl_version()
            self._validate_version(version)
        except KeyError:
            raise MissingRequiredFieldError(what='Template',
                                            required=DEFINITION_VERSION)
        for name in self.tpl:
            if name not in SECTIONS and name not in SPECIAL_SECTIONS:
                raise UnknownFieldError(what='Template', field=name)

    def _validate_version(self, version):
        if version not in self.VALID_TEMPLATE_VERSIONS:
            raise InvalidTemplateVersion(
                what=version,
                valid_versions=', '. join(self.VALID_TEMPLATE_VERSIONS))

    def _get_path(self, path):
        if path.lower().endswith('.yaml'):
            return path
        elif path.lower().endswith('.zip'):
            # a CSAR archive
            csar = CSAR(path, self.a_file)
            csar.validate()
            folder = csar.decompress()
            self.a_file = True  # the file has been decompressed locally
            return os.path.join(folder, csar.get_main_template())
        else:
            raise ValueError(_("%(path)s is not a valid file.")
                             % {'path': path})
