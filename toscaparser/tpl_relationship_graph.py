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


class ToscaGraph(object):
    '''Graph of Tosca Node Templates.'''
    def __init__(self, nodetemplates):
        """
        Initialize the vertices

        Args:
            self: (todo): write your description
            nodetemplates: (str): write your description
        """
        self.nodetemplates = nodetemplates
        self.vertices = {}
        self._create()

    def _create_vertex(self, node):
        """
        Create a vertex from a node

        Args:
            self: (todo): write your description
            node: (todo): write your description
        """
        if node not in self.vertices:
            self.vertices[node.name] = node

    def _create_edge(self, node1, node2, relationship):
        """
        Create a new edge between two nodes.

        Args:
            self: (todo): write your description
            node1: (str): write your description
            node2: (str): write your description
            relationship: (todo): write your description
        """
        if node1 not in self.vertices:
            self._create_vertex(node1)
        self.vertices[node1.name]._add_next(node2,
                                            relationship)

    def vertex(self, node):
        """
        Return the vertex vertex

        Args:
            self: (todo): write your description
            node: (todo): write your description
        """
        if node in self.vertices:
            return self.vertices[node]

    def __iter__(self):
        """
        Return an iterator over vertices.

        Args:
            self: (todo): write your description
        """
        return iter(self.vertices.values())

    def _create(self):
        """
        Creates a relationship between all relations.

        Args:
            self: (todo): write your description
        """
        for node in self.nodetemplates:
            relation = node.relationships
            if relation:
                for rel, nodetpls in relation.items():
                    for tpl in self.nodetemplates:
                        if tpl.name == nodetpls.name:
                            self._create_edge(node, tpl, rel)
            self._create_vertex(node)
