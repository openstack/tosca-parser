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

import os

from toscaparser.tests.base import TestCase
from toscaparser.topology_template import TopologyTemplate
import toscaparser.utils.yamlparser

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class TopologyTemplateTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        '''TOSCA template.'''
        self.tosca_tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/subsystem.yaml")
        self.tpl = YAML_LOADER(self.tosca_tpl_path)
        self.topo_tpl = self.tpl.get('topology_template')
        self.imports = self.tpl.get('imports')
        self.topo = TopologyTemplate(self.topo_tpl,
                                     self._get_all_custom_def())

    def _get_custom_def(self, type_definition):
        custom_defs = {}
        for definition in self.imports:
            if os.path.isabs(definition):
                def_file = definition
            else:
                tpl_dir = os.path.dirname(os.path.abspath(self.tosca_tpl_path))
                def_file = os.path.join(tpl_dir, definition)
            custom_type = YAML_LOADER(def_file)
            custom_defs.update(custom_type.get(type_definition))
        return custom_defs

    def _get_all_custom_def(self):
        custom_defs = {}
        custom_defs.update(self._get_custom_def('node_types'))
        custom_defs.update(self._get_custom_def('capability_types'))
        return custom_defs

    def test_description(self):
        expected_desc = 'Template of a database including its hosting stack.'
        self.assertEqual(expected_desc, self.topo.description)

    def test_inputs(self):
        self.assertEqual(
            ['mq_server_ip', 'my_cpus', 'receiver_port'],
            sorted([input.name for input in self.topo.inputs]))

        input_name = "receiver_port"
        expected_description = "Port to be used for receiving messages."
        for input in self.topo.inputs:
            if input.name == input_name:
                self.assertEqual(expected_description, input.description)

    def test_node_tpls(self):
        '''Test nodetemplate names.'''
        self.assertEqual(
            ['app', 'server', 'websrv'],
            sorted([tpl.name for tpl in self.topo.nodetemplates]))

        tpl_name = "app"
        expected_type = "example.SomeApp"
        expected_properties = ['admin_user', 'pool_size']
        expected_capabilities = ['message_receiver']
        expected_requirements = [{'host': {'node': 'websrv'}}]
        expected_relationshp = ['tosca.relationships.HostedOn']
        expected_host = ['websrv']
        for tpl in self.topo.nodetemplates:
            if tpl_name == tpl.name:
                '''Test node type.'''
                self.assertEqual(tpl.type, expected_type)

                '''Test properties.'''
                self.assertEqual(
                    expected_properties,
                    sorted(tpl.get_properties().keys()))

                '''Test capabilities.'''
                self.assertEqual(
                    expected_capabilities,
                    sorted(tpl.get_capabilities().keys()))

                '''Test requirements.'''
                self.assertEqual(
                    expected_requirements, tpl.requirements)

                '''Test relationship.'''
                ''' TODO : skip tempororily. need to fix it
                '''
                self.assertEqual(
                    expected_relationshp,
                    [x.type for x in tpl.relationships.keys()])
                self.assertEqual(
                    expected_host,
                    [y.name for y in tpl.relationships.values()])
                '''Test interfaces.'''
                # TODO(hurf) add interface test when new template is available

            if tpl.name == 'server':
                '''Test property value'''
                props = tpl.get_properties()
                if props and 'mem_size' in props.keys():
                    self.assertEqual(props['mem_size'].value, '4096 MB')
                '''Test capability'''
                caps = tpl.get_capabilities()
                self.assertIn('os', caps.keys())
                os_props_objs = None
                os_props = None
                os_type_prop = None
                if caps and 'os' in caps.keys():
                    capability = caps['os']
                    os_props_objs = capability.get_properties_objects()
                    os_props = capability.get_properties()
                    os_type_prop = capability.get_property_value('type')
                    break
                self.assertEqual(
                    ['Linux'],
                    [p.value for p in os_props_objs if p.name == 'type'])
                self.assertEqual(
                    'Linux',
                    os_props['type'].value if 'type' in os_props else '')
                self.assertEqual('Linux', os_props['type'].value)
                self.assertEqual('Linux', os_type_prop)

    def test_outputs(self):
        self.assertEqual(
            ['receiver_ip'],
            sorted([output.name for output in self.topo.outputs]))

    def test_groups(self):
        group = self.topo.groups[0]
        self.assertEqual('webserver_group', group.name)
        self.assertEqual(['websrv', 'server'], group.member_names)
        for node in group.members:
            if node.name == 'server':
                '''Test property value'''
                props = node.get_properties()
                if props and 'mem_size' in props.keys():
                    self.assertEqual(props['mem_size'].value, '4096 MB')
