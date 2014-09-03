# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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

from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.parameters import Input, Output
from translator.toscalib.tpl_relationship_graph import ToscaGraph

import translator.toscalib.utils.yamlparser


#TOSCA template key names
SECTIONS = (DEFINITION_VERSION, DEFAULT_NAMESPACE, TEMPLATE_NAME,
            TEMPLATE_AUTHOR, TEMPLATE_VERSION, DESCRIPTION, IMPORTS,
            DSL_DEFINITIONS, INPUTS, NODE_TEMPLATES, RELATIONSHIP_TEMPLATES,
            NODE_TYPES, RELATIONSHIP_TYPES, CAPABILITY_TYPES, ARTIFACT_TYPES,
            OUTPUTS, GROUPS) = \
           ('tosca_definitions_version', 'tosca_default_namespace',
            'template_name', 'template_author', 'template_version',
            'description', 'imports', 'dsl_definitions', 'inputs',
            'node_templates', 'relationship_templates', 'node_types',
            'relationship_types', 'capability_types', 'artifact_types',
            'outputs', 'groups')

log = logging.getLogger("tosca.model")

YAML_LOADER = translator.toscalib.utils.yamlparser.load_yaml


class ToscaTemplate(object):
    '''Load the template data.'''
    def __init__(self, path):
        self.tpl = YAML_LOADER(path)
        self.path = path
        self._validate_field()
        self.version = self._tpl_version()
        self.description = self._tpl_description()
        self.inputs = self._inputs()
        self.nodetemplates = self._nodetemplates()
        self.outputs = self._outputs()
        self.graph = ToscaGraph(self.nodetemplates)

    def _inputs(self):
        inputs = []
        for name, attrs in self._tpl_inputs().items():
            input = Input(name, attrs)
            input.validate()
            inputs.append(input)
        return inputs

    def _nodetemplates(self):
        custom_types = {}
        imports = self._tpl_imports()
        if imports:
            for definition in imports:
                if os.path.isabs(definition):
                    def_file = definition
                else:
                    tpl_dir = os.path.dirname(os.path.abspath(self.path))
                    def_file = os.path.join(tpl_dir, definition)
                custom_type = YAML_LOADER(def_file)
                node_types = custom_type['node_types']
                for name in node_types:
                    defintion = node_types[name]
                    custom_types[name] = defintion
        nodetemplates = []
        tpls = self._tpl_nodetemplates()
        for name in tpls:
            tpl = NodeTemplate(name, tpls, custom_types)
            tpl.validate()
            nodetemplates.append(tpl)
        return nodetemplates

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
        return self.tpl[INPUTS]

    def _tpl_nodetemplates(self):
        return self.tpl[NODE_TEMPLATES]

    def _tpl_outputs(self):
        return self.tpl[OUTPUTS]

    def _validate_field(self):
        try:
            self._tpl_version()
        except KeyError:
            raise MissingRequiredFieldError(what='Template',
                                            required=DEFINITION_VERSION)
        for name in self.tpl:
            if name not in SECTIONS:
                raise UnknownFieldError(what='Template', field=name)
