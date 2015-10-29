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

    def __init__(self, name, ctype, ntype, custom_def=None):
        self.name = name
        super(CapabilityTypeDef, self).__init__(ctype, self.CAPABILITY_PREFIX,
                                                custom_def)
        self.nodetype = ntype
        self.properties = None
        if self.PROPERTIES in self.defs:
            self.properties = self.defs[self.PROPERTIES]
        self.parent_capabilities = self._get_parent_capabilities()

    def get_properties_def_objects(self):
        '''Return a list of property definition objects.'''
        properties = []
        parent_properties = {}
        if self.parent_capabilities:
            for type, value in self.parent_capabilities.items():
                parent_properties[type] = value.get('properties')
        if self.properties:
            for prop, schema in self.properties.items(): 
                # in some cases (see tosca.capabilities.Endpoint.Admin definition) the property only has a value
                # and it has to get the schema from the parent definition 
                if isinstance(schema, dict):
                    properties.append(PropertyDef(prop, None, schema))
                else:
                    prop_value = schema
                    for parent_prop in parent_properties.values():
                        if prop in parent_prop:
                            schema = parent_prop[prop]
                            properties.append(PropertyDef(prop, prop_value, schema))
        if parent_properties:
            for parent, props in parent_properties.items():
                for prop, schema in props.items():
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

    def _get_parent_capabilities(self):
        capabilities = {}
        parent_cap = self.parent_type
        if parent_cap:
            while parent_cap != 'tosca.capabilities.Root':
                capabilities[parent_cap] = self.TOSCA_DEF[parent_cap]
                parent_cap = capabilities[parent_cap]['derived_from']
        return capabilities

    @property
    def parent_type(self):
        '''Return a capability this capability is derived from.'''
        return self.derived_from(self.defs)
