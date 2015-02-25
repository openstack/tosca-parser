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

from translator.toscalib.common import exception
import translator.toscalib.elements.interfaces as ifaces
from translator.toscalib.elements.nodetype import NodeType
from translator.toscalib.tests.base import TestCase

compute_type = NodeType('tosca.nodes.Compute')
component_type = NodeType('tosca.nodes.SoftwareComponent')
network_type = NodeType('tosca.nodes.network.Network')
network_port_type = NodeType('tosca.nodes.network.Port')
webserver_type = NodeType('tosca.nodes.WebServer')


class ToscaDefTest(TestCase):
    def test_type(self):
        self.assertEqual(compute_type.type, "tosca.nodes.Compute")
        self.assertRaises(exception.InvalidTypeError, NodeType,
                          'tosca.nodes.Invalid')
        self.assertEqual(network_type.type, "tosca.nodes.network.Network")
        self.assertEqual(network_port_type.type, "tosca.nodes.network.Port")

    def test_parent_type(self):
        self.assertEqual(compute_type.parent_type.type, "tosca.nodes.Root")
        self.assertEqual(network_type.parent_type.type, "tosca.nodes.Root")
        self.assertEqual(network_port_type.parent_type.type,
                         "tosca.nodes.Root")

    def test_capabilities(self):
        self.assertEqual(
            sorted(['tosca.capabilities.Container',
                    'tosca.capabilities.network.Bindable']),
            sorted([c.type for c in compute_type.capabilities]))
        self.assertEqual(
            ['tosca.capabilities.network.Linkable'],
            [c.type for c in network_type.capabilities])
        for cap in webserver_type.capabilities:
            if cap.type == 'tosca.capabilities.Endpoint':
                webserver_props = cap.properties_def
                break
        self.assertEqual(
            ['initiator', 'network_name', 'port',
             'port_name', 'ports', 'protocol',
             'secure', 'url_path'],
            sorted([p.name for p in webserver_props]))

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
        self.assertIn(
            ('tosca.relationships.network.BindsTo', 'tosca.nodes.Compute'),
            [(relation.type, node.type) for
             relation, node in network_port_type.relationship.items()])
        self.assertIn(
            ('tosca.relationships.network.LinksTo',
             'tosca.nodes.network.Network'),
            [(relation.type, node.type) for
             relation, node in network_port_type.relationship.items()])

    def test_interfaces(self):
        self.assertEqual(compute_type.interfaces, None)
        root_node = NodeType('tosca.nodes.Root')
        self.assertIn(ifaces.LIFECYCLE, root_node.interfaces)
