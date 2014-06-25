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


import logging

from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.elements.constraints import Constraint
from translator.toscalib.properties import Property


log = logging.getLogger('tosca')


class Input(object):

    INPUTFIELD = (TYPE, DESCRIPTION, DEFAULT, CONSTRAINTS) = \
        ('type', 'description', 'default', 'constraints')

    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    @property
    def type(self):
        return self.schema[self.TYPE]

    @property
    def description(self):
        if Property.DESCRIPTION in self.schema:
            return self.schema[self.DESCRIPTION]

    @property
    def default(self):
        if self.Property.DEFAULT in self.schema:
            return self.schema[self.DEFAULT]

    @property
    def constraints(self):
        if Property.CONSTRAINTS in self.schema:
            return self.schema[self.CONSTRAINTS]

    def validate(self):
        self._validate_field()
        self.validate_type(self.type)
        if self.constraints:
            self.validate_constraints(self.constraints)

    def _validate_field(self):
        if not isinstance(self.schema, dict):
            raise MissingRequiredFieldError(what='Input %s' % self.name,
                                            required=self.TYPE)
        try:
            self.type
        except KeyError:
            raise MissingRequiredFieldError(what='Input %s' % self.name,
                                            required=self.TYPE)
        for name in self.schema:
            if name not in self.INPUTFIELD:
                raise UnknownFieldError(what='Input %s' % self.name,
                                        field=name)

    def validate_type(self, input_type):
        if input_type not in Constraint.PROPERTY_TYPES:
            raise ValueError(_('Invalid type %s') % type)

    def validate_constraints(self, constraints):
        for constraint in constraints:
            Constraint(self.name, self.type, constraint)


class Output(object):

    OUTPUTFIELD = (DESCRIPTION, VALUE) = ('description', 'value')

    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    @property
    def description(self):
        return self.attrs[self.DESCRIPTION]

    @property
    def value(self):
        return self.attrs[self.VALUE]

    def validate(self):
        self._validate_field()

    def _validate_field(self):
        if not isinstance(self.attrs, dict):
            raise MissingRequiredFieldError(what='Output %s' % self.name,
                                            required=self.VALUE)
        try:
            self.value
        except KeyError:
            raise MissingRequiredFieldError(what='Output %s' % self.name,
                                            required=self.VALUE)
        for name in self.attrs:
            if name not in self.OUTPUTFIELD:
                raise UnknownFieldError(what='Output %s' % self.name,
                                        field=name)
