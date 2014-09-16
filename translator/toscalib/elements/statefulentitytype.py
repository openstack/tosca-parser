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

from translator.toscalib.common.exception import InvalidNodeTypeError
from translator.toscalib.elements.attribute_definition import AttributeDef
from translator.toscalib.elements.entitytype import EntityType
from translator.toscalib.elements.property_definition import PropertyDef


class StatefulEntityType(EntityType):
    '''Class representing TOSCA states.'''

    interfaces_node_lifecycle_operations = ['create',
                                            'configure', 'start',
                                            'stop', 'delete']

    interfaces_relationship_confiure_operations = ['post_configure_source',
                                                   'post_configure_target',
                                                   'add_target',
                                                   'remove_target']

    def __init__(self, entitytype, prefix, custom_def=None):
        if prefix not in entitytype:
            entitytype = prefix + entitytype
        if entitytype in list(self.TOSCA_DEF.keys()):
            self.defs = self.TOSCA_DEF[entitytype]
        elif custom_def and entitytype in list(custom_def.keys()):
            self.defs = custom_def[entitytype]
        else:
            raise InvalidNodeTypeError(what=entitytype)
        self.type = entitytype

    @property
    def properties_def(self):
        '''Return a list of property definition objects.'''
        properties = []
        props = self.get_value(self.PROPERTIES)
        if props:
            for prop, schema in props.items():
                properties.append(PropertyDef(prop, None, schema))
        return properties

    @property
    def attributes_def(self):
        '''Return a list of attribute definition objects.'''
        attrs = self.get_value(self.ATTRIBUTES)
        if attrs:
            return [AttributeDef(attr, None, schema)
                    for attr, schema in attrs.items()]
        return []
