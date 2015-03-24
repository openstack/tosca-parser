#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from translator.hot.syntax.hot_template import HotTemplate
from translator.hot.translate_inputs import TranslateInputs
from translator.hot.translate_node_templates import TranslateNodeTemplates
from translator.hot.translate_outputs import TranslateOutputs


class TOSCATranslator(object):
    '''Invokes translation methods.'''

    def __init__(self, tosca, parsed_params):
        super(TOSCATranslator, self).__init__()
        self.tosca = tosca
        self.hot_template = HotTemplate()
        self.parsed_params = parsed_params
        self.node_translator = None

    def translate(self):
        self._resolve_input()
        self.hot_template.description = self.tosca.description
        self.hot_template.parameters = self._translate_inputs()
        self.node_translator = TranslateNodeTemplates(self.tosca,
                                                      self.hot_template)
        self.hot_template.resources = self.node_translator.translate()
        self.hot_template.outputs = self._translate_outputs()
        return self.hot_template.output_to_yaml()

    def _translate_inputs(self):
        translator = TranslateInputs(self.tosca.inputs, self.parsed_params)
        return translator.translate()

    def _translate_outputs(self):
        translator = TranslateOutputs(self.tosca.outputs, self.node_translator)
        return translator.translate()

    # check all properties for all node and ensure they are resolved
    # to actual value
    def _resolve_input(self):
        for n in self.tosca.nodetemplates:
            for node_prop in n.get_properties_objects():
                if isinstance(node_prop.value, dict):
                    try:
                        self.parsed_params[node_prop.value['get_input']]
                    except Exception:
                        raise ValueError('Must specify all input values in \
                                        TOSCA template, missing %s' %
                                         node_prop.value['get_input'])
