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
from translator.toscalib.elements.capabilitytype import CapabilityTypeDef
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.property_definition import PropertyDef
from translator.toscalib.elements.relationshiptype import RelationshipType
from translator.toscalib.elements.statefulentitytype import StatefulEntityType


SECTIONS = (DERIVED_FROM, PROPERTIES, ATTRIBUTES, REQUIREMENTS,
            INTERFACES, CAPABILITIES) = \
           ('derived_from', 'properties', 'attributes', 'requirements',
            'interfaces', 'capabilities')


class NodeType(StatefulEntityType):
    '''TOSCA built-in node type.'''

    def __init__(self, ntype, custom_def=None):
        super(NodeType, self).__init__()
        if self.NODE_PREFIX not in ntype:
            ntype = self.NODE_PREFIX + ntype
        if ntype in list(self.TOSCA_DEF.keys()):
            self.defs = self.TOSCA_DEF[ntype]
        elif custom_def and ntype in list(custom_def.keys()):
            self.defs = custom_def[ntype]
        else:
            raise InvalidNodeTypeError(what=ntype)
        self.type = ntype
        self.related = {}

    @property
    def parent_type(self):
        '''Return a node this node is derived from.'''
        pnode = self.derived_from(self.defs)
        if pnode:
            return NodeType(pnode)

    @property
    def properties_def(self):
        '''Return a list of property definition objects.'''
        properties = []
        props = self.get_value(PROPERTIES)
        if props:
            for prop, schema in props.items():
                properties.append(PropertyDef(prop, None, schema))
        return properties

    @property
    def attributes_def(self):
        '''Return a list of attribute definition objects.'''
        attrs = self.get_value(ATTRIBUTES)
        if attrs:
            return [AttributeDef(attr, None, schema)
                    for attr, schema in attrs.items()]
        return []

    @property
    def relationship(self):
        '''Return a dictionary of relationships to other node types.

        This method returns a dictionary of named relationships that nodes
        of the current node type (self) can have to other nodes (of specific
        types) in a TOSCA template.

        '''
        relationship = {}
        requires = self.get_all_requirements()
        if requires:
            for req in requires:
                for key, value in req.items():
                    relation = self._get_relation(key, value)
                    rtype = RelationshipType(relation, key)
                    relatednode = NodeType(value)
                    relationship[rtype] = relatednode
        return relationship

    def _get_relation(self, key, ndtype):
        relation = None
        ntype = NodeType(ndtype)
        cap = ntype.capabilities
        for c in cap:
            if c.name == key:
                for r in self.RELATIONSHIP_TYPE:
                    rtypedef = ntype.TOSCA_DEF[r]
                    for properties in rtypedef.values():
                        if c.type in properties:
                            relation = r
                            break
                    if relation:
                        break
        return relation

    @property
    def capabilities(self):
        '''Return a list of capability objects.'''
        typecapabilities = []
        self.cap_prop = None
        self.cap_type = None
        caps = self.get_value(CAPABILITIES)
        if caps is None:
            caps = self.get_value(CAPABILITIES, None, True)
        if caps:
            cproperties = None
            for name, value in caps.items():
                ctype = value.get('type')
                if 'properties' in value:
                    cproperties = value.get('properties')
                cap = CapabilityTypeDef(name, ctype,
                                        self.type, cproperties)
                typecapabilities.append(cap)
        return typecapabilities

    @property
    def requirements(self):
        return self.get_value(REQUIREMENTS)

    def get_all_requirements(self):
        requires = self.requirements
        parent_node = self.parent_type
        if requires is None:
            requires = self.get_value(REQUIREMENTS, None, True)
            parent_node = parent_node.parent_type
        if parent_node:
            while parent_node.type != 'tosca.nodes.Root':
                req = parent_node.get_value(REQUIREMENTS, None, True)
                requires.extend(req)
                parent_node = parent_node.parent_type
        return requires

    @property
    def interfaces(self):
        return self.get_value(INTERFACES)

    @property
    def lifecycle_inputs(self):
        '''Return inputs to life cycle operations if found.'''
        inputs = []
        interfaces = self.interfaces
        if interfaces:
            for name, value in interfaces.items():
                if name == 'tosca.interfaces.node.Lifecycle':
                    for x, y in value.items():
                        if x == 'inputs':
                            for i in y.iterkeys():
                                inputs.append(i)
        return inputs

    @property
    def lifecycle_operations(self):
        '''Return available life cycle operations if found.'''
        ops = None
        interfaces = self.interfaces
        if interfaces:
            i = InterfacesDef(self.type, 'tosca.interfaces.node.Lifecycle')
            ops = i.lifecycle_ops
        return ops

    def get_capability(self, name):
        for key, value in self.capabilities:
            if key == name:
                return value

    def get_capability_type(self, name):
        for key, value in self.get_capability(name):
            if key == type:
                return value

    def get_value(self, ndtype, defs=None, parent=None):
        value = None
        if defs is None:
            defs = self.defs
        if ndtype in defs:
            value = defs[ndtype]
        if parent and not value:
            p = self.parent_type
            while value is None:
                #check parent node
                if not p:
                    break
                if p and p.type == 'tosca.nodes.Root':
                    break
                value = p.get_value(ndtype)
                p = p.parent_type
        return value
