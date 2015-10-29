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

from toscaparser.properties import Property


class Capability(object):
    '''TOSCA built-in capabilities type.'''

    def __init__(self, name, properties, definition):
        self.name = name
        self._properties = properties
        self.definition = definition

    def get_properties_objects(self):
        '''Return a list of property objects.'''
        properties = []
        # Enable to get properties from the definition
        props_def = self.definition.get_properties_def()
        if props_def:
            props_name = props_def.keys()
            
        for name in props_name:
            value = None
            if name in self._properties:
                value = self._properties[name]
            properties.append(Property(name, value, props_def[name].schema))
        return properties

    def get_properties(self):
        '''Return a dictionary of property name-object pairs.'''
        return {prop.name: prop
                for prop in self.get_properties_objects()}

    def get_property_value(self, name):
        '''Return the value of a given property name.'''
        props = self.get_properties()
        if props and name in props:
            return props[name].value
