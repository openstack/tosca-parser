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

from toscaparser.common.exception import InvalidTypeError
from toscaparser.elements.attribute_definition import AttributeDef
from toscaparser.elements.entity_type import EntityType
from toscaparser.elements.property_definition import PropertyDef


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
        entire_entitytype = entitytype
        if not entitytype.startswith(self.TOSCA):
            entire_entitytype = prefix + entitytype
        if entire_entitytype in list(self.TOSCA_DEF.keys()):
            self.defs = self.TOSCA_DEF[entire_entitytype]
            entitytype = entire_entitytype
        elif custom_def and entitytype in list(custom_def.keys()):
            self.defs = custom_def[entitytype]
        else:
            raise InvalidTypeError(what=entitytype)
        self.type = entitytype

    def get_properties_def_objects(self):
        '''Return a list of property definition objects.'''
        properties = []
        props = self.get_definition(self.PROPERTIES)
        if props:
            for prop, schema in props.items():
                properties.append(PropertyDef(prop, None, schema))
        return properties

    def get_properties_def(self):
        '''Return a dictionary of property definition name-object pairs.'''
        return {prop.name: prop
                for prop in self.get_properties_def_objects()}

    def get_property_def_value(self, name):
        '''Return the property definition associated with a given name.'''
        props_def = self.get_properties_def()
        if props_def and name in props_def.keys():
            return props_def[name].value

    def get_attributes_def_objects(self):
        '''Return a list of attribute definition objects.'''
        attrs = self.get_value(self.ATTRIBUTES)
        if attrs:
            return [AttributeDef(attr, None, schema)
                    for attr, schema in attrs.items()]
        return []

    def get_attributes_def(self):
        '''Return a dictionary of attribute definition name-object pairs.'''
        return {attr.name: attr
                for attr in self.get_attributes_def_objects()}

    def get_attribute_def_value(self, name):
        '''Return the attribute definition associated with a given name.'''
        attrs_def = self.get_attributes_def()
        if attrs_def and name in attrs_def.keys():
            return attrs_def[name].value
