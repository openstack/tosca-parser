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
from toscaparser.utils.gettextutils import _
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
          required: false
          entry_schema:
            type: string
        contacts:
          type: list
          required: false
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

    tosca.my.datatypes.TestLab:
      properties:
        humidity:
          type: range
          required: false
          constraints:
            - in_range: [-256, INFINITY]
        temperature1:
          type: range
          required: false
          constraints:
            - in_range: [-256, UNBOUNDED]
        temperature2:
          type: range
          required: false
          constraints:
            - in_range: [UNBOUNDED, 256]
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

        value_snippet = '''
        portspec_valid:
          protocol: tcp
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.datatypes.network.PortSpec',
                          value.get('portspec_valid'))
        self.assertIsNotNone(data.validate())

        value_snippet = '''
        portspec_invalid:
          protocol: xyz
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.datatypes.network.PortSpec',
                          value.get('portspec_invalid'))
        err = self.assertRaises(exception.ValidationError, data.validate)
        self.assertEqual(_('The value "xyz" of property "protocol" is not '
                           'valid. Expected a value from "[udp, tcp, igmp]".'
                           ),
                         err.__str__())

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

    # Test normative PortSpec datatype's additional requirements
    # TODO(Matt) - opened as bug 1555300
    # Need a test for PortSpec normative data type
    # that tests the spec. requirement: "A valid PortSpec
    # must have at least one of the following properties:
    # target, target_range, source or source_range."
    # TODO(Matt) - opened as bug 1555310
    # test PortSpec value for source and target
    # against the source_range and target_range
    # when specified.
    def test_port_spec_addl_reqs(self):
        value_snippet = '''
        test_port:
          protocol: tcp
          target: 65535
          target_range: [ 1, 65535 ]
          source: 1
          source_range: [ 1, 65535 ]

        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.datatypes.network.PortSpec',
                          value.get('test_port'))
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
        err = self.assertRaises(exception.ValidationError, input.validate,
                                336000)
        self.assertEqual(_('The value "336000" of property "None" is out of '
                           'range "(min:1, max:65535)".'),
                         err.__str__())

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
        self.assertEqual(_('[\'Tom\', \'Jerry\'] must be of type '
                           '"tosca.my.datatypes.PeopleBase".'),
                         error.__str__())

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
        self.assertEqual(_('Data value of type '
                           '"tosca.my.datatypes.PeopleBase" contains unknown '
                           'field "nema". Refer to the definition to verify '
                           'valid values.'),
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
        self.assertEqual(_('Data value of type '
                           '"tosca.my.datatypes.PeopleBase" is missing '
                           'required field "[\'name\']".'),
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
        self.assertEqual(_('"123" is not a string.'), error.__str__())

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
        self.assertEqual(_('Length of value "M" of property "name" must be '
                           'at least "2".'), error.__str__())

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
        self.assertEqual(_('"1" is not a string.'), error.__str__())

    # 'contact_pone' is an invalid attribute name in nested datatype below
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
        self.assertEqual(_('Data value of type '
                           '"tosca.my.datatypes.ContactInfo" contains unknown '
                           'field "contact_pone". Refer to the definition to '
                           'verify valid values.'),
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
        self.assertRaises(exception.ValidationError, ToscaTemplate, tpl_path)
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('"[\'1 foo street\', \'9 bar avenue\']" is not a map.'))

    def test_datatype_in_template_nested_datatype_error(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/datatypes/test_custom_datatypes_nested_datatype_error.yaml")
        self.assertRaises(exception.ValidationError, ToscaTemplate, tpl_path)
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError, _('"123456789" is not a string.'))

    def test_valid_range_type(self):
        value_snippet = '''
        user_port:
          protocol: tcp
          target_range:  [20000, 60000]
          source_range:  [1000, 3000]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('PortSpec', value.get('user_port'))
        self.assertIsNotNone(data.validate())

    def test_invalid_range_datatype(self):
        value_snippet = '''
        user_port:
          protocol: tcp
          target: 1
          target_range: [20000]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('PortSpec', value.get('user_port'))
        err = self.assertRaises(ValueError, data.validate)
        self.assertEqual(_('"[20000]" is not a valid range.'
                           ),
                         err.__str__())

        value_snippet = '''
        user_port:
          protocol: tcp
          target: 1
          target_range: [20000, 3000]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('PortSpec', value.get('user_port'))
        err = self.assertRaises(ValueError, data.validate)
        self.assertEqual(_('"[20000, 3000]" is not a valid range.'
                           ),
                         err.__str__())

        value_snippet = '''
        humidity: [-100, 100]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab',
                          value, DataTypeTest.custom_type_def)
        err = self.assertRaises(exception.InvalidSchemaError,
                                lambda: data.validate())
        self.assertEqual(_('The property "in_range" expects comparable values.'
                           ),
                         err.__str__())

    def test_range_unbounded(self):
        value_snippet = '''
        humidity: [-100, 100]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab',
                          value, DataTypeTest.custom_type_def)
        err = self.assertRaises(exception.InvalidSchemaError,
                                lambda: data.validate())
        self.assertEqual(_('The property "in_range" expects comparable values.'
                           ),
                         err.__str__())

    def test_invalid_ranges_against_constraints(self):
        # The TestLab range type has min=-256, max=UNBOUNDED
        value_snippet = '''
        temperature1: [-257, 999999]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab', value,
                          DataTypeTest.custom_type_def)
        err = self.assertRaises(exception.ValidationError, data.validate)
        self.assertEqual(_('The value "-257" of property "temperature1" is '
                           'out of range "(min:-256, max:UNBOUNDED)".'),
                         err.__str__())

        value_snippet = '''
        temperature2: [-999999, 257]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab', value,
                          DataTypeTest.custom_type_def)
        err = self.assertRaises(exception.ValidationError, data.validate)
        self.assertEqual(_('The value "257" of property "temperature2" is '
                           'out of range "(min:UNBOUNDED, max:256)".'),
                         err.__str__())

    def test_valid_ranges_against_constraints(self):

        # The TestLab range type has max=UNBOUNDED
        value_snippet = '''
        temperature1: [-255, 999999]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab', value,
                          DataTypeTest.custom_type_def)
        self.assertIsNotNone(data.validate())

        # The TestLab range type has min=UNBOUNDED
        value_snippet = '''
        temperature2: [-999999, 255]
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.my.datatypes.TestLab', value,
                          DataTypeTest.custom_type_def)
        self.assertIsNotNone(data.validate())

    def test_incorrect_field_in_datatype(self):
        tpl_snippet = '''
        tosca_definitions_version: tosca_simple_yaml_1_0
        topology_template:
          node_templates:
            server:
              type: tosca.nodes.Compute

            webserver:
              type: tosca.nodes.WebServer
              properties:
                admin_credential:
                  user: username
                  token: some_pass
                  some_field: value
              requirements:
                - host: server
        '''
        tpl = yamlparser.simple_parse(tpl_snippet)
        err = self.assertRaises(exception.ValidationError, ToscaTemplate,
                                None, None, None, tpl)
        self.assertIn(_('The pre-parsed input failed validation with the '
                        'following error(s): \n\n\tUnknownFieldError: Data '
                        'value of type "tosca.datatypes.Credential" contains'
                        ' unknown field "some_field". Refer to the definition'
                        ' to verify valid values'), err.__str__())

    def test_functions_datatype(self):
        value_snippet = '''
        admin_credential:
          user: username
          token: { get_input: password }
        '''
        value = yamlparser.simple_parse(value_snippet)
        data = DataEntity('tosca.datatypes.Credential',
                          value.get('admin_credential'))
        self.assertIsNotNone(data.validate())
