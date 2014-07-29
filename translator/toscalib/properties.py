# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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

from translator.toscalib.elements.constraints import Constraint
from translator.toscalib.elements.constraints import Schema


class Property(object):
    '''TOSCA built-in Property type.'''

    PROPERTY_KEYS = (
        TYPE, REQUIRED, DESCRIPTION, DEFAULT, CONSTRAINTS,
    ) = (
        'type', 'required', 'description', 'default', 'constraints'
    )

    def __init__(self, property_name, value, schema_dict):
        self.name = property_name
        self.value = value
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

    def validate(self):
        '''Validate if not a reference property.'''
        if not isinstance(self.value, dict):
            self._validate_datatype()
            self._validate_constraints()

    def _validate_datatype(self):
        try:
            dtype = self.type
            if dtype == Schema.STRING:
                return Constraint.validate_string(self.value)
            elif dtype == Schema.INTEGER:
                return Constraint.validate_integer(self.value)
            elif dtype == Schema.NUMBER:
                return Constraint.validate_number(self.value)
            elif dtype == Schema.LIST:
                return Constraint.validate_list(self.value)
        except Exception:
            pass

    def _validate_constraints(self):
        if self.constraints:
            for constraint in self.constraints:
                constraint.validate(self.value)
