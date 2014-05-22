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

from translator.toscalib.elements.constraints import Constraint
from translator.toscalib.elements.properties import PropertyDef

log = logging.getLogger('tosca')


class Input(object):
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    @property
    def type(self):
        return self.schema['type']

    @property
    def description(self):
        if PropertyDef.DESCRIPTION in self.schema:
            return self.schema['description']

    @property
    def default(self):
        if self.PropertyDef.DEFAULT in self.schema:
            return self.schema['default']

    @property
    def constraints(self):
        if PropertyDef.CONSTRAINTS in self.schema:
            return self.schema['constraints']

    def validate(self):
        self.validate_type(self.type)
        if self.constraints:
            self.validate_constraints(self.constraints)

    def validate_type(self, input_type):
        if input_type not in PropertyDef.PROPERTIY_TYPES:
            raise ValueError(_('Invalid type %s') % type)

    def validate_constraints(self, constraints):
        for constraint in constraints:
            for key in constraint.keys():
                if key not in Constraint.CONSTRAINTS:
                    raise ValueError(_('Invalid constraint %s') % constraint)


class Output(object):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    @property
    def description(self):
        return self.attrs['description']

    @property
    def value(self):
        return self.attrs['value']
