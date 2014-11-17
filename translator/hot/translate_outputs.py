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
from translator.toscalib import functions
from translator.toscalib.utils.gettextutils import _

TOSCA_TO_HOT_GET_ATTRS = {'ip_address': 'first_address'}


class TranslateOutputs():
    '''Translate TOSCA Outputs to Heat Outputs.'''

    def __init__(self, outputs):
        self.outputs = outputs

    def translate(self):
        return self._translate_outputs()

    def _translate_outputs(self):
        hot_outputs = []
        for output in self.outputs:
            hot_value = {}
            if isinstance(output.value, functions.GetAttribute):
                func = output.value
                get_parameters = [
                    func.node_template_name,
                    self._translate_attribute_name(func.attribute_name)]
                hot_value['get_attr'] = get_parameters
            elif isinstance(output.value, functions.GetProperty):
                func = output.value
                if func.req_or_cap:
                    raise NotImplementedError(_(
                        'get_property with requirement/capability in outputs '
                        'translation is not supported'))
                get_parameters = [
                    func.node_template_name,
                    self._translate_attribute_name(func.property_name)]
                hot_value['get_attr'] = get_parameters
            else:
                hot_value['get_attr'] = output.value
            hot_outputs.append(HotOutput(output.name,
                                         hot_value,
                                         output.description))
        return hot_outputs

    def _translate_attribute_name(self, attribute_name):
        return TOSCA_TO_HOT_GET_ATTRS.get(attribute_name, attribute_name)
