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

from toscaparser.common import exception
from toscaparser.properties import Property
from toscaparser.tests.base import TestCase
from toscaparser.utils import yamlparser


class PropertyTest(TestCase):

    def test_type(self):
        test_property_schema = {'type': 'string'}
        propertyInstance = Property('test_property', 'Hughes',
                                    test_property_schema)
        self.assertEqual('string', propertyInstance.type)

    def test_type_invalid(self):
        test_property_schema = {'type': 'Fish'}
        propertyInstance = Property('test_property', 'Hughes',
                                    test_property_schema)
        error = self.assertRaises(exception.InvalidTypeError,
                                  propertyInstance.validate)
        self.assertEqual('Type "Fish" is not a valid type.', str(error))

    def test_list(self):
        test_property_schema = {'type': 'list'}
        propertyInstance = Property('test_property', ['a', 'b'],
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual(['a', 'b'], propertyInstance.value)

    def test_list_invalid(self):
        test_property_schema = {'type': 'list'}
        propertyInstance = Property('test_property', 'a',
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"a" is not a list.', str(error))

    def test_list_entry_schema(self):
        test_property_schema = {'type': 'list',
                                'entry_schema': {'type': 'string'}}
        propertyInstance = Property('test_property', ['a', 'b'],
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual(['a', 'b'], propertyInstance.value)

        schema_snippet = '''
        type: list
        entry_schema:
          type: string
          constraints:
            - min_length: 2
        '''
        test_property_schema = yamlparser.simple_parse(schema_snippet)
        propertyInstance = Property('test_property', ['ab', 'cd'],
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual(['ab', 'cd'], propertyInstance.value)

    def test_list_entry_schema_invalid(self):
        test_property_schema = {'type': 'list',
                                'entry_schema': {'type': 'integer'}}
        propertyInstance = Property('test_property', [1, 'b'],
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"b" is not an integer.', str(error))

    def test_map(self):
        test_property_schema = {'type': 'map'}
        propertyInstance = Property('test_property', {'a': 'b'},
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual({'a': 'b'}, propertyInstance.value)

    def test_map_invalid(self):
        test_property_schema = {'type': 'map'}
        propertyInstance = Property('test_property', 12,
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"12" is not a map.', str(error))

    def test_map_entry_schema(self):
        test_property_schema = {'type': 'map',
                                'entry_schema': {'type': 'boolean'}}
        propertyInstance = Property('test_property',
                                    {'valid': True, 'required': True},
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual({'valid': True, 'required': True},
                         propertyInstance.value)

    def test_map_entry_schema_invalid(self):
        test_property_schema = {'type': 'map',
                                'entry_schema': {'type': 'boolean'}}
        propertyInstance = Property('test_property',
                                    {'valid': True, 'contact_name': 123},
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"123" is not a boolean.', str(error))

    def test_boolean(self):
        test_property_schema = {'type': 'boolean'}
        propertyInstance = Property('test_property', 'true',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        propertyInstance = Property('test_property', True,
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual(True, propertyInstance.value)

    def test_boolean_invalid(self):
        test_property_schema = {'type': 'boolean'}
        propertyInstance = Property('test_property', 12,
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"12" is not a boolean.', str(error))

    def test_float(self):
        test_property_schema = {'type': 'float'}
        propertyInstance = Property('test_property', 0.1,
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual(0.1, propertyInstance.value)

    def test_float_invalid(self):
        test_property_schema = {'type': 'float'}
        propertyInstance = Property('test_property', 12,
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('"12" is not a float.', str(error))

    def test_timestamp(self):
        test_property_schema = {'type': 'timestamp'}
        # canonical timestamp
        propertyInstance = Property('test_property', '2015-04-01T02:59:43.1Z',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual("2015-04-01T02:59:43.1Z", propertyInstance.value)

        # iso8601 timestamp
        propertyInstance = Property('test_property',
                                    '2015-04-01t21:59:43.10-05:00',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual("2015-04-01t21:59:43.10-05:00",
                         propertyInstance.value)

        # space separated timestamp
        propertyInstance = Property('test_property',
                                    '2015-04-01 21:59:43.10 -5',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual("2015-04-01 21:59:43.10 -5", propertyInstance.value)

        # no time zone timestamp
        propertyInstance = Property('test_property', '2015-04-01 21:59:43.10',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual("2015-04-01 21:59:43.10", propertyInstance.value)

        # date (00:00:00Z)
        propertyInstance = Property('test_property', '2015-04-01',
                                    test_property_schema)
        self.assertIsNone(propertyInstance.validate())
        self.assertEqual("2015-04-01", propertyInstance.value)

    def test_timestamp_invalid(self):
        test_property_schema = {'type': 'timestamp'}
        # invalid timestamp - day out of range
        propertyInstance = Property('test_property', '2015-04-115T02:59:43.1Z',
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        self.assertEqual('day is out of range for month', str(error))

    def test_required(self):
        test_property_schema = {'type': 'string'}
        propertyInstance = Property('test_property', 'Foo',
                                    test_property_schema)
        self.assertEqual(True, propertyInstance.required)

    def test_proprety_inheritance(self):
        from toscaparser.nodetemplate import NodeTemplate

        tosca_custom_def = '''
          tosca.nodes.SoftwareComponent.MySoftware:
            derived_from: SoftwareComponent
            properties:
              install_path:
                required: false
                type: string
                default: /opt/mysoftware
        '''

        tosca_node_template = '''
          node_templates:
            mysoftware_instance:
              type: tosca.nodes.SoftwareComponent.MySoftware
              properties:
                component_version: 3.1
        '''

        expected_properties = ['component_version',
                               'install_path']

        nodetemplates = yamlparser.\
            simple_parse(tosca_node_template)['node_templates']
        custom_def = yamlparser.simple_parse(tosca_custom_def)
        name = list(nodetemplates.keys())[0]
        tpl = NodeTemplate(name, nodetemplates, custom_def)
        self.assertIsNone(tpl.validate())
        self.assertEqual(expected_properties,
                         sorted(tpl.get_properties().keys()))
