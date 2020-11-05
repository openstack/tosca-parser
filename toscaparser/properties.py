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

from toscaparser.dataentity import DataEntity
from toscaparser.elements.constraints import Schema
from toscaparser.functions import is_function


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

    def __init__(self, property_name, value, schema_dict, custom_def=None):
        """
        Initialize a custom schema.

        Args:
            self: (todo): write your description
            property_name: (str): write your description
            value: (todo): write your description
            schema_dict: (dict): write your description
            custom_def: (todo): write your description
        """
        self.name = property_name
        self.value = value
        self.custom_def = custom_def
        self.schema = Schema(property_name, schema_dict)

    @property
    def type(self):
        """
        Return the type of the schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.type

    @property
    def required(self):
        """
        Return the schema is required.

        Args:
            self: (todo): write your description
        """
        return self.schema.required

    @property
    def description(self):
        """
        Return the description of the schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.description

    @property
    def default(self):
        """
        Return the default schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.default

    @property
    def constraints(self):
        """
        Returns the constraints of the schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.constraints

    @property
    def entry_schema(self):
        """
        Return the schema schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.entry_schema

    def validate(self):
        '''Validate if not a reference property.'''
        if not is_function(self.value):
            if self.type == Schema.STRING:
                self.value = str(self.value)
            self.value = DataEntity.validate_datatype(self.type, self.value,
                                                      self.entry_schema,
                                                      self.custom_def,
                                                      self.name)
            self._validate_constraints()

    def _validate_constraints(self):
        """
        Validate the constraints.

        Args:
            self: (todo): write your description
        """
        if self.constraints:
            for constraint in self.constraints:
                constraint.validate(self.value)
