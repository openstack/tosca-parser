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

from translator.toscalib.elements.entitytype import EntityType
from translator.toscalib.elements.property_definition import PropertyDef


class CapabilityTypeDef(EntityType):
    '''TOSCA built-in capabilities type.'''

    def __init__(self, name, ctype, ntype, properties):
        self.name = name
        self.type = ctype
        self.nodetype = ntype
        self.properties = properties
        self.defs = {}
        if ntype:
            self.defs = self.TOSCA_DEF[ctype]

    @property
    def properties_def(self):
        '''Return a list of property objects.'''
        properties = []
        props = self.entity_value(self.defs, 'properties')
        if props:
            if isinstance(props, dict):
                for prop, schema in props.items():
                    prop_val = None
                    for k, v in schema.items():
                        if k == 'default':
                            prop_val = v
                properties.append(PropertyDef(prop,
                                              prop_val, schema))
        if self.properties:
            for prop, value in self.properties.items():
                properties.append(PropertyDef(prop, value, None))
        return properties

    @property
    def parent_type(self):
        '''Return a capability this capability is derived from.'''
        return self.derived_from(self.defs)
