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

from translator.toscalib.common.exception import InvalidTemplateVersion
from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib import functions
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.parameters import Input, Output
from translator.toscalib.relationship_template import RelationshipTemplate
from translator.toscalib.tpl_relationship_graph import ToscaGraph

import translator.toscalib.utils.yamlparser


#TOSCA template key names
SECTIONS = (DEFINITION_VERSION, DEFAULT_NAMESPACE, TEMPLATE_NAME,
            TEMPLATE_AUTHOR, TEMPLATE_VERSION, DESCRIPTION, IMPORTS,
            DSL_DEFINITIONS, INPUTS, NODE_TEMPLATES, RELATIONSHIP_TEMPLATES,
            NODE_TYPES, RELATIONSHIP_TYPES, CAPABILITY_TYPES, ARTIFACT_TYPES,
            OUTPUTS, GROUPS, DATATYPE_DEFINITIONS) = \
           ('tosca_definitions_version', 'tosca_default_namespace',
            'template_name', 'template_author', 'template_version',
            'description', 'imports', 'dsl_definitions', 'inputs',
            'node_templates', 'relationship_templates', 'node_types',
            'relationship_types', 'capability_types', 'artifact_types',
            'outputs', 'groups', 'datatype_definitions')

log = logging.getLogger("tosca.model")

YAML_LOADER = translator.toscalib.utils.yamlparser.load_yaml


class ToscaTemplate(object):

    VALID_TEMPLATE_VERSIONS = ['tosca_simple_yaml_1_0_0']

    '''Load the template data.'''
    def __init__(self, path):
        self.tpl = YAML_LOADER(path)
        self.path = path
        self._validate_field()
        self.version = self._tpl_version()
        self.description = self._tpl_description()
        self.inputs = self._inputs()
        self.relationship_templates = self._relationship_templates()
        self.nodetemplates = self._nodetemplates()
        self.outputs = self._outputs()
        self.graph = ToscaGraph(self.nodetemplates)
        self._process_intrinsic_functions()

    def _inputs(self):
        inputs = []
        for name, attrs in self._tpl_inputs().items():
            input = Input(name, attrs)
            input.validate()
            inputs.append(input)
        return inputs

    def _nodetemplates(self):
        custom_defs = {}
        node_types = self._get_custom_types(NODE_TYPES)
        if node_types:
            custom_defs.update(node_types)
        data_types = self._get_custom_types(DATATYPE_DEFINITIONS)
        if data_types:
            custom_defs.update(data_types)
        capability_types = self._get_custom_types(CAPABILITY_TYPES)
        if capability_types:
            custom_defs.update(capability_types)
        nodetemplates = []
        tpls = self._tpl_nodetemplates()
        for name in tpls:
            tpl = NodeTemplate(name, tpls, custom_defs,
                               self.relationship_templates)
            tpl.validate(self)
            nodetemplates.append(tpl)
        return nodetemplates

    def _relationship_templates(self):
        custom_defs = self._get_custom_types(RELATIONSHIP_TYPES)

        rel_templates = []
        tpls = self._tpl_relationship_templates()
        for name in tpls:
            tpl = RelationshipTemplate(tpls[name], name, custom_defs)
            rel_templates.append(tpl)
        return rel_templates

    def _outputs(self):
        outputs = []
        for name, attrs in self._tpl_outputs().items():
            output = Output(name, attrs)
            output.validate()
            outputs.append(output)
        return outputs

    def _tpl_version(self):
        return self.tpl[DEFINITION_VERSION]

    def _tpl_description(self):
        return self.tpl[DESCRIPTION].rstrip()

    def _tpl_imports(self):
        if IMPORTS in self.tpl:
            return self.tpl[IMPORTS]

    def _tpl_inputs(self):
        return self.tpl.get(INPUTS) or {}

    def _tpl_nodetemplates(self):
        return self.tpl[NODE_TEMPLATES]

    def _get_custom_types(self, type_definition):
        # Handle custom types defined in outer template file
        custom_defs = {}
        imports = self._tpl_imports()
        if imports:
            for definition in imports:
                if os.path.isabs(definition):
                    def_file = definition
                else:
                    tpl_dir = os.path.dirname(os.path.abspath(self.path))
                    def_file = os.path.join(tpl_dir, definition)
                custom_type = YAML_LOADER(def_file)
                outer_custom_types = custom_type.get(type_definition)
                if outer_custom_types:
                    custom_defs.update(outer_custom_types)

        # Handle custom types defined in current template file
        inner_custom_types = self.tpl.get(type_definition) or {}
        if inner_custom_types:
            custom_defs.update(inner_custom_types)
        return custom_defs

    def _tpl_relationship_templates(self):
        return self.tpl.get(RELATIONSHIP_TEMPLATES) or {}

    def _tpl_relationship_types(self):
        return self._get_custom_types(RELATIONSHIP_TYPES)

    def _tpl_outputs(self):
        return self.tpl.get(OUTPUTS) or {}

    def _validate_field(self):
        try:
            version = self._tpl_version()
            self._validate_version(version)
        except KeyError:
            raise MissingRequiredFieldError(what='Template',
                                            required=DEFINITION_VERSION)
        for name in self.tpl:
            if name not in SECTIONS:
                raise UnknownFieldError(what='Template', field=name)

    def _process_intrinsic_functions(self):
        """Process intrinsic functions

        Current implementation processes functions within node template
        properties, requirements, interfaces inputs and template outputs.
        """
        for node_template in self.nodetemplates:
            for prop in node_template.get_properties_objects():
                prop.value = functions.get_function(self,
                                                    node_template,
                                                    prop.value)
            for interface in node_template.interfaces:
                if interface.inputs:
                    for name, value in interface.inputs.items():
                        interface.inputs[name] = functions.get_function(
                            self,
                            node_template,
                            value)
            if node_template.requirements:
                for req in node_template.requirements:
                    if 'properties' in req:
                        for key, value in req['properties'].items():
                            req['properties'][key] = functions.get_function(
                                self,
                                req,
                                value)

        for output in self.outputs:
            func = functions.get_function(self, self.outputs, output.value)
            if isinstance(func, functions.GetAttribute):
                output.attrs[output.VALUE] = func

    def _validate_version(self, version):
        if version not in self.VALID_TEMPLATE_VERSIONS:
            raise InvalidTemplateVersion(
                what=version,
                valid_versions=', '. join(self.VALID_TEMPLATE_VERSIONS))
