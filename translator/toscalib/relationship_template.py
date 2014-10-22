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

from translator.toscalib.entity_template import EntityTemplate

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

    def validate(self):
        self._validate_properties(self.entity_tpl, self.type_definition)
