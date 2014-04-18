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


class PropertyDef(object):
    '''TOSCA built-in Property type.'''

    PROPERTY_KEYS = (
        TYPE, REQUIRED, DESCRIPTION, DEFAULT, CONSTRAINTS,
    ) = (
        'type', 'required', 'description', 'default', 'constraints'
    )
    PROPERTIY_TYPES = (
        INTEGER,
        STRING, NUMBER, BOOLEAN,
        LIST
    ) = (
        'integer',
        'string', 'number', 'boolean',
        'list'
    )

    def __init__(self, name, nodetype, schema=None, value=None, tpl_name=None):
        self.name = name
        self.nodetype = nodetype
        self.schema = schema
        self.value = value
        self.tpl_name = tpl_name

    @property
    def required(self):
        if self.schema:
            for prop_key, prop_vale in self.schema.items():
                if prop_key == self.REQUIRED and prop_vale:
                    return True
        return False

    @property
    def constraints(self):
        if self.schema:
            if self.CONSTRAINTS in self.schema:
                return self.schema[self.CONSTRAINTS]

    @property
    def description(self):
        if self.schema:
            if self.DESCRIPTION in self.schema:
                return self.schema[self.DESCRIPTION]
        return ''

    def validate(self):
        '''Validate if not a reference property.'''
        if not isinstance(self.value, dict):
            self._validate_constraints()
            self._validate_datatype()

    def _validate_datatype(self):
        if self.schema:
            dtype = self.schema[self.TYPE]
            if dtype == self.STRING:
                return Constraint.validate_string(self.value)
            elif dtype == self.INTEGER:
                return Constraint.validate_integer(self.value)
            elif dtype == self.NUMBER:
                return Constraint.validate_number(self.value)
            elif dtype == self.LIST:
                return Constraint.validate_list(self.value)

    def _validate_constraints(self):
        constraints = self.constraints
        if constraints:
            for constraint in constraints:
                Constraint(self.name, self.value, constraint).validate()
