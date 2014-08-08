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

from translator.toscalib.elements.property_definition import PropertyDef
from translator.toscalib.elements.statefulentitytype import StatefulEntityType


class RelationshipType(StatefulEntityType):
    '''TOSCA built-in relationship type.'''
    def __init__(self, type, capability_name, custom_def=None):
        super(RelationshipType, self).__init__(type, self.RELATIONSHIP_PREFIX,
                                               custom_def)
        self.capability_name = capability_name

    @property
    def valid_targets(self):
        return self.entity_value(self.defs, 'valid_targets')

    @property
    def parent_type(self):
        '''Return a relationship this relationship is derived from.'''
        return self.derived_from(self.defs)

    @property
    def properties_def(self):
        '''Return a list of property definition objects.'''
        properties = []
        props = self.get_value(self.PROPERTIES)
        if props:
            for prop, schema in props.items():
                properties.append(PropertyDef(prop, None, schema))
        return properties
