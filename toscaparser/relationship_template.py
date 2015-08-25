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

from toscaparser.entity_template import EntityTemplate
from toscaparser.properties import Property

SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
            INTERFACES, CAPABILITIES, TYPE) = \
           ('derived_from', 'properties', 'requirements', 'interfaces',
            'capabilities', 'type')

log = logging.getLogger('tosca')


class RelationshipTemplate(EntityTemplate):
    '''Relationship template.'''
    def __init__(self, relationship_template, name, custom_def=None):
        super(RelationshipTemplate, self).__init__(name,
                                                   relationship_template,
                                                   'relationship_type',
                                                   custom_def)
        self.name = name.lower()

    def get_properties_objects(self):
        '''Return properties objects for this template.'''
        if self._properties is None:
            self._properties = self._create_relationship_properties()
        return self._properties

    def _create_relationship_properties(self):
        props = []
        properties = {}
        relationship = self.entity_tpl.get('relationship')
        if relationship:
            properties = self.type_definition.get_value(self.PROPERTIES,
                                                        relationship) or {}
        if not properties:
            properties = self.entity_tpl.get(self.PROPERTIES) or {}

        if properties:
            for name, value in properties.items():
                props_def = self.type_definition.get_properties_def()
                if props_def and name in props_def:
                    if name in properties.keys():
                        value = properties.get(name)
                    prop = Property(name, value,
                                    props_def[name].schema, self.custom_def)
                    props.append(prop)
        for p in self.type_definition.get_properties_def_objects():
            if p.default is not None and p.name not in properties.keys():
                prop = Property(p.name, p.default, p.schema, self.custom_def)
                props.append(prop)
        return props

    def validate(self):
        self._validate_properties(self.entity_tpl, self.type_definition)
