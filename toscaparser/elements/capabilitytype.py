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

from toscaparser.elements.property_definition import PropertyDef
from toscaparser.elements.statefulentitytype import StatefulEntityType


class CapabilityTypeDef(StatefulEntityType):
    '''TOSCA built-in capabilities type.'''
    TOSCA_TYPEURI_CAPABILITY_ROOT = 'tosca.capabilities.Root'

    def __init__(self, name, ctype, ntype, custom_def=None):
        self.name = name
        super(CapabilityTypeDef, self).__init__(ctype, self.CAPABILITY_PREFIX,
                                                custom_def)
        self.nodetype = ntype
        self.properties = None
        self.custom_def = custom_def
        if self.PROPERTIES in self.defs:
            self.properties = self.defs[self.PROPERTIES]
        self.parent_capabilities = self._get_parent_capabilities(custom_def)

    def get_properties_def_objects(self):
        '''Return a list of property definition objects.'''
        properties = []
        parent_properties = {}
        if self.parent_capabilities:
            for type, value in self.parent_capabilities.items():
                parent_properties[type] = value.get('properties')
        if self.properties:
            for prop, schema in self.properties.items():
                properties.append(PropertyDef(prop, None, schema))
        if parent_properties:
            for parent, props in parent_properties.items():
                for prop, schema in props.items():
                    # add parent property if not overridden by children type
                    if not self.properties or \
                            prop not in self.properties.keys():
                        properties.append(PropertyDef(prop, None, schema))
        return properties

    def get_properties_def(self):
        '''Return a dictionary of property definition name-object pairs.'''
        return {prop.name: prop
                for prop in self.get_properties_def_objects()}

    def get_property_def_value(self, name):
        '''Return the definition of a given property name.'''
        props_def = self.get_properties_def()
        if props_def and name in props_def:
            return props_def[name].value

    def _get_parent_capabilities(self, custom_def=None):
        capabilities = {}
        parent_cap = self.parent_type
        if parent_cap:
            parent_cap = parent_cap.type
            while parent_cap != self.TOSCA_TYPEURI_CAPABILITY_ROOT:
                if parent_cap in self.TOSCA_DEF.keys():
                    capabilities[parent_cap] = self.TOSCA_DEF[parent_cap]
                elif custom_def and parent_cap in custom_def.keys():
                    capabilities[parent_cap] = custom_def[parent_cap]
                parent_cap = capabilities[parent_cap]['derived_from']
        return capabilities

    @property
    def parent_type(self):
        '''Return a capability this capability is derived from.'''
        if not hasattr(self, 'defs'):
            return None
        pnode = self.derived_from(self.defs)
        if pnode:
            return CapabilityTypeDef(self.name, pnode,
                                     self.nodetype, self.custom_def)

    def inherits_from(self, type_names):
        '''Check this capability is in type_names

           Check if this capability or some of its parent types
           are in the list of types: type_names
        '''
        if self.type in type_names:
            return True
        elif self.parent_type:
            return self.parent_type.inherits_from(type_names)
        else:
            return False
