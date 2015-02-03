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

from translator.toscalib.properties import Property


class Capability(object):
    '''TOSCA built-in capabilities type.'''

    def __init__(self, name, properties, definition):
        self.name = name
        self._properties = properties
        self.definition = definition

    @property
    def properties(self):
        '''Return a list of property objects.'''
        properties = []
        props = self._properties
        if props:
            for name, value in props.items():
                for p in self.definition.properties_def:
                    if p.name == name:
                        properties.append(Property(name, value, p.schema))
                        break
        return properties
