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


import logging

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.dataentity import DataEntity
from toscaparser.elements.constraints import Schema
from toscaparser.elements.entity_type import EntityType
from toscaparser.utils.gettextutils import _


log = logging.getLogger('tosca')


class Input(object):

    INPUTFIELD = (TYPE, DESCRIPTION, DEFAULT, CONSTRAINTS, REQUIRED, STATUS,
                  ENTRY_SCHEMA) = ('type', 'description', 'default',
                                   'constraints', 'required', 'status',
                                   'entry_schema')

    def __init__(self, name, schema_dict):
        """
        Add a new schema.

        Args:
            self: (todo): write your description
            name: (str): write your description
            schema_dict: (dict): write your description
        """
        self.name = name
        self.schema = Schema(name, schema_dict)

        self._validate_field()
        self.validate_type(self.type)

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
    def status(self):
        """
        Return the status of the schema.

        Args:
            self: (todo): write your description
        """
        return self.schema.status

    def validate(self, value=None):
        """
        Validate value

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        if value is not None:
            self._validate_value(value)

    def _validate_field(self):
        """
        Validate the field.

        Args:
            self: (todo): write your description
        """
        for name in self.schema.schema:
            if name not in self.INPUTFIELD:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Input "%s"' % self.name,
                                      field=name))

    def validate_type(self, input_type):
        """
        Validate input_type.

        Args:
            self: (todo): write your description
            input_type: (str): write your description
        """
        if input_type not in Schema.PROPERTY_TYPES:
            ExceptionCollector.appendException(
                ValueError(_('Invalid type "%s".') % type))

    # TODO(anyone) Need to test for any built-in datatype not just network
    # that is, tosca.datatypes.* and not assume tosca.datatypes.network.*
    # TODO(anyone) Add support for tosca.datatypes.Credential
    def _validate_value(self, value):
        """
        Validate the data type.

        Args:
            self: (todo): write your description
            value: (todo): write your description
        """
        tosca = EntityType.TOSCA_DEF
        datatype = None
        if self.type in tosca:
            datatype = tosca[self.type]
        elif EntityType.DATATYPE_NETWORK_PREFIX + self.type in tosca:
            datatype = tosca[EntityType.DATATYPE_NETWORK_PREFIX + self.type]

        DataEntity.validate_datatype(self.type, value, None, datatype)


class Output(object):

    OUTPUTFIELD = (DESCRIPTION, VALUE) = ('description', 'value')

    def __init__(self, name, attrs):
        """
        Initialize an attribute.

        Args:
            self: (todo): write your description
            name: (str): write your description
            attrs: (dict): write your description
        """
        self.name = name
        self.attrs = attrs

    @property
    def description(self):
        """
        Return the description of this object.

        Args:
            self: (todo): write your description
        """
        return self.attrs.get(self.DESCRIPTION)

    @property
    def value(self):
        """
        Returns the value of the field.

        Args:
            self: (todo): write your description
        """
        return self.attrs.get(self.VALUE)

    def validate(self):
        """
        Validate the field.

        Args:
            self: (todo): write your description
        """
        self._validate_field()

    def _validate_field(self):
        """
        Validate the field.

        Args:
            self: (todo): write your description
        """
        if not isinstance(self.attrs, dict):
            ExceptionCollector.appendException(
                MissingRequiredFieldError(what='Output "%s"' % self.name,
                                          required=self.VALUE))
        if self.value is None:
            ExceptionCollector.appendException(
                MissingRequiredFieldError(what='Output "%s"' % self.name,
                                          required=self.VALUE))
        for name in self.attrs:
            if name not in self.OUTPUTFIELD:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Output "%s"' % self.name,
                                      field=name))
