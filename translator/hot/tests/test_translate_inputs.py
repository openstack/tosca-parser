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

from translator.hot.translate_inputs import TranslateInputs
from translator.toscalib.parameters import Input
from translator.toscalib.tests.base import TestCase
import translator.toscalib.utils.yamlparser


class ToscaTemplateInputValidationTest(TestCase):

    def _translate_input_test(self, tpl_snippet, input_params,
                              expectedmessage=None):
        inputs_dict = (translator.toscalib.utils.yamlparser.
                       simple_parse(tpl_snippet)['inputs'])
        inputs = []
        for name, attrs in inputs_dict.items():
            input = Input(name, attrs)
            inputs.append(input)

        translateinput = TranslateInputs(inputs, input_params)
        try:
            translateinput.translate()
        except ValueError:
            pass
        except Exception as err:
            self.assertEqual(expectedmessage, err.__str__())

    def test_invalid_input_type(self):
        tpl_snippet = '''
        inputs:
          cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - valid_values: [ 1, 2, 4, 8 ]
        '''

        input_params = {'cpus': 'string'}
        expectedmessage = ('could not convert string to float: string')
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage)

    def test_invalid_input_constraints_for_equal(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - equal: 1
        '''

        input_params = {'num_cpus': '0'}
        expectedmessage = ('num_cpus: 0 is not equal to "1".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_greater_or_equal(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - greater_or_equal: 1
        '''

        input_params = {'num_cpus': '0'}
        expectedmessage = ('num_cpus: 0 must be greater or equal to "1".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_greater_than(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - greater_than: 1
        '''

        input_params = {'num_cpus': '0'}
        expectedmessage = ('num_cpus: 0 must be greater than "1".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_less_than(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - less_than: 8
        '''

        input_params = {'num_cpus': '8'}
        expectedmessage = ('num_cpus: 8 must be less than "8".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_less_or_equal(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - less_or_equal: 8
        '''

        input_params = {'num_cpus': '9'}
        expectedmessage = ('num_cpus: 9 must be less or equal to "8".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_valid_values(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - valid_values: [ 1, 2, 4, 8 ]
        '''

        input_params = {'num_cpus': '3'}
        expectedmessage = ('num_cpus: 3 is not an valid value "[1, 2, 4, 8]".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_in_range(self):
        tpl_snippet = '''
        inputs:
          num_cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - in_range: [ 1, 8 ]
        '''

        input_params = {'num_cpus': '10'}
        expectedmessage = ('num_cpus: 10 is out of range (min:1, max:8).')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_min_length(self):
        tpl_snippet = '''
        inputs:
          user_name:
            type: string
            description: Name of the user.
            constraints:
              - min_length: 8
        '''

        input_params = {'user_name': 'abcd'}
        expectedmessage = ('length of user_name: abcd must be at least "8".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_max_length(self):
        tpl_snippet = '''
        inputs:
          user_name:
            type: string
            description: Name of the user.
            constraints:
              - max_length: 6
        '''

        input_params = {'user_name': 'abcdefg'}
        expectedmessage = ('length of user_name: '
                           'abcdefg must be no greater than "6".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_invalid_input_constraints_for_pattern(self):
        tpl_snippet = '''
        inputs:
          user_name:
            type: string
            description: Name of the user.
            constraints:
              - pattern: '^\w+$'
        '''

        input_params = {'user_name': '1-abc'}
        expectedmessage = ('user_name: "1-abc" does '
                           'not match pattern "^\\w+$".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)
