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

from translator.hot.syntax.hot_output import HotOutput


class TranslateOutputs(object):
    '''Translate TOSCA Outputs to Heat Outputs.'''

    def __init__(self, outputs, node_translator):
        self.outputs = outputs
        self.nodes = node_translator

    def translate(self):
        return self._translate_outputs()

    def _translate_outputs(self):
        hot_outputs = []
        for output in self.outputs:
            if output.value.name == 'get_attribute':
                get_parameters = output.value.args
                hot_target = self.nodes.find_hot_resource(get_parameters[0])
                hot_value = hot_target.get_hot_attribute(get_parameters[1],
                                                         get_parameters)
                hot_outputs.append(HotOutput(output.name,
                                             hot_value,
                                             output.description))
            else:
                hot_outputs.append(HotOutput(output.name,
                                             output.value,
                                             output.description))
        return hot_outputs
