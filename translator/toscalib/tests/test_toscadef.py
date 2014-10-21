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
from translator.toscalib.elements.nodetype import NodeType
from translator.toscalib.tests.base import TestCase
compute_type = NodeType('tosca.nodes.Compute')
component_type = NodeType('tosca.nodes.SoftwareComponent')


class ToscaDefTest(TestCase):
    def test_type(self):
        self.assertEqual(compute_type.type, "tosca.nodes.Compute")
        self.assertRaises(InvalidNodeTypeError, NodeType,
                          'tosca.nodes.Invalid')

    def test_parent_type(self):
        self.assertEqual(compute_type.parent_type.type, "tosca.nodes.Root")

    def test_capabilities(self):
        self.assertEqual(
            ['tosca.capabilities.Container'],
            [c.type for c in compute_type.capabilities])

    def test_properties_def(self):
        self.assertEqual(
            ['disk_size', 'ip_address', 'mem_size',
             'num_cpus', 'os_arch', 'os_distribution',
             'os_type', 'os_version'],
            sorted([p.name for p in compute_type.properties_def]))
        self.assertTrue([p.required for p in compute_type.properties_def
                         if p.name == 'os_type'])

    def test_attributes_def(self):
        self.assertEqual(
            ['ip_address'],
            sorted([p.name for p in compute_type.attributes_def]))

    def test_requirements(self):
        self.assertEqual(
            [{'host': 'tosca.nodes.Compute'}],
            [r for r in component_type.requirements])

    def test_relationship(self):
        self.assertEqual(
            [('tosca.relationships.HostedOn', 'tosca.nodes.Compute')],
            [(relation.type, node.type) for
             relation, node in component_type.relationship.items()])
        self.assertIn(
            ('tosca.relationships.HostedOn', ['tosca.capabilities.Container']),
            [(relation.type, relation.valid_targets) for
             relation in list(component_type.relationship.keys())])

    def test_interfaces(self):
        self.assertEqual(compute_type.interfaces, None)
        root_node = NodeType('tosca.nodes.Root')
        self.assertIn('tosca.interfaces.node.Lifecycle', root_node.interfaces)

    def test_default_mem_size(self):
        test_value = 0
        for p_def in compute_type.properties_def:
            if p_def.name == 'mem_size':
                test_value = p_def.default
        self.assertEqual(test_value, 1024)
