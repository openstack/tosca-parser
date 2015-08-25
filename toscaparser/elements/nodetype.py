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

from toscaparser.elements.capabilitytype import CapabilityTypeDef
import toscaparser.elements.interfaces as ifaces
from toscaparser.elements.interfaces import InterfacesDef
from toscaparser.elements.relationshiptype import RelationshipType
from toscaparser.elements.statefulentitytype import StatefulEntityType


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
            # NOTE(sdmonov): Check if requires is a dict.
            # If it is a dict convert it to a list of dicts.
            # This is needed because currently the code below supports only
            # lists as requirements definition. The following check will
            # make sure if a map (dict) was provided it will be converted to
            # a list before proceeding to the parsing.
            if isinstance(requires, dict):
                requires = [{key: value} for key, value in requires.items()]

            keyword = None
            node_type = None
            for require in requires:
                for key, req in require.items():
                    if 'relationship' in req:
                        relation = req.get('relationship')
                        if 'type' in relation:
                            relation = relation.get('type')
                        node_type = req.get('node')
                        value = req
                        if node_type:
                            keyword = 'node'
                        else:
                            # If value is a dict and has a type key
                            # we need to lookup the node type using
                            # the capability type
                            value = req
                            if isinstance(value, dict):
                                captype = value['capability']
                                value = (self.
                                         _get_node_type_by_cap(key, captype))
                            relation = self._get_relation(key, value)
                            keyword = key
                            node_type = value
                rtype = RelationshipType(relation, keyword, req)
                relatednode = NodeType(node_type, self.custom_def)
                relationship[rtype] = relatednode
        return relationship

    def _get_node_type_by_cap(self, key, cap):
        '''Find the node type that has the provided capability

        This method will lookup all node types if they have the
        provided capability.
        '''

        # Filter the node types
        node_types = [node_type for node_type in self.TOSCA_DEF.keys()
                      if node_type.startswith(self.NODE_PREFIX) and
                      node_type != 'tosca.nodes.Root']

        for node_type in node_types:
            node_def = self.TOSCA_DEF[node_type]
            if isinstance(node_def, dict) and 'capabilities' in node_def:
                node_caps = node_def['capabilities']
                for value in node_caps.values():
                    if isinstance(value, dict) and \
                            'type' in value and value['type'] == cap:
                        return node_type

    def _get_relation(self, key, ndtype):
        relation = None
        ntype = NodeType(ndtype)
        caps = ntype.get_capabilities()
        if caps and key in caps.keys():
            c = caps[key]
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

    def get_capabilities_objects(self):
        '''Return a list of capability objects.'''
        typecapabilities = []
        caps = self.get_value(self.CAPABILITIES)
        if caps is None:
            caps = self.get_value(self.CAPABILITIES, None, True)
        if caps:
            for name, value in caps.items():
                ctype = value.get('type')
                cap = CapabilityTypeDef(name, ctype, self.type,
                                        self.custom_def)
                typecapabilities.append(cap)
        return typecapabilities

    def get_capabilities(self):
        '''Return a dictionary of capability name-objects pairs.'''
        return {cap.name: cap
                for cap in self.get_capabilities_objects()}

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
        caps = self.get_capabilities()
        if caps and name in caps.keys():
            return caps[name].value

    def get_capability_type(self, name):
        captype = self.get_capability(name)
        if captype and name in captype.keys():
            return captype[name].value
