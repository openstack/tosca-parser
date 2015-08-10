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


from collections import OrderedDict
from translator.common.utils import CompareUtils
from translator.hot.translate_inputs import TranslateInputs
from translator.toscalib.parameters import Input
from translator.toscalib.tests.base import TestCase
from translator.toscalib.utils.gettextutils import _
import translator.toscalib.utils.yamlparser


class ToscaTemplateInputValidationTest(TestCase):

    def _translate_input_test(self, tpl_snippet, input_params,
                              expectedmessage=None,
                              expected_hot_params=None):
        inputs_dict = (translator.toscalib.utils.yamlparser.
                       simple_parse(tpl_snippet)['inputs'])
        inputs = []
        for name, attrs in inputs_dict.items():
            input = Input(name, attrs)
            inputs.append(input)

        translateinput = TranslateInputs(inputs, input_params)
        try:
            resulted_hot_params = translateinput.translate()
            if expected_hot_params:
                self._compare_hot_params(resulted_hot_params,
                                         expected_hot_params)
        except Exception as err:
            self.assertEqual(expectedmessage, err.__str__())

    def _compare_hot_params(self, resulted_hot_params,
                            expected_hot_params):
        for expected_param in expected_hot_params:
            for resulted_param_obj in resulted_hot_params:
                resulted_param = resulted_param_obj.get_dict_output()
                result = CompareUtils.compare_dicts(expected_param,
                                                    resulted_param)
                if not result:
                    raise Exception(_("hot input and resulted input "
                                    "params are not equal."))

    def test_invalid_input_type(self):
        tpl_snippet = '''
        inputs:
          cpus:
            type: integer
            description: Number of CPUs for the server.
            constraints:
              - valid_values: [ 1, 2, 4, 8 ]
        '''

        input_params = {'cpus': '0.3'}
        expectedmessage = _("invalid literal for int() with base 10: '0.3'")
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
        expectedmessage = _('num_cpus: 0 is not equal to "1".')
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
        expectedmessage = _('num_cpus: 0 must be greater or equal to "1".')
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
        expectedmessage = _('num_cpus: 0 must be greater than "1".')
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
        expectedmessage = _('num_cpus: 8 must be less than "8".')
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
        expectedmessage = _('num_cpus: 9 must be less or equal to "8".')
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
        expectedmessage = _('num_cpus: 3 is not an valid value'
                            ' "[1, 2, 4, 8]".')
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
        expectedmessage = _('num_cpus: 10 is out of range (min:1, max:8).')
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
        expectedmessage = _('length of user_name: abcd must be at least "8".')
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
        expectedmessage = _('length of user_name: '
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
        expectedmessage = _('user_name: "1-abc" does '
                            'not match pattern "^\\w+$".')
        self._translate_input_test(tpl_snippet, input_params, expectedmessage)

    def test_valid_input_storage_size(self):
        tpl_snippet = '''
        inputs:
          storage_size:
            type: scalar-unit.size
            description: size of the storage volume.
        '''

        expectedmessage = _('both equal.')
        input_params = {'storage_size': '2 GB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 2)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

        """ TOSCA 2000 MB => 2 GB HOT conversion"""
        input_params = {'storage_size': '2000 MB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 2)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

        """ TOSCA 2048 MB => 2 GB HOT conversion"""
        input_params = {'storage_size': '2048 MB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 2)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

        """ TOSCA 2 MB => 1 GB HOT conversion"""
        input_params = {'storage_size': '2 MB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 1)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

        """ TOSCA 1024 MB => 1 GB HOT conversion"""
        input_params = {'storage_size': '1024 MB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 1)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

        """ TOSCA 1024 MiB => 1 GB HOT conversion"""
        input_params = {'storage_size': '1024 MiB'}
        expected_hot_params = [{'storage_size':
                                OrderedDict([('type', 'number'),
                                             ('description',
                                              'size of the storage volume.'),
                                             ('default', 1)])}]
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage, expected_hot_params)

    def test_invalid_input_storage_size(self):
        tpl_snippet = '''
        inputs:
          storage_size:
            type: scalar-unit.size
            description: size of the storage volume.
        '''

        input_params = {'storage_size': '0 MB'}
        expectedmsg = _("Unit value should be > 0.")
        self._translate_input_test(tpl_snippet, input_params, expectedmsg)

        input_params = {'storage_size': '-2 MB'}
        expectedmsg = _('"-2 MB" is not a valid scalar-unit')
        self._translate_input_test(tpl_snippet, input_params, expectedmsg)

    def test_invalid_input_type_version(self):
        tpl_snippet = '''
        inputs:
          version:
            type: version
        '''

        input_params = {'version': '0.a'}
        expectedmessage = _('Value of TOSCA version property '
                            '"0.a" is invalid.')
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage)

        input_params = {'version': '0.0.0.abc'}
        expectedmessage = _('Value of TOSCA version property '
                            '"0.0.0.abc" is invalid.')
        self._translate_input_test(tpl_snippet, input_params,
                                   expectedmessage)

    def test_valid_input_type_version(self):
        tpl_snippet = '''
        inputs:
          version:
            type: version
            default: 12
        '''

        expectedmessage = _('both equal.')
        input_params = {'version': '18'}
        expected_hot_params = [{'version':
                                OrderedDict([('type', 'string'),
                                             ('default', '18.0')])}]
        self._translate_input_test(tpl_snippet, input_params, expectedmessage,
                                   expected_hot_params)

        input_params = {'version': '18.0'}
        expected_hot_params = [{'version':
                                OrderedDict([('type', 'string'),
                                             ('default', '18.0')])}]
        self._translate_input_test(tpl_snippet, input_params, expectedmessage,
                                   expected_hot_params)

        input_params = {'version': '18.0.1'}
        expected_hot_params = [{'version':
                                OrderedDict([('type', 'string'),
                                             ('default', '18.0.1')])}]
        self._translate_input_test(tpl_snippet, input_params, expectedmessage,
                                   expected_hot_params)
