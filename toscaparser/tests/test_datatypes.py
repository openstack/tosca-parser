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

import os

from testtools.testcase import skip
from toscaparser.common import exception
from toscaparser.dataentity import DataEntity
from toscaparser.elements.datatype import DataType
from toscaparser.parameters import Input
from toscaparser.tests.base import TestCase
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils import yamlparser


class DataTypeTest(TestCase):

    custom_type_schema = '''
    tosca.my.datatypes.PeopleBase:
      properties:
        name:
          type: string
          required: true
          constraints:
            - min_length: 2
        gender:
          type: string
          default: unknown

    tosca.my.datatypes.People:
      derived_from: tosca.my.datatypes.PeopleBase
      properties:
        addresses:
          type: map
          entry_schema:
            type: string
        contacts:
          type: list
          entry_schema:
            type: tosca.my.datatypes.ContactInfo

    tosca.my.datatypes.ContactInfo:
      description: simple contact information
      properties:
        contact_name:
          type: string
          required: true
          constraints:
            - min_length: 2
        contact_email:
          type: string
        contact_phone:
          type: string
    '''
    custom_type_def = yamlparser.simple_parse(custom_type_schema)

    def test_empty_template(self):
        value_snippet = ''
        value = yamlparser.simple_parse(value_snippet)
        self.assertEqual(value, {})

    def test_built_in_datatype(self):
        value_snippet = '''
        private_network:
          network_name: private
          network_id: 3e54214f-5c09-1bc9-9999-44100326da1b
          addresses: [ 10.111.128.10 ]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.datatypes.network.NetworkInfo',
                          value.get('private_network'))
        self.assertIsNotNone(data.validate())

    def test_built_in_datatype_with_short_name(self):
        value_snippet = '''
        ethernet_port:
          port_name: port1
          port_id: 2c0c7a37-691a-23a6-7709-2d10ad041467
          network_id: 3e54214f-5c09-1bc9-9999-44100326da1b
          mac_address: f1:18:3b:41:92:1e
          addresses: [ 172.24.9.102 ]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('PortInfo', value.get('ethernet_port'))
        self.assertIsNotNone(data.validate())

    def test_built_in_datatype_without_properties(self):
        value_snippet = '''
        2
        '''
        value = yamlparser.simple_parse(value_snippet)
        datatype = DataType('PortDef')
        self.assertEqual('integer', datatype.value_type)
        data = DataEntity('PortDef', value)
        self.assertIsNotNone(data.validate())

    @skip('The example in TOSCA spec may have some problem.')
    def test_built_in_nested_datatype(self):
        value_snippet = '''
        user_port:
          protocol: tcp
          target: [50000]
          source: [9000]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('PortSpec', value.get('user_port'))
        self.assertIsNotNone(data.validate())

    def test_built_in_nested_datatype_portdef(self):
        tpl_snippet = '''
        inputs:
          db_port:
            type: PortDef
            description: Port for the MySQL database
        '''
        inputs = yamlparser.simple_parse(tpl_snippet)['inputs']
        name, attrs = list(inputs.items())[0]
        input = Input(name, attrs)
        self.assertIsNone(input.validate(3360))
        try:
            input.validate(336000)
        except Exception as err:
            self.assertTrue(isinstance(err, exception.ValidationError))
            self.assertEqual('None: 336000 is out of range (min:1, '
                             'max:65535).', err.__str__())

    def test_custom_datatype(self):
        value_snippet = '''
        name: Mike
        gender: male
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        self.assertIsNotNone(data.validate())

    def test_custom_datatype_with_parent(self):
        value_snippet = '''
        name: Mike
        gender: male
        contacts:
          - {contact_name: Tom,
            contact_email: tom@email.com,
            contact_phone: '123456789'}
          - {contact_name: Jerry,
            contact_email: jerry@email.com,
            contact_phone: '321654987'}
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.People', value,
                          DataTypeTest.custom_type_def)
        self.assertIsNotNone(data.validate())

    # [Tom, Jerry] is not a dict, it can't be a value of datatype PeopleBase
    def test_non_dict_value_for_datatype(self):
        value_snippet = '''
        [Tom, Jerry]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(exception.TypeMismatchError, data.validate)
        self.assertEqual('[\'Tom\', \'Jerry\'] must be of type: '
                         '"tosca.my.datatypes.PeopleBase".', error.__str__())

    # 'nema' is an invalid field name
    def test_field_error_in_dataentity(self):
        value_snippet = '''
        nema: Mike
        gender: male
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(exception.UnknownFieldError, data.validate)
        self.assertEqual('Data value of type tosca.my.datatypes.PeopleBase '
                         'contain(s) unknown field: "nema", refer to the '
                         'definition to verify valid values.',
                         error.__str__())

    def test_default_field_in_dataentity(self):
        value_snippet = '''
        name: Mike
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        data = data.validate()
        self.assertEqual('unknown', data.get('gender'))

    # required field 'name' is missing
    def test_missing_field_in_dataentity(self):
        value_snippet = '''
        gender: male
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(exception.MissingRequiredFieldError,
                                  data.validate)
        self.assertEqual('Data value of type tosca.my.datatypes.PeopleBase '
                         'is missing required field: "[\'name\']".',
                         error.__str__())

    # the value of name field is not a string
    def test_type_error_in_dataentity(self):
        value_snippet = '''
        name: 123
        gender: male
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(ValueError, data.validate)
        self.assertEqual('"123" is not a string.', error.__str__())

    # the value of name doesn't meet the defined constraint
    def test_value_error_in_dataentity(self):
        value_snippet = '''
        name: M
        gender: male
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.PeopleBase', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(exception.ValidationError, data.validate)
        self.assertEqual('length of name: M must be at least "2".',
                         error.__str__())

    # value of addresses doesn't fit the entry_schema
    def test_validation_in_collection_entry(self):
        value_snippet = '''
        name: Mike
        gender: male
        addresses: {Home: 1, Office: 9 bar avenue}
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.People', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(ValueError, data.validate)
        self.assertEqual('"1" is not a string.', error.__str__())

    # contact_pone is an invalid field name in nested datatype
    def test_validation_in_nested_datatype(self):
        value_snippet = '''
        name: Mike
        gender: male
        contacts:
          - {contact_name: Tom,
            contact_email: tom@email.com,
            contact_pone: '123456789'}
          - {contact_name: Jerry,
            contact_email: jerry@email.com,
            contact_phone: '321654987'}
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.People', value,
                          DataTypeTest.custom_type_def)
        error = self.assertRaises(exception.UnknownFieldError, data.validate)
        self.assertEqual('Data value of type tosca.my.datatypes.ContactInfo '
                         'contain(s) unknown field: "contact_pone", refer to '
                         'the definition to verify valid values.',
                         error.__str__())

    def test_datatype_in_current_template(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/datatypes/test_custom_datatypes_in_current_template.yaml")
        self.assertIsNotNone(ToscaTemplate(tpl_path))

    def test_datatype_in_template_positive(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/datatypes/test_custom_datatypes_positive.yaml")
        self.assertIsNotNone(ToscaTemplate(tpl_path))

    def test_datatype_in_template_invalid_value(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/datatypes/test_custom_datatypes_value_error.yaml")
        error = self.assertRaises(ValueError, ToscaTemplate, tpl_path)
        self.assertEqual('"[\'1 foo street\', \'9 bar avenue\']" '
                         'is not a map.', error.__str__())

    def test_datatype_in_template_nested_datatype_error(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/datatypes/test_custom_datatypes_nested_datatype_error.yaml")
        error = self.assertRaises(ValueError, ToscaTemplate, tpl_path)
        self.assertEqual('"123456789" is not a string.', error.__str__())
