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

from translator.toscalib.elements.capabilitytype import CapabilityTypeDef
import translator.toscalib.elements.interfaces as ifaces
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.relationshiptype import RelationshipType
from translator.toscalib.elements.statefulentitytype import StatefulEntityType


class NodeType(StatefulEntityType):
    '''TOSCA built-in node type.'''

    def __init__(self, ntype, custom_def=None):
        super(NodeType, self).__init__(ntype, self.NODE_PREFIX, custom_def)
        self.custom_def = custom_def

    @property
    def parent_type(self):
        '''Return a node this node is derived from.'''
        pnode = self.derived_from(self.defs)
        if pnode:
            return NodeType(pnode)

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
            keyword = None
            node_type = None
            for req in requires:
                #get all keys in requirement
                if 'relationship' in req:
                    keys = req.keys()
                    for k in keys:
                        if k not in self.SECTIONS:
                            relation = req.get('relationship')
                            node_type = req.get(k)
                            keyword = k
                            break
                else:
                    for key, value in req.items():
                        if key == 'type':
                            continue
                        if key == 'interfaces':
                            continue
                        else:
                            relation = self._get_relation(key, value)
                            keyword = key
                            node_type = value
                rtype = RelationshipType(relation, keyword, req)
                relatednode = NodeType(node_type, self.custom_def)
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
                    else:
                        for properties in rtypedef.values():
                            if c.parent_type in properties:
                                relation = r
                                break
        return relation

    @property
    def capabilities(self):
        '''Return a list of capability objects.'''
        typecapabilities = []
        caps = self.get_value(self.CAPABILITIES)
        if caps is None:
            caps = self.get_value(self.CAPABILITIES, None, True)
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
        return self.get_value(self.REQUIREMENTS)

    def get_all_requirements(self):
        requires = self.requirements
        parent_node = self.parent_type
        if requires is None:
            requires = self.get_value(self.REQUIREMENTS, None, True)
            parent_node = parent_node.parent_type
        if parent_node:
            while parent_node.type != 'tosca.nodes.Root':
                req = parent_node.get_value(self.REQUIREMENTS, None, True)
                for r in req:
                    if r not in requires:
                        requires.append(r)
                parent_node = parent_node.parent_type
        return requires

    @property
    def interfaces(self):
        return self.get_value(self.INTERFACES)

    @property
    def lifecycle_inputs(self):
        '''Return inputs to life cycle operations if found.'''
        inputs = []
        interfaces = self.interfaces
        if interfaces:
            for name, value in interfaces.items():
                if name == ifaces.LIFECYCLE:
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
            i = InterfacesDef(self.type, ifaces.LIFECYCLE)
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
