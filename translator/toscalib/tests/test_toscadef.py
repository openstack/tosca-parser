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
                    'tosca.capabilities.OperatingSystem',
                    'tosca.capabilities.network.Bindable',
                    'tosca.capabilities.Scalable']),
            sorted([c.type for c in compute_type.get_capabilities_objects()]))
        self.assertEqual(
            ['tosca.capabilities.network.Linkable'],
            [c.type for c in network_type.get_capabilities_objects()])
        endpoint_props_def_objects = \
            self._get_capability_properties_def_objects(
                webserver_type.get_capabilities_objects(),
                'tosca.capabilities.Endpoint')
        self.assertEqual(
            ['initiator', 'network_name', 'port',
             'port_name', 'ports', 'protocol',
             'secure', 'url_path'],
            sorted([p.name for p in endpoint_props_def_objects]))
        endpoint_props_def = self._get_capability_properties_def(
            webserver_type.get_capabilities_objects(),
            'tosca.capabilities.Endpoint')
        self.assertEqual(
            ['initiator', 'network_name', 'port',
             'port_name', 'ports', 'protocol',
             'secure', 'url_path'],
            sorted(endpoint_props_def.keys()))
        endpoint_prop_def = self._get_capability_property_def(
            webserver_type.get_capabilities_objects(),
            'tosca.capabilities.Endpoint',
            'initiator')
        self.assertEqual(None, endpoint_prop_def)
        os_props = self._get_capability_properties_def_objects(
            compute_type.get_capabilities_objects(),
            'tosca.capabilities.OperatingSystem')
        self.assertEqual(
            ['architecture', 'distribution', 'type', 'version'],
            sorted([p.name for p in os_props]))
        self.assertTrue([p.required for p in os_props if p.name == 'type'])

    def _get_capability_properties_def_objects(self, caps, type):
        properties_def = None
        for cap in caps:
            if cap.type == type:
                properties_def = cap.get_properties_def_objects()
                break
        return properties_def

    def _get_capability_properties_def(self, caps, type):
        properties_def = None
        for cap in caps:
            if cap.type == type:
                properties_def = cap.get_properties_def()
                break
        return properties_def

    def _get_capability_property_def(self, caps, type, property):
        property_def = None
        for cap in caps:
            if cap.type == type:
                property_def = cap.get_property_def_value(property)
                break
        return property_def

    def test_properties_def(self):
        self.assertEqual(
            ['disk_size', 'mem_size', 'num_cpus'],
            sorted(compute_type.get_properties_def().keys()))

    def test_attributes_def(self):
        self.assertEqual(
            ['private_address', 'public_address'],
            sorted(compute_type.get_attributes_def().keys()))

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
