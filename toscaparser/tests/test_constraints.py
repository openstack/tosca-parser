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

import datetime
import yaml

from toscaparser.common import exception
from toscaparser.elements.constraints import Constraint
from toscaparser.elements.constraints import Schema
from toscaparser.tests.base import TestCase
from toscaparser.utils.gettextutils import _
from toscaparser.utils import yamlparser


class ConstraintTest(TestCase):

    def test_schema_dict(self):
        tpl_snippet = '''
        cpus:
          type: integer
          description: Number of CPUs for the server.
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        cpus_schema = Schema('cpus', schema['cpus'])
        self.assertEqual(len(cpus_schema), 2)
        self.assertEqual('integer', cpus_schema.type)
        self.assertEqual('Number of CPUs for the server.',
                         cpus_schema.description)
        self.assertEqual(True, cpus_schema.required)
        self.assertIsNone(cpus_schema.default)

    def test_schema_not_dict(self):
        tpl_snippet = '''
        cpus:
          - type: integer
          - description: Number of CPUs for the server.
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Schema,
                                  'cpus', schema['cpus'])
        self.assertEqual(_('Schema definition of "cpus" must be a dict.'),
                         str(error))

    def test_schema_miss_type(self):
        tpl_snippet = '''
        cpus:
          description: Number of CPUs for the server.
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Schema,
                                  'cpus', schema['cpus'])
        self.assertEqual(_('Schema definition of "cpus" must have a "type" '
                           'attribute.'), str(error))

    def test_schema_none_description(self):
        tpl_snippet = '''
        cpus:
          type: integer
        '''
        schema = yamlparser.simple_parse(tpl_snippet)
        cpus_schema = Schema('cpus', schema['cpus'])
        self.assertEqual('', cpus_schema.description)

    def test_invalid_constraint_type(self):
        schema = {'invalid_type': 2}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('Invalid property "invalid_type".'),
                         str(error))

    def test_invalid_prop_type(self):
        schema = {'length': 5}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('Property "length" is not valid for data type '
                           '"integer".'), str(error))

    def test_invalid_validvalues(self):
        schema = {'valid_values': 2}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "valid_values" expects a list.'),
                         str(error))

    def test_validvalues_validate(self):
        schema = {'valid_values': [2, 4, 6, 8]}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertIsNone(constraint.validate(4))

    def test_validvalues_validate_fail(self):
        schema = {'valid_values': [2, 4, 6, 8]}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 5)
        self.assertEqual(_('The value "5" of property "prop" is not valid. '
                           'Expected a value from "[2, 4, 6, 8]".'),
                         str(error))

    def test_invalid_in_range(self):
        snippet = 'in_range: {2, 6}'
        schema = yaml.load(snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "in_range" expects a list.'),
                         str(error))

    def test_in_range_min_max(self):
        schema = {'in_range': [2, 6]}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertEqual(2, constraint.min)
        self.assertEqual(6, constraint.max)

    def test_in_range_validate(self):
        schema = {'in_range': [2, 6]}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertIsNone(constraint.validate(2))
        self.assertIsNone(constraint.validate(4))
        self.assertIsNone(constraint.validate(6))

    def test_in_range_validate_fail(self):
        schema = {'in_range': [2, 6]}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 8)
        self.assertEqual(_('The value "8" of property "prop" is out of range '
                           '"(min:2, max:6)".'), str(error))

    def test_equal_validate(self):
        schema = {'equal': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertIsNone(constraint.validate(4))

    def test_equal_validate_fail(self):
        schema = {'equal': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 8)
        self.assertEqual('The value "8" of property "prop" is not equal to '
                         '"4".', str(error))

    def test_greater_than_validate(self):
        schema = {'greater_than': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertIsNone(constraint.validate(6))

    def test_greater_than_validate_fail(self):
        schema = {'greater_than': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 3)
        self.assertEqual(_('The value "3" of property "prop" must be greater '
                           'than "4".'), str(error))

        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 4)
        self.assertEqual(_('The value "4" of property "prop" must be greater '
                           'than "4".'), str(error))

    def test_greater_than_invalid(self):
        snippet = 'greater_than: {4}'
        schema = yaml.load(snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "greater_than" expects comparable '
                           'values.'), str(error))

    def test_greater_or_equal_validate(self):
        schema = {'greater_or_equal': 3.9}
        constraint = Constraint('prop', Schema.FLOAT, schema)
        self.assertIsNone(constraint.validate(3.9))
        self.assertIsNone(constraint.validate(4.0))

    def test_greater_or_equal_validate_fail(self):
        schema = {'greater_or_equal': 3.9}
        constraint = Constraint('prop', Schema.FLOAT, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 3.0)
        self.assertEqual(_('The value "3.0" of property "prop" must be '
                           'greater than or equal to "3.9".'),
                         str(error))

        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 3.8)
        self.assertEqual(_('The value "3.8" of property "prop" must be '
                           'greater than or equal to "3.9".'),
                         str(error))

    def test_greater_or_equal_invalid(self):
        snippet = 'greater_or_equal: {3.9}'
        schema = yaml.load(snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "greater_or_equal" expects '
                           'comparable values.'), str(error))

    def test_less_than_validate(self):
        schema = {'less_than': datetime.date(2014, 0o7, 25)}
        constraint = Constraint('prop', Schema.TIMESTAMP, schema)
        self.assertIsNone(constraint.validate(datetime.date(2014, 0o7, 20)))
        self.assertIsNone(constraint.validate(datetime.date(2014, 0o7, 24)))

    def test_less_than_validate_fail(self):
        schema = {'less_than': datetime.date(2014, 0o7, 25)}
        constraint = Constraint('prop', Schema.TIMESTAMP, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate,
                                  datetime.date(2014, 0o7, 25))
        self.assertEqual(_('The value "2014-07-25" of property "prop" must be '
                           'less than "2014-07-25".'),
                         str(error))

        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate,
                                  datetime.date(2014, 0o7, 27))
        self.assertEqual(_('The value "2014-07-27" of property "prop" must be '
                           'less than "2014-07-25".'),
                         str(error))

    def test_less_than_invalid(self):
        snippet = 'less_than: {3.9}'
        schema = yaml.load(snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "less_than" expects comparable '
                           'values.'), str(error))

    def test_less_or_equal_validate(self):
        schema = {'less_or_equal': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        self.assertIsNone(constraint.validate(4))
        self.assertIsNone(constraint.validate(3))

    def test_less_or_equal_validate_fail(self):
        schema = {'less_or_equal': 4}
        constraint = Constraint('prop', Schema.INTEGER, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 5)
        self.assertEqual(_('The value "5" of property "prop" must be less '
                           'than or equal to "4".'), str(error))

    def test_less_or_equal_invalid(self):
        snippet = 'less_or_equal: {3.9}'
        schema = yaml.load(snippet)
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.INTEGER,
                                  schema)
        self.assertEqual(_('The property "less_or_equal" expects comparable '
                           'values.'), str(error))

    def test_invalid_length(self):
        schema = {'length': 'four'}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.STRING,
                                  schema)
        self.assertEqual(_('The property "length" expects an integer.'),
                         str(error))

        schema = {'length': 4.5}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.STRING,
                                  schema)
        self.assertEqual(_('The property "length" expects an integer.'),
                         str(error))

    def test_length_validate(self):
        schema = {'length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        self.assertIsNone(constraint.validate('abcd'))

    def test_length_validate_fail(self):
        schema = {'length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 'abc')
        self.assertEqual(_('Length of value "abc" of property "prop" must '
                           'be equal to "4".'), str(error))

        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate,
                                  'abcde')
        self.assertEqual(_('Length of value "abcde" of property "prop" must '
                           'be equal to "4".'), str(error))

    def test_invalid_min_length(self):
        schema = {'min_length': 'four'}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.STRING,
                                  schema)
        self.assertEqual(_('The property "min_length" expects an integer.'),
                         str(error))

    def test_min_length_validate(self):
        schema = {'min_length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        self.assertIsNone(constraint.validate('abcd'))
        self.assertIsNone(constraint.validate('abcde'))

    def test_min_length_validate_fail(self):
        schema = {'min_length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 'abc')
        self.assertEqual(_('Length of value "abc" of property "prop" must '
                           'be at least "4".'), str(error))

    def test_invalid_max_length(self):
        schema = {'max_length': 'four'}
        error = self.assertRaises(exception.InvalidSchemaError, Constraint,
                                  'prop', Schema.STRING,
                                  schema)
        self.assertEqual(_('The property "max_length" expects an integer.'),
                         str(error))

    def test_max_length_validate(self):
        schema = {'max_length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        self.assertIsNone(constraint.validate('abcd'))
        self.assertIsNone(constraint.validate('abc'))

    def test_max_length_validate_fail(self):
        schema = {'max_length': 4}
        constraint = Constraint('prop', Schema.STRING, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate,
                                  'abcde')
        self.assertEqual(_('Length of value "abcde" of property "prop" '
                           'must be no greater than "4".'),
                         str(error))

    def test_pattern_validate(self):
        schema = {'pattern': '[0-9]*'}
        constraint = Constraint('prop', Schema.STRING, schema)
        self.assertIsNone(constraint.validate('123'))

    def test_pattern_validate_fail(self):
        schema = {'pattern': '[0-9]*'}
        constraint = Constraint('prop', Schema.STRING, schema)
        error = self.assertRaises(exception.ValidationError,
                                  constraint.validate, 'abc')
        self.assertEqual(_('The value "abc" of property "prop" does not '
                           'match pattern "[0-9]*".'), str(error))

    def test_min_length_with_map(self):
        schema = {'min_length': 1}
        constraint = Constraint('prop', Schema.MAP, schema)
        try:
            constraint.validate({"k": "v"})
        except Exception as ex:
            self.fail(ex)

    def test_max_length_with_map(self):
        schema = {'max_length': 1}
        constraint = Constraint('prop', Schema.MAP, schema)
        try:
            constraint.validate({"k": "v"})
        except Exception as ex:
            self.fail(ex)
