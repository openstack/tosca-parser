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

from toscaparser.common import exception
from toscaparser.elements.artifacttype import ArtifactTypeDef
from toscaparser.elements.entity_type import EntityType
from toscaparser.elements.grouptype import GroupType
import toscaparser.elements.interfaces as ifaces
from toscaparser.elements.nodetype import NodeType
from toscaparser.elements.policytype import PolicyType
from toscaparser.tests.base import TestCase

compute_type = NodeType('tosca.nodes.Compute')
component_type = NodeType('tosca.nodes.SoftwareComponent')
network_type = NodeType('tosca.nodes.network.Network')
network_port_type = NodeType('tosca.nodes.network.Port')
webserver_type = NodeType('tosca.nodes.WebServer')
database_type = NodeType('tosca.nodes.Database')
artif_root_type = ArtifactTypeDef('tosca.artifacts.Root')
artif_file_type = ArtifactTypeDef('tosca.artifacts.File')
artif_bash_type = ArtifactTypeDef('tosca.artifacts.Implementation.Bash')
artif_python_type = ArtifactTypeDef('tosca.artifacts.Implementation.Python')
artif_container_docker_type = ArtifactTypeDef('tosca.artifacts.'
                                              'Deployment.Image.'
                                              'Container.Docker')
artif_vm_iso_type = ArtifactTypeDef('tosca.artifacts.'
                                    'Deployment.Image.VM.ISO')
artif_vm_qcow2_type = ArtifactTypeDef('tosca.artifacts.'
                                      'Deployment.Image.VM.QCOW2')
