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
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.parameters import Input, Output
from translator.toscalib.tpl_relationship_graph import ToscaGraph
from translator.toscalib.utils.gettextutils import _
import translator.toscalib.utils.yamlparser


SECTIONS = (VERSION, DESCRIPTION, INPUTS,
            NODE_TEMPLATES, OUTPUTS) = \
           ('tosca_definitions_version', 'description', 'inputs',
            'node_templates', 'outputs')

log = logging.getLogger("tosca.model")


class ToscaTemplate(object):
    '''Load the template data.'''
    def __init__(self, path):
        self.tpl = translator.toscalib.utils.yamlparser.load_yaml(path)
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
            if not isinstance(input.schema, dict):
                raise ValueError(_("The input %(input)s has no attributes.")
                                 % {'input': input})
            input.validate()
            inputs.append(input)
        return inputs

    def _nodetemplates(self):
        nodetemplates = []
        tpls = self._tpl_nodetemplates()
        for name, value in tpls.items():
            tpl = NodeTemplate(name, tpls)
            tpl.validate()
            nodetemplates.append(tpl)
        return nodetemplates

    def _outputs(self):
        outputs = []
        for name, attrs in self._tpl_outputs().items():
            outputs.append(Output(name, attrs))
        return outputs

    def _tpl_version(self):
        return self.tpl[VERSION]

    def _tpl_description(self):
        return self.tpl[DESCRIPTION].rstrip()

    def _tpl_inputs(self):
        return self.tpl[INPUTS]

    def _tpl_nodetemplates(self):
        return self.tpl[NODE_TEMPLATES]

    def _tpl_outputs(self):
        return self.tpl[OUTPUTS]
