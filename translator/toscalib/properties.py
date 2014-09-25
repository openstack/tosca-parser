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

import re

from translator.toscalib.common.exception import InvalidPropertyValueError
from translator.toscalib.common.exception import InvalidSchemaError
from translator.toscalib.elements.constraints import Constraint
from translator.toscalib.elements.constraints import Schema
from translator.toscalib.functions import is_function
from translator.toscalib.utils.gettextutils import _


class Property(object):
    '''TOSCA built-in Property type.'''

    PROPERTY_KEYS = (
        TYPE, REQUIRED, DESCRIPTION, DEFAULT, CONSTRAINTS
    ) = (
        'type', 'required', 'description', 'default', 'constraints'
    )

    ENTRY_SCHEMA_KEYS = (
        ENTRYTYPE, ENTRYPROPERTIES
    ) = (
        'type', 'properties'
    )

    def __init__(self, property_name, value, schema_dict):
        self.name = property_name
        self.value = self._convert_value(value)
        self.schema = Schema(property_name, schema_dict)

    @property
    def type(self):
        return self.schema.type

    @property
    def required(self):
        return self.schema.required

    @property
    def description(self):
        return self.schema.description

    @property
    def default(self):
        return self.schema.default

    @property
    def constraints(self):
        return self.schema.constraints

    @property
    def entry_schema(self):
        return self.schema.entry_schema

    def validate(self):
        '''Validate if not a reference property.'''
        if not is_function(self.value):
            if self.type == Schema.STRING:
                self.value = str(self.value)

            self._validate_datatype()
            self._validate_constraints()

            if self.type == Schema.LIST:
                self._validate_children(enumerate(self.value))
            elif self.type == Schema.MAP:
                self._validate_children(self.value.items())

    def _validate_datatype(self):
            dtype = self.type
            if dtype == Schema.STRING:
                return Constraint.validate_string(self.value)
            elif dtype == Schema.INTEGER:
                return Constraint.validate_integer(self.value)
            elif dtype == Schema.NUMBER:
                return Constraint.validate_number(self.value)
            elif dtype == Schema.LIST:
                return Constraint.validate_list(self.value)
            elif dtype == Schema.MAP:
                return Constraint.validate_map(self.value)
            elif dtype == Schema.BOOLEAN:
                return Constraint.validate_boolean(self.value)
            else:
                msg = _('Type (%s) is not a valid data type.') % self.type
                raise InvalidSchemaError(message=msg)

    def _validate_children(self, child_values):
        entry_schema = self.schema.entry_schema
        if entry_schema is not None:
            if entry_schema.get(self.ENTRYTYPE) is not None:
                for value in dict(child_values).values():
                    entry_prop = Property(_('Entry of %s') % self.name,
                                          value, entry_schema)
                    entry_prop.validate()
                return child_values

            properties_schema = entry_schema.get(self.ENTRYPROPERTIES)
            if properties_schema is not None:
                for entry_values in dict(child_values).values():
                    for k in list(properties_schema):
                        entry_of_prop = Property(k, entry_values.get(k),
                                                 properties_schema.get(k))
                        entry_of_prop.validate()
        return child_values

    def _validate_constraints(self):
        if self.constraints:
            for constraint in self.constraints:
                constraint.validate(self.value)

    def _convert_value(self, value):
        if self.name == 'mem_size':
            mem_reader = re.compile('(\d*)\s*(\w*)')
            matcher = str(value)
            result = mem_reader.match(matcher).groups()
            r = []
            if (result[0] != '') and (result[1] == ''):
                r = int(result[0])
            elif (result[0] != '') and (result[1] == 'MB'):
                r = int(result[0])
            elif (result[0] != '') and (result[1] == 'GB'):
                r = int(result[0]) * 1024
            else:
                raise InvalidPropertyValueError(what=self.name)
            return r
        return value
