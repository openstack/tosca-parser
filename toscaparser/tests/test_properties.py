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

from testtools import matchers

from toscaparser.common import exception
from toscaparser.elements.property_definition import PropertyDef
from toscaparser.nodetemplate import NodeTemplate
from toscaparser.properties import Property
from toscaparser.tests.base import TestCase
from toscaparser.utils.gettextutils import _
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
        self.assertEqual(_('Type "Fish" is not a valid type.'), str(error))

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
        self.assertEqual(_('"a" is not a list.'), str(error))

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
        self.assertEqual(_('"b" is not an integer.'), str(error))

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
        self.assertEqual(_('"12" is not a map.'), str(error))

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
        self.assertEqual(_('"123" is not a boolean.'), str(error))

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
        self.assertEqual(_('"12" is not a boolean.'), str(error))

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
        self.assertEqual(_('"12" is not a float.'), str(error))

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
        value = '2015-04-115T02:59:43.1Z'
        propertyInstance = Property('test_property', value,
                                    test_property_schema)
        error = self.assertRaises(ValueError, propertyInstance.validate)
        expected_message = (_('"%s" is not a valid timestamp.') % value)
        self.assertThat(str(error), matchers.StartsWith(expected_message))

    def test_required(self):
        test_property_schema = {'type': 'string'}
        propertyInstance = Property('test_property', 'Foo',
                                    test_property_schema)
        self.assertEqual(True, propertyInstance.required)

    def test_proprety_inheritance(self):

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

        tpl = self._get_nodetemplate(tosca_node_template, tosca_custom_def)
        self.assertIsNone(tpl.validate())
        self.assertEqual(expected_properties,
                         sorted(tpl.get_properties().keys()))

    def test_missing_property_type(self):
        tpl_snippet = '''
         properties:
           prop:
             typo: tosca.mytesttype.Test
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        error = self.assertRaises(exception.InvalidSchemaError, PropertyDef,
                                  'prop', None, schema['properties']['prop'])
        self.assertEqual(_('Schema definition of "prop" must have a "type" '
                           'attribute.'), str(error))

    def test_invalid_required_value(self):
        tpl_snippet = '''
         properties:
           prop:
             type: tosca.mytesttype.Test
             required: dunno
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        error = self.assertRaises(exception.InvalidSchemaError, PropertyDef,
                                  'prop', None, schema['properties']['prop'])

        valid_values = ', '.join(PropertyDef.VALID_REQUIRED_VALUES)
        expected_message = (_('Schema definition of "prop" has "required" '
                              'attribute with invalid value "dunno". The '
                              'value must be one of "%s".') % valid_values)
        self.assertEqual(expected_message, str(error))

    def test_invalid_property_status(self):
        tpl_snippet = '''
         properties:
           prop:
             type: string
             status: unknown
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        error = self.assertRaises(exception.InvalidSchemaError, PropertyDef,
                                  'prop', None, schema['properties']['prop'])

        valid_values = ', '.join(PropertyDef.VALID_STATUS_VALUES)
        expected_message = (_('Schema definition of "prop" has "status" '
                              'attribute with invalid value "unknown". The '
                              'value must be one of "%s".') % valid_values)
        self.assertEqual(expected_message, str(error))

    def test_capability_proprety_inheritance(self):
        tosca_custom_def_example1 = '''
          tosca.capabilities.ScalableNew:
            derived_from: tosca.capabilities.Scalable
            properties:
              max_instances:
                type: integer
                default: 0
                required: no

          tosca.nodes.ComputeNew:
            derived_from: tosca.nodes.Compute
            capabilities:
              scalable:
                type: tosca.capabilities.ScalableNew
        '''

        tosca_node_template_example1 = '''
          node_templates:
            compute_instance:
              type: tosca.nodes.ComputeNew
              capabilities:
                scalable:
                  properties:
                    min_instances: 1
        '''

        tosca_custom_def_example2 = '''
          tosca.nodes.ComputeNew:
            derived_from: tosca.nodes.Compute
            capabilities:
              new_cap:
                type: tosca.capabilities.Scalable
        '''

        tosca_node_template_example2 = '''
          node_templates:
            db_server:
                type: tosca.nodes.ComputeNew
                capabilities:
                  host:
                   properties:
                     num_cpus: 1
        '''

        tpl1 = self._get_nodetemplate(tosca_node_template_example1,
                                      tosca_custom_def_example1)
        self.assertIsNone(tpl1.validate())

        tpl2 = self._get_nodetemplate(tosca_node_template_example2,
                                      tosca_custom_def_example2)
        self.assertIsNone(tpl2.validate())

    def _get_nodetemplate(self, tpl_snippet,
                          custom_def_snippet=None):
        nodetemplates = yamlparser.\
            simple_parse(tpl_snippet)['node_templates']
        custom_def = []
        if custom_def_snippet:
            custom_def = yamlparser.simple_parse(custom_def_snippet)
        name = list(nodetemplates.keys())[0]
        tpl = NodeTemplate(name, nodetemplates, custom_def)
        return tpl

    def test_explicit_relationship_proprety(self):

        tosca_node_template = '''
          node_templates:

            client_node:
              type: tosca.nodes.Compute
              requirements:
                - local_storage:
                    node: my_storage
                    relationship:
                      type: AttachesTo
                      properties:
                        location: /mnt/disk

            my_storage:
              type: tosca.nodes.BlockStorage
              properties:
                size: 1 GB
        '''

        expected_properties = ['location']

        nodetemplates = yamlparser.\
            simple_parse(tosca_node_template)['node_templates']
        tpl = NodeTemplate('client_node', nodetemplates, [])

        self.assertIsNone(tpl.validate())
        rel_tpls = []
        for relationship, trgt in tpl.relationships.items():
            rel_tpls.extend(trgt.get_relationship_template())
        self.assertEqual(expected_properties,
                         sorted(rel_tpls[0].get_properties().keys()))
