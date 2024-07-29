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
import requests
from unittest import mock
import urllib

from toscaparser.common import exception
import toscaparser.elements.interfaces as ifaces
from toscaparser.elements.nodetype import NodeType
from toscaparser.elements.portspectype import PortSpec
from toscaparser.functions import GetInput
from toscaparser.functions import GetProperty
from toscaparser.nodetemplate import NodeTemplate
from toscaparser.tests.base import MockTestClass
from toscaparser.tests.base import TestCase
from toscaparser.tests import utils
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils.gettextutils import _
from toscaparser.utils.urlutils import UrlUtils
import toscaparser.utils.yamlparser


class ToscaTemplateTest(TestCase):
    '''TOSCA template.'''
    tosca_tpl = utils.get_sample_test_path(
        "data/tosca_single_instance_wordpress.yaml")
    params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
              'db_root_pwd': '12345678'}
    tosca = ToscaTemplate(tosca_tpl, parsed_params=params)
    tosca_elk_tpl = utils.get_sample_test_path("data/tosca_elk.yaml")
    tosca_repo_tpl = utils.get_sample_test_path(
        "data/repositories/tosca_repositories_test_definition.yaml")

    def test_version(self):
        self.assertEqual(self.tosca.version, "tosca_simple_yaml_1_0")

    def test_description(self):
        expected_description = "TOSCA simple profile with wordpress, " \
                               "web server and mysql on the same server."
        self.assertEqual(self.tosca.description, expected_description)

    def test_inputs(self):
        self.assertEqual(
            ['cpus', 'db_name', 'db_port',
             'db_pwd', 'db_root_pwd', 'db_user'],
            sorted([input.name for input in self.tosca.inputs]))

        input_name = "db_port"
        expected_description = "Port for the MySQL database."
        for input in self.tosca.inputs:
            if input.name == input_name:
                self.assertEqual(input.description, expected_description)

    def test_node_tpls(self):
        '''Test nodetemplate names.'''
        self.assertEqual(
            ['mysql_database', 'mysql_dbms', 'server',
             'webserver', 'wordpress'],
            sorted([tpl.name for tpl in self.tosca.nodetemplates]))

        tpl_name = "mysql_database"
        expected_type = "tosca.nodes.Database"
        expected_properties = ['name', 'password', 'user']
        expected_capabilities = ['database_endpoint', 'feature']
        expected_requirements = [{'host': 'mysql_dbms'}]
        ''' TODO: needs enhancement in tosca_elk.yaml..
        expected_relationshp = ['tosca.relationships.HostedOn']
        expected_host = ['mysql_dbms']
        '''
        expected_interface = [ifaces.LIFECYCLE_SHORTNAME]

        for tpl in self.tosca.nodetemplates:
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
                ''' needs enhancements in tosca_elk.yaml
                self.assertEqual(
                    expected_relationshp,
                    [x.type for x in tpl.relationships.keys()])
                self.assertEqual(
                    expected_host,
                    [y.name for y in tpl.relationships.values()])
                '''
                '''Test interfaces.'''
                self.assertEqual(
                    expected_interface,
                    [x.type for x in tpl.interfaces])

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

    def test_node_inheritance_type(self):
        wordpress_node = [
            node for node in self.tosca.nodetemplates
            if node.name == 'wordpress'][0]
        self.assertTrue(
            wordpress_node.is_derived_from("tosca.nodes.WebApplication"))
        self.assertTrue(
            wordpress_node.is_derived_from("tosca.nodes.Root"))
        self.assertFalse(
            wordpress_node.is_derived_from("tosca.policies.Root"))

    def test_nodetype_without_relationship(self):
        # Nodes that contain "relationship" in "requirements"
        depend_node_types = (
            "tosca.nodes.SoftwareComponent",
        )

        # Nodes that do not contain "relationship" in "requirements"
        non_depend_node_types = (
            "tosca.nodes.Compute",
            "sample.SC",
        )

        tosca_tpl = utils.get_sample_test_path(
            "data/test_nodetype_without_relationship.yaml")
        tosca = ToscaTemplate(tosca_tpl)

        nodetemplates = tosca.nodetemplates
        for node in nodetemplates:
            node_depend = node.related_nodes
            if node_depend:
                self.assertIn(
                    node.type,
                    depend_node_types
                )
            else:
                self.assertIn(
                    node.type,
                    non_depend_node_types
                )

    def test_outputs(self):
        self.assertEqual(
            ['website_url'],
            sorted([output.name for output in self.tosca.outputs]))

    def test_interfaces(self):
        wordpress_node = [
            node for node in self.tosca.nodetemplates
            if node.name == 'wordpress'][0]
        interfaces = wordpress_node.interfaces
        self.assertEqual(2, len(interfaces))
        for interface in interfaces:
            if interface.name == 'create':
                self.assertEqual(ifaces.LIFECYCLE_SHORTNAME,
                                 interface.type)
                self.assertEqual('wordpress/wordpress_install.sh',
                                 interface.implementation)
                self.assertIsNone(interface.inputs)
            elif interface.name == 'configure':
                self.assertEqual(ifaces.LIFECYCLE_SHORTNAME,
                                 interface.type)
                self.assertEqual('wordpress/wordpress_configure.sh',
                                 interface.implementation)
                self.assertEqual(3, len(interface.inputs))
                self.skipTest('bug #1440247')
                wp_db_port = interface.inputs['wp_db_port']
                self.assertIsInstance(wp_db_port, GetProperty)
                self.assertEqual('get_property', wp_db_port.name)
                self.assertEqual(['SELF',
                                  'database_endpoint',
                                  'port'],
                                 wp_db_port.args)
                result = wp_db_port.result()
                self.assertIsInstance(result, GetInput)
            else:
                raise AssertionError(
                    'Unexpected interface: {0}'.format(interface.name))

    def test_normative_type_by_short_name(self):
        # test template with a short name Compute
        template = utils.get_sample_test_path(
            "data/test_tosca_normative_type_by_shortname.yaml")

        tosca_tpl = ToscaTemplate(template)
        expected_type = "tosca.nodes.Compute"
        for tpl in tosca_tpl.nodetemplates:
            self.assertEqual(tpl.type, expected_type)
        for tpl in tosca_tpl.nodetemplates:
            compute_type = NodeType(tpl.type)
            self.assertEqual(
                sorted(['tosca.capabilities.Container',
                        'tosca.capabilities.Endpoint.Admin',
                        'tosca.capabilities.Node',
                        'tosca.capabilities.OperatingSystem',
                        'tosca.capabilities.network.Bindable',
                        'tosca.capabilities.Scalable']),
                sorted([c.type
                        for c in compute_type.get_capabilities_objects()]))

    def test_template_with_no_inputs(self):
        tosca_tpl = self._load_template('test_no_inputs_in_template.yaml')
        self.assertEqual(0, len(tosca_tpl.inputs))

    def test_template_with_no_outputs(self):
        tosca_tpl = self._load_template('test_no_outputs_in_template.yaml')
        self.assertEqual(0, len(tosca_tpl.outputs))

    def test_template_file_with_suffix_yml(self):
        tosca_tpl = self._load_template('custom_types/wordpress.yml')
        self.assertIsNotNone(tosca_tpl)

    def test_relationship_interface(self):
        template = ToscaTemplate(self.tosca_elk_tpl)
        for node_tpl in template.nodetemplates:
            if node_tpl.name == 'logstash':
                config_interface = 'Configure'
                artifact = 'logstash/configure_elasticsearch.py'
                relation = node_tpl.relationships
                for key in relation.keys():
                    rel_tpl = relation.get(key).get_relationship_template()
                    if rel_tpl:
                        self.assertTrue(rel_tpl[0].is_derived_from(
                            "tosca.relationships.Root"))
                        interfaces = rel_tpl[0].interfaces
                        for interface in interfaces:
                            self.assertEqual(config_interface,
                                             interface.type)
                            self.assertEqual('pre_configure_source',
                                             interface.name)
                            self.assertEqual(artifact,
                                             interface.implementation)

    def test_relationship(self):
        template = ToscaTemplate(self.tosca_elk_tpl)
        for node_tpl in template.nodetemplates:
            if node_tpl.name == 'paypal_pizzastore':
                expected_relationships = ['tosca.relationships.ConnectsTo',
                                          'tosca.relationships.HostedOn']
                expected_hosts = ['tosca.nodes.Database',
                                  'tosca.nodes.WebServer']
                self.assertEqual(len(node_tpl.relationships), 2)
                self.assertEqual(
                    expected_relationships,
                    sorted([k.type for k in node_tpl.relationships.keys()]))
                self.assertEqual(
                    expected_hosts,
                    sorted([v.type for v in node_tpl.relationships.values()]))

    def test_repositories(self):
        template = ToscaTemplate(self.tosca_repo_tpl)
        self.assertEqual(
            ['repo_code0', 'repo_code1', 'repo_code2'],
            sorted([input.name for input in template.repositories]))

        input_name = "repo_code2"
        expected_url = "https://github.com/nandinivemula/intern/master"
        for input in template.repositories:
            if input.name == input_name:
                self.assertEqual(input.url, expected_url)

    def test_template_macro(self):
        template = ToscaTemplate(self.tosca_elk_tpl)
        for node_tpl in template.nodetemplates:
            if node_tpl.name == 'mongo_server':
                self.assertEqual(
                    ['disk_size', 'mem_size', 'num_cpus'],
                    sorted(node_tpl.get_capability('host').
                           get_properties().keys()))

    def test_template_requirements(self):
        """Test different formats of requirements

        The requirements can be defined in few different ways,
        1. Requirement expressed as a capability with an implicit relationship.
        2. Requirement expressed with explicit relationship.
        3. Requirement expressed with a relationship template.
        4. Requirement expressed via TOSCA types to provision a node
           with explicit relationship.
        5. Requirement expressed via TOSCA types with a filter.
        """
        tosca_tpl = utils.get_sample_test_path(
            "data/requirements/test_requirements.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        for node_tpl in tosca.nodetemplates:
            if node_tpl.name == 'my_app':
                expected_relationship = [
                    ('tosca.relationships.ConnectsTo', 'mysql_database'),
                    ('tosca.relationships.HostedOn', 'my_webserver')]
                actual_relationship = sorted([
                    (relation.type, node.name) for
                    relation, node in node_tpl.relationships.items()])
                self.assertEqual(expected_relationship, actual_relationship)
            if node_tpl.name == 'mysql_database':
                self.assertEqual(
                    [('tosca.relationships.HostedOn', 'my_dbms')],
                    [(relation.type, node.name) for
                     relation,
                     node in node_tpl.relationships.items()])
            if node_tpl.name == 'my_server':
                self.assertEqual(
                    [('tosca.relationships.AttachesTo', 'my_storage')],
                    [(relation.type, node.name) for
                     relation,
                     node in node_tpl.relationships.items()])

    def test_template_requirements_not_implemented(self):
        # TODO(spzala): replace this test with new one once TOSCA types look up
        # support is implemented.
        """Requirements that yet need to be implemented

        The following requirement formats are not yet implemented,
        due to look up dependency:
        1. Requirement expressed via TOSCA types to provision a node
           with explicit relationship.
        2. Requirement expressed via TOSCA types with a filter.
        """
        tpl_snippet_1 = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            description: Requires a particular node type and relationship.
                        To be full-filled via lookup into node repository.
            requirements:
              - req1:
                  node: tosca.nodes.DBMS
                  relationship: tosca.relationships.HostedOn
        '''

        tpl_snippet_2 = '''
        node_templates:
          my_webserver:
            type: tosca.nodes.WebServer
            description: Requires a particular node type with a filter.
                         To be full-filled via lookup into node repository.
            requirements:
              - req1:
                  node: tosca.nodes.Compute
                  target_filter:
                    properties:
                      num_cpus: { in_range: [ 1, 4 ] }
                      mem_size: { greater_or_equal: 2 }
                    capabilities:
                      - tosca.capabilities.OS:
                          properties:
                            architecture: x86_64
                            type: linux
        '''

        tpl_snippet_3 = '''
        node_templates:
          my_webserver2:
            type: tosca.nodes.WebServer
            description: Requires a node type with a particular capability.
                         To be full-filled via lookup into node repository.
            requirements:
              - req1:
                  node: tosca.nodes.Compute
                  relationship: tosca.relationships.HostedOn
                  capability: tosca.capabilities.Container
        '''
        self._requirements_not_implemented(tpl_snippet_1, 'mysql_database')
        self._requirements_not_implemented(tpl_snippet_2, 'my_webserver')
        self._requirements_not_implemented(tpl_snippet_3, 'my_webserver2')

    def _requirements_not_implemented(self, tpl_snippet, tpl_name):
        nodetemplates = (toscaparser.utils.yamlparser.
                         simple_parse(tpl_snippet))['node_templates']
        self.assertRaises(
            NotImplementedError,
            lambda: NodeTemplate(tpl_name, nodetemplates).relationships)

    # Test the following:
    # 1. Custom node type derived from 'WebApplication' named 'TestApp'
    #    with a custom Capability Type 'TestCapability'
    # 2. Same as #1, but referencing a custom 'TestCapability' Capability Type
    #    that is not defined
    def test_custom_capability_type_definition(self):
        tpl_snippet = '''
        node_templates:
          test_app:
            type: tosca.nodes.WebApplication.TestApp
            capabilities:
              test_cap:
                properties:
                  test: 1
        '''
        # custom node type definition with custom capability type definition
        custom_def = '''
        tosca.nodes.WebApplication.TestApp:
          derived_from: tosca.nodes.WebApplication
          capabilities:
            test_cap:
               type: tosca.capabilities.TestCapability
        tosca.capabilities.TestCapability:
          derived_from: tosca.capabilities.Root
          properties:
            test:
              type: integer
              required: false
        '''
        expected_capabilities = ['app_endpoint', 'feature', 'test_cap']
        nodetemplates = (toscaparser.utils.yamlparser.
                         simple_parse(tpl_snippet))['node_templates']
        custom_def = (toscaparser.utils.yamlparser.
                      simple_parse(custom_def))
        name = list(nodetemplates.keys())[0]
        tpl = NodeTemplate(name, nodetemplates, custom_def)
        self.assertEqual(
            expected_capabilities,
            sorted(tpl.get_capabilities().keys()))

        # custom definition without valid capability type definition
        custom_def = '''
        tosca.nodes.WebApplication.TestApp:
          derived_from: tosca.nodes.WebApplication
          capabilities:
            test_cap:
               type: tosca.capabilities.TestCapability
        '''
        custom_def = (toscaparser.utils.yamlparser.
                      simple_parse(custom_def))
        tpl = NodeTemplate(name, nodetemplates, custom_def)
        err = self.assertRaises(
            exception.InvalidTypeError,
            lambda: NodeTemplate(name, nodetemplates,
                                 custom_def).get_capabilities_objects())
        self.assertEqual('Type "tosca.capabilities.TestCapability" is not '
                         'a valid type.', str(err))

    def test_capability_without_properties(self):
        expected_version = "tosca_simple_yaml_1_0"
        expected_description = \
            "Test resources for which properties are not defined in "\
            "the parent of capabilitytype. "\
            "TestApp has capabilities->test_cap, "\
            "and the type of test_cap is TestCapabilityAA. "\
            "The parents of TestCapabilityAA is TestCapabilityA, "\
            "and TestCapabilityA has no properties."
        expected_nodetemplates = {
            "test_app": {
                "type": "tosca.nodes.WebApplication.TestApp",
                "capabilities": {
                    "test_cap": {
                        "properties": {
                            "test": 1
                        }
                    }
                }
            }
        }

        tosca_tpl = utils.get_sample_test_path(
            "data/test_capability_without_properties.yaml")
        tosca = ToscaTemplate(tosca_tpl)

        self.assertEqual(expected_version, tosca.version)
        self.assertEqual(expected_description, tosca.description)
        self.assertEqual(
            expected_nodetemplates,
            tosca.nodetemplates[0].templates,
        )

    def test_local_template_with_local_relpath_import(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress.yaml")
        params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
                  'db_root_pwd': '12345678'}
        tosca = ToscaTemplate(tosca_tpl, parsed_params=params)
        self.assertTrue(tosca.topology_template.custom_defs)

    @mock.patch.object(ToscaTemplate, '_tpl_imports')
    def test_local_template_with_url_import(self, mock_tpl_imports):
        tosca_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress_with_url_import.yaml")
        import_file_path = utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")
        mock_tpl_imports.return_value = [import_file_path]
        tosca = ToscaTemplate(tosca_tpl,
                              parsed_params={'db_root_pwd': '123456'})
        self.assertTrue(tosca.topology_template.custom_defs)

    @mock.patch.object(urllib.request, 'urlopen')
    def test_url_template_with_local_relpath_import(self, mock_urlopen):
        tosca_tpl = ('https://example.com/tosca_single_instance_'
                     'wordpress.yaml')
        mock_path = 'https://example.com/custom_types/wordpress.yaml'

        mockclass = MockTestClass()
        mockclass.comp_urldict = {tosca_tpl: utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress.yaml"),
            mock_path: utils.get_sample_test_path(
                "data/custom_types/wordpress.yaml")}
        mock_urlopen.side_effect = mockclass.mock_urlopen_method
        tosca = ToscaTemplate(tosca_tpl, a_file=False,
                              parsed_params={"db_name": "mysql",
                                             "db_user": "mysql",
                                             "db_root_pwd": "1234",
                                             "db_pwd": "5678",
                                             "db_port": 3306,
                                             "cpus": 4})
        self.assertTrue(tosca.topology_template.custom_defs)

    @mock.patch.object(urllib.request, 'urlopen')
    def test_url_template_with_local_abspath_import(self, mock_urlopen):
        tosca_tpl = ('https://example.com/tosca_single_instance_wordpress_'
                     'with_local_abspath_import.yaml')

        mockclass = MockTestClass()
        mockclass.comp_urldict = {tosca_tpl: utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress_with_local_abspath_"
            "import.yaml")}
        mock_urlopen.side_effect = mockclass.mock_urlopen_method
        self.assertRaises(exception.ValidationError, ToscaTemplate, tosca_tpl,
                          None, False)
        err_msg = (_('Absolute file name "/tmp/tosca-parser/toscaparser/tests'
                     '/data/custom_types/wordpress.yaml" cannot be used in a '
                     'URL-based input template "%(tpl)s".')
                   % {'tpl': tosca_tpl})
        exception.ExceptionCollector.assertExceptionMessage(ImportError,
                                                            err_msg)

    @mock.patch.object(UrlUtils, 'join_url')
    @mock.patch.object(os.path, 'isabs')
    @mock.patch.object(ToscaTemplate, '_tpl_imports')
    @mock.patch.object(urllib.request, 'urlopen')
    def test_url_template_with_url_import(
            self, mock_urlopen, mock_tpl_imports, mock_isabs, mock_join_url):
        tosca_tpl = ('https://example.com/tosca_single_instance_wordpress_'
                     'with_url_import.yaml')

        mockclass = MockTestClass()
        mockclass.comp_urldict = {tosca_tpl: utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress_with_url_import.yaml")}
        mock_urlopen.side_effect = mockclass.mock_urlopen_method

        import_file_path = utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")
        mock_tpl_imports.return_value = [import_file_path]
        mock_isabs.return_value = False
        mock_join_url.return_value = import_file_path

        tosca = ToscaTemplate(tosca_tpl, a_file=False,
                              parsed_params={"db_root_pwd": "1234"})
        self.assertTrue(tosca.topology_template.custom_defs)

    def test_csar_parsing_wordpress(self):
        csar_archive = utils.get_sample_test_path(
            "data/CSAR/csar_wordpress.zip")
        self.assertTrue(ToscaTemplate(csar_archive,
                                      parsed_params={"db_name": "mysql",
                                                     "db_user": "mysql",
                                                     "db_root_pwd": "1234",
                                                     "db_pwd": "5678",
                                                     "db_port": 3306,
                                                     "cpus": 4}))

    @mock.patch.object(requests, 'get')
    def test_csar_parsing_elk_url_based(self, mock_requests_get):
        csar_archive = 'https://example.com/csar_elk.zip'

        class TestResponse:
            content: bytes

        response = TestResponse()
        file_path = utils.get_sample_test_path("data/CSAR/csar_elk.zip")

        with open(file_path, 'br') as f:
            response.content = f.read()
        f.close()

        mock_requests_get.return_value = response
        self.assertTrue(ToscaTemplate(csar_archive, a_file=False,
                                      parsed_params={"my_cpus": 4}))

    def test_nested_imports_in_templates(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_instance_nested_imports.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        expected_custom_types = ['tosca.nodes.SoftwareComponent.Kibana',
                                 'tosca.nodes.WebApplication.WordPress',
                                 'test_namespace_prefix.Rsyslog',
                                 'Test2ndRsyslogType',
                                 'test_2nd_namespace_prefix.Rsyslog',
                                 'tosca.nodes.SoftwareComponent.Logstash',
                                 'tosca.nodes.SoftwareComponent.Rsyslog.'
                                 'TestRsyslogType']
        self.assertCountEqual(tosca.topology_template.custom_defs.keys(),
                              expected_custom_types)

    def test_invalid_template_file(self):
        template_file = 'invalid template file'
        expected_msg = (_('"%s" is not a valid file.') % template_file)
        self.assertRaises(
            exception.ValidationError,
            ToscaTemplate, template_file, None, False)
        exception.ExceptionCollector.assertExceptionMessage(ValueError,
                                                            expected_msg)

    def test_multiple_validation_errors(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_multiple_validation_errors.yaml")
        self.assertRaises(exception.ValidationError, ToscaTemplate, tosca_tpl,
                          None)
        valid_versions = '", "'.join(ToscaTemplate.VALID_TEMPLATE_VERSIONS)
        err1_msg = (_('The template version "tosca_simple_yaml_1" is invalid. '
                      'Valid versions are "%s".') % valid_versions)
        exception.ExceptionCollector.assertExceptionMessage(
            exception.InvalidTemplateVersion, err1_msg)

        err2_msg = _('Import "custom_types/not_there.yaml" is not valid.')
        exception.ExceptionCollector.assertExceptionMessage(
            ImportError, err2_msg)

        err3_msg = _('Type "tosca.nodes.WebApplication.WordPress" is not a '
                     'valid type.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.InvalidTypeError, err3_msg)

        err4_msg = _('Node template "wordpress" contains unknown field '
                     '"requirement". Refer to the definition to verify valid '
                     'values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err4_msg)

        err5_msg = _('\'Property "passwords" was not found in node template '
                     '"mysql_database".\'')
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError, err5_msg)

        err6_msg = _('Template "mysql_dbms" is missing required field "type".')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.MissingRequiredFieldError, err6_msg)

        err7_msg = _('Node template "mysql_dbms" contains unknown field '
                     '"type1". Refer to the definition to verify valid '
                     'values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err7_msg)

        err8_msg = _('\'Node template "server1" was not found in '
                     '"webserver".\'')
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError, err8_msg)

        err9_msg = _('"relationship" used in template "webserver" is missing '
                     'required field "type".')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.MissingRequiredFieldError, err9_msg)

        err10_msg = _('Type "tosca.nodes.XYZ" is not a valid type.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.InvalidTypeError, err10_msg)

    def test_invalid_section_names(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_invalid_section_names.yaml")
        self.assertRaises(exception.ValidationError, ToscaTemplate, tosca_tpl,
                          None)
        err1_msg = _('Template contains unknown field '
                     '"tosca_definitions_versions". Refer to the definition '
                     'to verify valid values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err1_msg)

        err2_msg = _('Template contains unknown field "descriptions". '
                     'Refer to the definition to verify valid values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err2_msg)

        err3_msg = _('Template contains unknown field "import". Refer to '
                     'the definition to verify valid values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err3_msg)

        err4_msg = _('Template contains unknown field "topology_templates". '
                     'Refer to the definition to verify valid values.')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownFieldError, err4_msg)

    def test_csar_with_alternate_extenstion(self):
        tosca_tpl = utils.get_sample_test_path("data/CSAR/csar_elk.csar")
        tosca = ToscaTemplate(tosca_tpl, parsed_params={"my_cpus": 2})
        self.assertTrue(tosca.topology_template.custom_defs)

    def test_available_rel_tpls(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_available_rel_tpls.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        for node in tosca.nodetemplates:
            for relationship, target in node.relationships.items():
                try:
                    target.relationships
                except TypeError as error:
                    self.fail(error)

    def test_no_input(self):
        self.assertRaises(exception.ValidationError, ToscaTemplate, None,
                          None, False, None)
        err_msg = (('No path or yaml_dict_tpl was provided. '
                    'There is nothing to parse.'))
        exception.ExceptionCollector.assertExceptionMessage(ValueError,
                                                            err_msg)

    def test_path_and_yaml_dict_tpl_input(self):
        test_tpl = utils.get_sample_test_path("data/tosca_helloworld.yaml")

        yaml_dict_tpl = toscaparser.utils.yamlparser.load_yaml(test_tpl)

        tosca = ToscaTemplate(test_tpl, yaml_dict_tpl=yaml_dict_tpl)

        self.assertEqual(tosca.version, "tosca_simple_yaml_1_0")

    def test_yaml_dict_tpl_input(self):
        test_tpl = utils.get_sample_test_path("data/tosca_helloworld.yaml")

        yaml_dict_tpl = toscaparser.utils.yamlparser.load_yaml(test_tpl)

        tosca = ToscaTemplate(yaml_dict_tpl=yaml_dict_tpl)

        self.assertEqual(tosca.version, "tosca_simple_yaml_1_0")

    @mock.patch.object(ToscaTemplate, '_tpl_imports')
    def test_yaml_dict_tpl_with_params_and_url_import(self, mock_tpl_imports):
        test_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress_with_url_import.yaml")

        yaml_dict_tpl = toscaparser.utils.yamlparser.load_yaml(test_tpl)

        params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
                  'db_root_pwd': 'mypasswd'}
        import_file_path = utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")
        mock_tpl_imports.return_value = [import_file_path]

        tosca = ToscaTemplate(parsed_params=params,
                              yaml_dict_tpl=yaml_dict_tpl)

        self.assertEqual(tosca.version, "tosca_simple_yaml_1_0")

    def test_yaml_dict_tpl_with_rel_import(self):
        test_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress.yaml")

        yaml_dict_tpl = toscaparser.utils.yamlparser.load_yaml(test_tpl)
        params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
                  'db_root_pwd': '12345678'}
        self.assertRaises(exception.ValidationError, ToscaTemplate, None,
                          params, False, yaml_dict_tpl)
        err_msg = (_('Relative file name "custom_types/wordpress.yaml" '
                     'cannot be used in a pre-parsed input template.'))
        exception.ExceptionCollector.assertExceptionMessage(ImportError,
                                                            err_msg)

    def test_yaml_dict_tpl_with_fullpath_import(self):
        test_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress.yaml")

        yaml_dict_tpl = toscaparser.utils.yamlparser.load_yaml(test_tpl)

        yaml_dict_tpl['imports'] = [utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")]

        params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
                  'db_root_pwd': 'mypasswd'}

        tosca = ToscaTemplate(parsed_params=params,
                              yaml_dict_tpl=yaml_dict_tpl)

        self.assertEqual(tosca.version, "tosca_simple_yaml_1_0")

    def test_policies_for_node_templates(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/policies/tosca_policy_template.yaml")
        tosca = ToscaTemplate(tosca_tpl)

        for policy in tosca.topology_template.policies:
            self.assertTrue(
                policy.is_derived_from("tosca.policies.Root"))
            if policy.name == 'my_compute_placement_policy':
                self.assertEqual('tosca.policies.Placement', policy.type)
                self.assertEqual(['my_server_1', 'my_server_2'],
                                 policy.targets)
                self.assertEqual('node_templates', policy.get_targets_type())
                for node in policy.targets_list:
                    if node.name == 'my_server_1':
                        '''Test property value'''
                        props = node.get_properties()
                        if props and 'mem_size' in props.keys():
                            self.assertEqual(props['mem_size'].value,
                                             '4096 MB')

    def test_policies_for_groups(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/policies/tosca_policy_template.yaml")
        tosca = ToscaTemplate(tosca_tpl)

        for policy in tosca.topology_template.policies:
            self.assertTrue(
                policy.is_derived_from("tosca.policies.Root"))
            if policy.name == 'my_groups_placement':
                self.assertEqual('mycompany.mytypes.myScalingPolicy',
                                 policy.type)
                self.assertEqual(['webserver_group'], policy.targets)
                self.assertEqual('groups', policy.get_targets_type())
                group = policy.get_targets_list()[0]
                for node in group.get_member_nodes():
                    if node.name == 'my_server_2':
                        '''Test property value'''
                        props = node.get_properties()
                        if props and 'mem_size' in props.keys():
                            self.assertEqual(props['mem_size'].value,
                                             '4096 MB')
    #  Test the following:
    #  check the inheritance between custom policies.
    #  It will first parse the tosca template located at
    #  data/policies/tosca_custom_policy_template.yaml where
    #  two empty customs policies have been created. The child
    #  empty custom policy tosca.policies.Adva.Failure.Restart
    #  is derived from its parent empty  custom policy
    #  tosca.policies.Adva.Failure which is also derived
    #  from its parent empty policy tosca.policies.Root.

    def test_policies_for_custom(self):
        host_prop = {}
        tosca_tpl = utils.get_sample_test_path(
            "data/policies/tosca_custom_policy_template.yaml")
        tosca = ToscaTemplate(tosca_tpl)

        for policy in tosca.topology_template.policies:
            self.assertTrue(
                policy.is_derived_from("tosca.policies.Root"))
            if policy.name == 'My_failure_policy_restart':
                self.assertEqual('tosca.policies.Adva.Failure.Restart',
                                 policy.type)
                targets = policy.targets
                for target in targets:
                    if ('my_server_1' == target):
                        '''Test property value'''
                        for nodetemplate in tosca.nodetemplates:
                            if nodetemplate.name == target:
                                caps = nodetemplate.get_capabilities()
                                for cap in caps.keys():
                                    generic_cap = \
                                        nodetemplate.get_capability(cap)
                                    if generic_cap:
                                        for prop in \
                                            generic_cap.\
                                                get_properties_objects():
                                            host_prop[prop.name] = prop.value
                                        if cap == 'host':
                                            self.assertEqual(host_prop
                                                             ['mem_size'],
                                                             '512 MB')

    def test_node_filter(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/node_filter/test_node_filter.yaml")
        ToscaTemplate(tosca_tpl)

    def test_attributes_inheritance(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_attributes_inheritance.yaml")
        ToscaTemplate(tosca_tpl)

    @mock.patch.object(urllib.request, 'urlopen')
    def test_repositories_definition(self, mock_urlopen):
        tosca_tpl = utils.get_sample_test_path(
            "data/repositories/test_repositories_definition.yaml")
        mock_path = "https://example.com/custom_types/compute_with_prop.yaml"

        mockclass = MockTestClass()
        mockclass.comp_urldict = {mock_path: utils.get_sample_test_path(
            "data/custom_types/compute_with_prop.yaml")}
        mock_urlopen.side_effect = mockclass.mock_urlopen_method
        ToscaTemplate(tosca_tpl)

    def test_custom_caps_def(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_custom_caps_def.yaml")
        ToscaTemplate(tosca_tpl)

    def test_custom_caps_with_custom_datatype(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_custom_caps_with_datatype.yaml")
        ToscaTemplate(tosca_tpl)

    def test_custom_rel_with_script(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_tosca_custom_rel_with_script.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        rel = tosca.relationship_templates[0]
        self.assertEqual(rel.type, "tosca.relationships.HostedOn")
        self.assertTrue(rel.is_derived_from("tosca.relationships.Root"))
        self.assertEqual(len(rel.interfaces), 1)
        self.assertEqual(rel.interfaces[0].type, "Configure")

    def test_various_portspec_errors(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/datatypes/test_datatype_portspec_add_req.yaml")
        self.assertRaises(exception.ValidationError, ToscaTemplate, tosca_tpl,
                          None)

        # TODO(TBD) find way to reuse error messages from constraints.py
        msg = (_('The value "%(pvalue)s" of property "%(pname)s" is out of '
                 'range "(min:%(vmin)s, max:%(vmax)s)".') %
               dict(pname=PortSpec.SOURCE,
                    pvalue='0',
                    vmin='1',
                    vmax='65535'))
        exception.ExceptionCollector.assertExceptionMessage(
            exception.ValidationError, msg)

        # Test value below range min.
        msg = (_('The value "%(pvalue)s" of property "%(pname)s" is out of '
                 'range "(min:%(vmin)s, max:%(vmax)s)".') %
               dict(pname=PortSpec.SOURCE,
                    pvalue='1',
                    vmin='2',
                    vmax='65534'))
        exception.ExceptionCollector.assertExceptionMessage(
            exception.RangeValueError, msg)

        # Test value above range max.
        msg = (_('The value "%(pvalue)s" of property "%(pname)s" is out of '
                 'range "(min:%(vmin)s, max:%(vmax)s)".') %
               dict(pname=PortSpec.SOURCE,
                    pvalue='65535',
                    vmin='2',
                    vmax='65534'))
        exception.ExceptionCollector.assertExceptionMessage(
            exception.RangeValueError, msg)

    def test_containers(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/containers/test_container_docker_mysql.yaml")
        ToscaTemplate(tosca_tpl, parsed_params={"mysql_root_pwd": "12345678"})

    def test_endpoint_on_compute(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_endpoint_on_compute.yaml")
        ToscaTemplate(tosca_tpl)

    def test_nested_dsl_def(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/dsl_definitions/test_nested_dsl_def.yaml")
        self.assertIsNotNone(ToscaTemplate(tosca_tpl))

    def test_multiple_policies(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/policies/test_tosca_nfv_multiple_policies.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        self.assertEqual(
            ['ALRM1', 'SP1', 'SP2'],
            sorted([policy.name for policy in tosca.policies]))

    def test_custom_capability(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_custom_capabilty.yaml")
        ToscaTemplate(tosca_tpl)

    def test_csar_multilevel_imports_relative_path(self):
        csar_archive = utils.get_sample_test_path(
            "data/CSAR/csar_relative_path_import_check.zip")
        self.assertTrue(ToscaTemplate(csar_archive))

    def test_csar_multiple_deployment_flavours(self):
        csar_archive = utils.get_sample_test_path(
            "data/CSAR/csar_multiple_deployment_flavour.zip")
        tosca = ToscaTemplate(csar_archive)
        flavours = list()
        for tp in tosca.nested_tosca_templates_with_topology:
            flavour_id = tp.substitution_mappings.properties.get('flavour_id')
            flavour = {'flavour_id': flavour_id}
            flavours.append(flavour)
        self.assertEqual(flavours[0]['flavour_id'], 'simple')
        self.assertEqual(flavours[1]['flavour_id'], 'complex')

    def test_custom_rel_get_type(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/test_tosca_custom_rel.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        for src in tosca.nodetemplates:
            for rel, trgt in src.relationships.items():
                rel_tpls = trgt.get_relationship_template()

        self.assertEqual(rel_tpls[0].type, "MyAttachesTo")

    def test_policies_without_required_property(self):
        tosca_tpl = utils.get_sample_test_path(
            "data/policies/test_policies_without_required_property.yaml")
        self.assertRaises(exception.ValidationError, ToscaTemplate,
                          tosca_tpl, None)

    @mock.patch.object(ToscaTemplate, '_tpl_imports')
    def test_local_custom_defs(self, mock_tpl_imports):
        """Compare if custom defs on local and remote the same."""

        tosca_tpl = utils.get_sample_test_path(
            "data/tosca_single_instance_wordpress_with_url_import.yaml")

        local_def = utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")
        remote_def = (
            "https://example.com/custom_types/wordpress.yaml")

        local_defs = {remote_def: local_def}
        params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
                  'db_root_pwd': '12345678'}
        import_file_path = utils.get_sample_test_path(
            "data/custom_types/wordpress.yaml")
        mock_tpl_imports.return_value = [import_file_path]
        tosca = ToscaTemplate(tosca_tpl, parsed_params=params)
        tosca_local = ToscaTemplate(tosca_tpl, parsed_params=params,
                                    local_defs=local_defs)

        # Compare the name of input params defined in the custom defs
        expected = ["wp_db_name", "wp_db_user", "wp_db_password"]
        for t in [tosca, tosca_local]:
            actual = list(
                (t.tpl["topology_template"]["node_templates"]["wordpress"]
                    ["interfaces"]["Standard"]["configure"]["inputs"]).keys())
            self.assertEqual(expected, actual)
