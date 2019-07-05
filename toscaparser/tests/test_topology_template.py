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

from toscaparser.common import exception
from toscaparser.substitution_mappings import SubstitutionMappings
from toscaparser.tests.base import TestCase
from toscaparser.topology_template import TopologyTemplate
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils.gettextutils import _
import toscaparser.utils.yamlparser

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class TopologyTemplateTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        '''TOSCA template.'''
        self.tosca_tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/transactionsubsystem.yaml")
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

    def _get_custom_types(self):
        custom_types = {}
        def_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/definitions.yaml")
        custom_type = YAML_LOADER(def_file)
        node_types = custom_type['node_types']
        for name in node_types:
            defintion = node_types[name]
            custom_types[name] = defintion
        return custom_types

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
        expected_capabilities = ['app_endpoint', 'feature', 'message_receiver']
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
            sorted(['receiver_ip', 'receiver_port']),
            sorted([output.name for output in self.topo.outputs]))

    def test_groups(self):
        group = self.topo.groups[0]
        self.assertEqual('webserver_group', group.name)
        self.assertEqual(['websrv', 'server'], group.members)
        for node in group.get_member_nodes():
            if node.name == 'server':
                '''Test property value'''
                props = node.get_properties()
                if props and 'mem_size' in props.keys():
                    self.assertEqual(props['mem_size'].value, '4096 MB')

    def test_system_template(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/system.yaml")
        system_tosca_template = ToscaTemplate(tpl_path)
        self.assertIsNotNone(system_tosca_template)
        self.assertEqual(
            len(system_tosca_template.
                nested_tosca_templates_with_topology), 4)
        self.assertTrue(system_tosca_template.has_nested_templates())

    def test_invalid_keyname(self):
        tpl_snippet = '''
        substitution_mappings:
          node_type: example.DatabaseSubsystem
          capabilities:
            database_endpoint: [ db_app, database_endpoint ]
          requirements:
            receiver1: [ tran_app, receiver1 ]
          invalid_key: 123
        '''
        sub_mappings = (toscaparser.utils.yamlparser.
                        simple_parse(tpl_snippet))['substitution_mappings']
        expected_message = _(
            'SubstitutionMappings contains unknown field '
            '"invalid_key". Refer to the definition '
            'to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: SubstitutionMappings(sub_mappings, None, None,
                                         None, None, None))
        self.assertEqual(expected_message, err.__str__())

    def test_missing_required_keyname(self):
        tpl_snippet = '''
        substitution_mappings:
          capabilities:
            database_endpoint: [ db_app, database_endpoint ]
          requirements:
            receiver1: [ tran_app, receiver1 ]
        '''
        sub_mappings = (toscaparser.utils.yamlparser.
                        simple_parse(tpl_snippet))['substitution_mappings']
        expected_message = _('SubstitutionMappings used in topology_template '
                             'is missing required field "node_type".')
        err = self.assertRaises(
            exception.MissingRequiredFieldError,
            lambda: SubstitutionMappings(sub_mappings, None, None,
                                         None, None, None))
        self.assertEqual(expected_message, err.__str__())

    def test_invalid_nodetype(self):
        tpl_snippet = '''
        substitution_mappings:
          node_type: example.DatabaseSubsystem1
          capabilities:
            database_endpoint: [ db_app, database_endpoint ]
          requirements:
            receiver1: [ tran_app, receiver1 ]
        '''
        sub_mappings = (toscaparser.utils.yamlparser.
                        simple_parse(tpl_snippet))['substitution_mappings']
        custom_defs = self._get_custom_types()
        expected_message = _('Node type "example.DatabaseSubsystem1" '
                             'is not a valid type.')
        err = self.assertRaises(
            exception.InvalidNodeTypeError,
            lambda: SubstitutionMappings(sub_mappings, None, None,
                                         None, None, custom_defs))
        self.assertEqual(expected_message, err.__str__())

    def test_system_with_input_validation(self):
        tpl_path0 = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/validate/system_invalid_input.yaml")
        tpl_path1 = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/validate/"
            "queuingsubsystem_invalid_input.yaml")
        errormsg = _('SubstitutionMappings with node_type '
                     'example.QueuingSubsystem is missing '
                     'required input definition of input "server_port".')

        # It's invalid in nested template.
        self.assertRaises(exception.ValidationError,
                          lambda: ToscaTemplate(tpl_path0))
        exception.ExceptionCollector.assertExceptionMessage(
            exception.MissingRequiredInputError, errormsg)

        # Subtemplate deploy standaolone is also invalid.
        self.assertRaises(exception.ValidationError,
                          lambda: ToscaTemplate(tpl_path1))
        exception.ExceptionCollector.assertExceptionMessage(
            exception.MissingRequiredInputError, errormsg)

    def test_substitution_mappings_valid_output(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/validate/"
            "test_substitution_mappings_valid_output.yaml")
        self.assertIsNotNone(ToscaTemplate(tpl_path))

    def test_system_with_unknown_output_validation(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/topology_template/validate/"
            "test_substitution_mappings_invalid_output.yaml")
        errormsg = _('\'Attribute "my_cpu_output" was not found in node '
                     'template "substitute_app".\'')
        self.assertRaises(exception.ValidationError,
                          lambda: ToscaTemplate(tpl_path))
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError, errormsg)

    def test_invalid_type_policies(self):
        tpl_snippet = '''
        policies:
           some_policy:
              type: tosca.policies.Placement
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('policies must be of type "list".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_groups(self):
        tpl_snippet = '''
        groups:
           - some_group:
              type: tosca.groups.Root
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('groups must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_substitution_mappings(self):
        tpl_snippet = '''
        substitution_mappings:
           - node_type: MyService
             properties:
               num_cpus: cpus
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('substitution_mappings must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_outputs(self):
        tpl_snippet = '''
        outputs:
           - some_output:
               value: some_value
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('outputs must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_relationship_templates(self):
        tpl_snippet = '''
        relationship_templates:
           - my_connection:
                type: ConnectsTo
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('relationship_templates must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_nodetemplates(self):
        tpl_snippet = '''
        node_templates:
           - some_node:
               type: tosca.nodes.Compute
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('node_templates must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())

    def test_invalid_type_inputs(self):
        tpl_snippet = '''
        inputs:
           - some_input:
               type: integer
               value: 1
        '''
        policies = (toscaparser.utils.yamlparser.simple_parse(tpl_snippet))
        custom_defs = self._get_custom_types()
        err = self.assertRaises(exception.TypeMismatchError,
                                lambda: TopologyTemplate(policies,
                                                         custom_defs))
        errormsg = _('inputs must be of type "dict".')
        self.assertEqual(errormsg, err.__str__())