policy_root_type = PolicyType('tosca.policies.Root')
policy_placement_type = PolicyType('tosca.policies.Placement')
policy_scaling_type = PolicyType('tosca.policies.Scaling')
policy_update_type = PolicyType('tosca.policies.Update')
policy_performance_type = PolicyType('tosca.policies.Performance')
group_type = GroupType('tosca.groups.Root')


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

    def test_group(self):
        self.assertEqual(group_type.type, "tosca.groups.Root")
        self.assertIsNone(group_type.parent_type)
        self.assertIn(ifaces.LIFECYCLE_SHORTNAME, group_type.interfaces)

    def test_capabilities(self):
        # Assure the normative Compute node type
        # has all the required Capability types
        # regardless of symbloc name
        # TODO(Matt) - since Compute IS a normative node type
        # we SHOULD test symbolic capability names as well
        self.assertEqual(
            ['tosca.capabilities.Container',
             'tosca.capabilities.Endpoint.Admin',
             'tosca.capabilities.Node',
             'tosca.capabilities.OperatingSystem',
             'tosca.capabilities.Scalable',
             'tosca.capabilities.network.Bindable'],
            sorted([c.type for c in compute_type.get_capabilities_objects()]))
        # Assure the normative Network node type
        # hsa all the required Capability types
        # TODO(Matt) - since Network IS a normative node type
        # we SHOULD test symbolic capability names as well
        self.assertEqual(
            ['tosca.capabilities.Node',
             'tosca.capabilities.network.Linkable'],
            sorted([c.type for c in network_type.get_capabilities_objects()]))

        # Assure the normative WebServer node type's
        # Endpoint cap. has all required property names
        # Note: we are testing them in alphabetic sort order
        endpoint_props_def_objects = \
            self._get_capability_properties_def_objects(
                webserver_type.get_capabilities_objects(),
                'tosca.capabilities.Endpoint')
        # Assure WebServer's Endpoint capability's properties have their
        # required keyname value set correctly
        self.assertEqual(
            [('initiator', False), ('network_name', False), ('port', False),
             ('port_name', False), ('ports', False), ('protocol', True),
             ('secure', False), ('url_path', False)],
            sorted([(p.name, p.required) for p in endpoint_props_def_objects]))

        os_props = self._get_capability_properties_def_objects(
            compute_type.get_capabilities_objects(),
            'tosca.capabilities.OperatingSystem')
        self.assertEqual(
            [('architecture', False), ('distribution', False), ('type', False),
             ('version', False)],
            sorted([(p.name, p.required) for p in os_props]))

        host_props = self._get_capability_properties_def_objects(
            compute_type.get_capabilities_objects(),
            'tosca.capabilities.Container')
        self.assertEqual(
            [('cpu_frequency', False), ('disk_size', False),
             ('mem_size', False), ('num_cpus', False)],
            sorted([(p.name, p.required) for p in host_props]))
        endpoint_admin_properties = 'secure'
        endpoint_admin_props_def_objects = \
            self._get_capability_properties_def_objects(
                webserver_type.get_capabilities_objects(),
                'tosca.capabilities.Endpoint.Admin')
        self.assertIn(
            endpoint_admin_properties,
            sorted([p.name for p in endpoint_admin_props_def_objects]))

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

    def test_properties_def(self):
        self.assertEqual(
            ['name', 'password', 'port', 'user'],
            sorted(database_type.get_properties_def().keys()))

    def test_attributes_def(self):
        self.assertEqual(
            ['networks', 'ports', 'private_address', 'public_address',
             'state', 'tosca_id', 'tosca_name'],
            sorted(compute_type.get_attributes_def().keys()))

    def test_requirements(self):
        self.assertEqual(
            [{'host': {'capability': 'tosca.capabilities.Container',
                       'node': 'tosca.nodes.Compute',
                       'relationship': 'tosca.relationships.HostedOn'}},
             {'dependency': {'capability': 'tosca.capabilities.Node',
                             'node': 'tosca.nodes.Root',
                             'occurrences': [0, 'UNBOUNDED'],
                             'relationship': 'tosca.relationships.DependsOn'}}
             ],
            [r for r in component_type.requirements])

    def test_relationship(self):
        self.assertEqual(
            [('tosca.relationships.DependsOn', 'tosca.nodes.Root'),
             ('tosca.relationships.HostedOn', 'tosca.nodes.Compute')],
            sorted([(relation.type, node.type) for
                   relation, node in component_type.relationship.items()]))
        self.assertIn(
            ('tosca.relationships.HostedOn', ['tosca.capabilities.Container']),
            [(relation.type, relation.valid_target_types) for
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
        self.assertIsNone(compute_type.interfaces)
        root_node = NodeType('tosca.nodes.Root')
        self.assertIn(ifaces.LIFECYCLE_SHORTNAME, root_node.interfaces)

    def test_artifacts(self):
        self.assertIsNone(artif_root_type.parent_type)
        self.assertEqual('tosca.artifacts.Root',
                         artif_file_type.parent_type.type)
        self.assertEqual({}, artif_file_type.parent_artifacts)
        self.assertEqual(sorted(['tosca.artifacts.Root'],
                                key=lambda x: str(x)),
                         sorted([artif_file_type.get_artifact(name)
                                for name in artif_file_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.artifacts.Implementation',
                         artif_bash_type.parent_type.type)
        self.assertEqual({'tosca.artifacts.Implementation':
                          {'derived_from': 'tosca.artifacts.Root',
                           'description':
                           'TOSCA base type for implementation artifacts'}},
                         artif_bash_type.parent_artifacts)
        self.assertEqual(sorted([['sh'], 'tosca.artifacts.Implementation',
                                 'Script artifact for the Unix Bash shell',
                                 'application/x-sh'], key=lambda x: str(x)),
                         sorted([artif_bash_type.get_artifact(name)
                                for name in artif_bash_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.artifacts.Implementation',
                         artif_python_type.parent_type.type)
        self.assertEqual({'tosca.artifacts.Implementation':
                          {'derived_from': 'tosca.artifacts.Root',
                           'description':
                           'TOSCA base type for implementation artifacts'}},
                         artif_python_type.parent_artifacts)
        self.assertEqual(sorted([['py'], 'tosca.artifacts.Implementation',
                                 'Artifact for the interpreted Python'
                                 ' language', 'application/x-python'],
                                key=lambda x: str(x)),
                         sorted([artif_python_type.get_artifact(name)
                                for name in artif_python_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.artifacts.Deployment.Image',
                         artif_container_docker_type.parent_type.type)
        self.assertEqual({'tosca.artifacts.Deployment':
                          {'derived_from': 'tosca.artifacts.Root',
                           'description':
                           'TOSCA base type for deployment artifacts'},
                          'tosca.artifacts.Deployment.Image':
                          {'derived_from': 'tosca.artifacts.Deployment'}},
                         artif_container_docker_type.parent_artifacts)
        self.assertEqual(sorted(['tosca.artifacts.Deployment.Image',
                                 'Docker container image'],
                                key=lambda x: str(x)),
                         sorted([artif_container_docker_type.
                                get_artifact(name) for name in
                                artif_container_docker_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.artifacts.Deployment.Image',
                         artif_vm_iso_type.parent_type.type)
        self.assertEqual({'tosca.artifacts.Deployment':
                          {'derived_from': 'tosca.artifacts.Root',
                           'description':
                           'TOSCA base type for deployment artifacts'},
                          'tosca.artifacts.Deployment.Image':
                          {'derived_from': 'tosca.artifacts.Deployment'}},
                         artif_vm_iso_type.parent_artifacts)
        self.assertEqual(sorted(['tosca.artifacts.Deployment.Image',
                                 'Virtual Machine (VM) image in '
                                 'ISO disk format',
                                 'application/octet-stream', ['iso']],
                                key=lambda x: str(x)),
                         sorted([artif_vm_iso_type.
                                get_artifact(name) for name in
                                artif_vm_iso_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.artifacts.Deployment.Image',
                         artif_vm_qcow2_type.parent_type.type)
        self.assertEqual({'tosca.artifacts.Deployment':
                          {'derived_from': 'tosca.artifacts.Root',
                           'description':
                           'TOSCA base type for deployment artifacts'},
                          'tosca.artifacts.Deployment.Image':
                          {'derived_from': 'tosca.artifacts.Deployment'}},
                         artif_vm_qcow2_type.parent_artifacts)
        self.assertEqual(sorted(['tosca.artifacts.Deployment.Image',
                                 'Virtual Machine (VM) image in QCOW v2 '
                                 'standard disk format',
                                 'application/octet-stream', ['qcow2']],
                                key=lambda x: str(x)),
                         sorted([artif_vm_qcow2_type.
                                get_artifact(name) for name in
                                artif_vm_qcow2_type.defs],
                                key=lambda x: str(x)))

    def test_policies(self):
        self.assertIsNone(policy_root_type.parent_type)
        self.assertEqual('tosca.policies.Root',
                         policy_placement_type.parent_type.type)
        self.assertEqual({}, policy_placement_type.parent_policies)
        self.assertEqual(sorted(['tosca.policies.Root',
                                 'The TOSCA Policy Type definition that is '
                                 'used to govern placement of TOSCA nodes or '
                                 'groups of nodes.'],
                                key=lambda x: str(x)),
                         sorted([policy_placement_type.get_policy(name)
                                for name in policy_placement_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.policies.Root',
                         policy_scaling_type.parent_type.type)
        self.assertEqual({}, policy_scaling_type.parent_policies)
        self.assertEqual(sorted(['tosca.policies.Root',
                                 'The TOSCA Policy Type definition that is '
                                 'used to govern scaling of TOSCA nodes or '
                                 'groups of nodes.'],
                                key=lambda x: str(x)),
                         sorted([policy_scaling_type.get_policy(name)
                                for name in policy_scaling_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.policies.Root',
                         policy_update_type.parent_type.type)
        self.assertEqual({}, policy_update_type.parent_policies)
        self.assertEqual(sorted(['tosca.policies.Root',
                                 'The TOSCA Policy Type definition that is '
                                 'used to govern update of TOSCA nodes or '
                                 'groups of nodes.'],
                                key=lambda x: str(x)),
                         sorted([policy_update_type.get_policy(name)
                                for name in policy_update_type.defs],
                                key=lambda x: str(x)))

        self.assertEqual('tosca.policies.Root',
                         policy_performance_type.parent_type.type)
        self.assertEqual({}, policy_performance_type.parent_policies)
        self.assertEqual(sorted(['tosca.policies.Root',
                                 'The TOSCA Policy Type definition that is '
                                 'used to declare performance requirements '
                                 'for TOSCA nodes or groups of nodes.'],
                                key=lambda x: str(x)),
                         sorted([policy_performance_type.get_policy(name)
                                for name in policy_performance_type.defs],
                                key=lambda x: str(x)))

    def test_port_spec(self):
        tosca_def = EntityType.TOSCA_DEF
        port_spec = tosca_def.get('tosca.datatypes.network.PortSpec')
        self.assertEqual(port_spec.get('derived_from'),
                         'tosca.datatypes.Root')
        properties = port_spec.get('properties')
        self.assertEqual(
            sorted(['protocol', 'target', 'target_range', 'source',
                    'source_range']),
            sorted(properties.keys()))
