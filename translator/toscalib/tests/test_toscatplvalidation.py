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
import six

from translator.toscalib.common import exception
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.parameters import Input, Output
from translator.toscalib.relationship_template import RelationshipTemplate
from translator.toscalib.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate
import translator.toscalib.utils.yamlparser


class ToscaTemplateValidationTest(TestCase):

    def test_well_defined_template(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/tosca_single_instance_wordpress.yaml")
        self.assertIsNotNone(ToscaTemplate(tpl_path))

    def test_first_level_sections(self):
        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/test_tosca_top_level_error1.yaml")
        err = self.assertRaises(exception.MissingRequiredFieldError,
                                ToscaTemplate, tpl_path)
        self.assertEqual('Template is missing required field: '
                         '"tosca_definitions_version".', err.__str__())

        tpl_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/test_tosca_top_level_error2.yaml")
        err = self.assertRaises(exception.UnknownFieldError,
                                ToscaTemplate, tpl_path)
        self.assertEqual('Template contain(s) unknown field: '
                         '"node_template", refer to the definition '
                         'to verify valid values.', err.__str__())

    def test_inputs(self):
        tpl_snippet = '''
        inputs:
          cpus:
            type: integer
            description: Number of CPUs for the server.
            constraint:
              - valid_values: [ 1, 2, 4, 8 ]
        '''
        inputs = (translator.toscalib.utils.yamlparser.
                  simple_parse(tpl_snippet)['inputs'])
        name, attrs = list(inputs.items())[0]
        input = Input(name, attrs)
        try:
            input.validate()
        except Exception as err:
            self.assertTrue(isinstance(err, exception.UnknownFieldError))
            self.assertEqual('Input cpus contain(s) unknown field: '
                             '"constraint", refer to the definition to '
                             'verify valid values.', err.__str__())

    def test_outputs(self):
        tpl_snippet = '''
        outputs:
          server_address:
            description: IP address of server instance.
            values: { get_property: [server, private_address] }
        '''
        outputs = (translator.toscalib.utils.yamlparser.
                   simple_parse(tpl_snippet)['outputs'])
        name, attrs = list(outputs.items())[0]
        output = Output(name, attrs)
        try:
            output.validate()
        except Exception as err:
            self.assertTrue(
                isinstance(err, exception.MissingRequiredFieldError))
            self.assertEqual('Output server_address is missing required '
                             'field: "value".', err.__str__())

        tpl_snippet = '''
        outputs:
          server_address:
            descriptions: IP address of server instance.
            value: { get_property: [server, private_address] }
        '''
        outputs = (translator.toscalib.utils.yamlparser.
                   simple_parse(tpl_snippet)['outputs'])
        name, attrs = list(outputs.items())[0]
        output = Output(name, attrs)
        try:
            output.validate()
        except Exception as err:
            self.assertTrue(isinstance(err, exception.UnknownFieldError))
            self.assertEqual('Output server_address contain(s) unknown '
                             'field: "descriptions", refer to the definition '
                             'to verify valid values.',
                             err.__str__())

    def _custom_types(self):
        custom_types = {}
        def_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/custom_types/wordpress.yaml")
        custom_type = translator.toscalib.utils.yamlparser.load_yaml(def_file)
        node_types = custom_type['node_types']
        for name in node_types:
            defintion = node_types[name]
            custom_types[name] = defintion
        return custom_types

    def _single_node_template_content_test(self, tpl_snippet, expectederror,
                                           expectedmessage):
        nodetemplates = (translator.toscalib.utils.yamlparser.
                         simple_parse(tpl_snippet))['node_templates']
        name = list(nodetemplates.keys())[0]
        try:
            nodetemplate = NodeTemplate(name, nodetemplates,
                                        self._custom_types())
            nodetemplate.validate()
            nodetemplate.requirements
            nodetemplate.get_capabilities_objects()
            nodetemplate.get_properties_objects()
            nodetemplate.interfaces

        except Exception as err:
            self.assertTrue(isinstance(err, expectederror))
            self.assertEqual(expectedmessage, err.__str__())

    def test_node_templates(self):
        tpl_snippet = '''
        node_templates:
          server:
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: 4
              mem_size: 4096
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
        '''
        expectedmessage = ('Template server is missing '
                           'required field: "type".')
        self._single_node_template_content_test(
            tpl_snippet,
            exception.MissingRequiredFieldError,
            expectedmessage)

        tpl_snippet = '''
        node_templates:
          mysql_dbms:
            type: tosca.nodes.DBMS
            properties:
              dbms_root_password: aaa
              dbms_port: 3376
            requirement:
              - host: server
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                create: mysql_dbms_install.sh
                start: mysql_dbms_start.sh
                configure:
                  implementation: mysql_dbms_configure.sh
                  inputs:
                    db_root_password: { get_property: [ mysql_dbms, \
                    dbms_root_password ] }
        '''
        expectedmessage = ('Second level of template mysql_dbms '
                           'contain(s) unknown field: "requirement", '
                           'refer to the definition to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

    def test_node_template_type(self):
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Databases
            properties:
              db_name: { get_input: db_name }
              db_user: { get_input: db_user }
              db_password: { get_input: db_pwd }
            capabilities:
              database_endpoint:
                properties:
                  port: { get_input: db_port }
            requirements:
              - host: mysql_dbms
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Type "tosca.nodes.Databases" is not '
                           'a valid type.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.InvalidTypeError,
                                                expectedmessage)

    def test_node_template_requirements(self):
        tpl_snippet = '''
        node_templates:
          webserver:
            type: tosca.nodes.WebServer
            requirements:
              host: server
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                create: webserver_install.sh
                start: d.sh
        '''
        expectedmessage = ('Requirements of template webserver '
                           'must be of type: "list".')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.TypeMismatchError,
                                                expectedmessage)

        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            properties:
              db_name: { get_input: db_name }
              db_user: { get_input: db_user }
              db_password: { get_input: db_pwd }
            capabilities:
              database_endpoint:
                properties:
                  port: { get_input: db_port }
            requirements:
              - host: mysql_dbms
              - database_endpoint: mysql_database
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "database_endpoint", '
                           'refer to the definition to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

    def test_node_template_capabilities(self):
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            properties:
              db_name: { get_input: db_name }
              db_user: { get_input: db_user }
              db_password: { get_input: db_pwd }
            capabilities:
              http_endpoint:
                properties:
                  port: { get_input: db_port }
            requirements:
              - host: mysql_dbms
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Capabilities of template mysql_database '
                           'contain(s) unknown field: "http_endpoint", '
                           'refer to the definition to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

    def test_node_template_properties(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: { get_input: cpus }
              mem_size: 4096
              os_image: F18_x86_64
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
        '''
        expectedmessage = ('Properties of template server contain(s) '
                           'unknown field: "os_image", refer to the '
                           'definition to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

    def test_node_template_interfaces(self):
        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              tosca.interfaces.node.lifecycle.Standards:
                 create: wordpress_install.sh
                 configure:
                   implementation: wordpress_configure.sh
                   inputs:
                     wp_db_name: { get_property: [ mysql_database, db_name ] }
                     wp_db_user: { get_property: [ mysql_database, db_user ] }
                     wp_db_password: { get_property: [ mysql_database, \
                     db_password ] }
                     wp_db_port: { get_property: [ SELF, \
                     database_endpoint, port ] }
        '''
        expectedmessage = ('Interfaces of template wordpress '
                           'contain(s) unknown field: '
                           '"tosca.interfaces.node.lifecycle.Standards", '
                           'refer to the definition to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                 create: wordpress_install.sh
                 config:
                   implementation: wordpress_configure.sh
                   inputs:
                     wp_db_name: { get_property: [ mysql_database, db_name ] }
                     wp_db_user: { get_property: [ mysql_database, db_user ] }
                     wp_db_password: { get_property: [ mysql_database, \
                     db_password ] }
                     wp_db_port: { get_property: [ SELF, \
                     database_endpoint, port ] }
        '''
        expectedmessage = ('Interfaces of template wordpress contain(s) '
                           'unknown field: "config", refer to the definition'
                           ' to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              tosca.interfaces.node.lifecycle.Standard:
                 create: wordpress_install.sh
                 configure:
                   implementation: wordpress_configure.sh
                   inputs:
                     wp_db_name: { get_property: [ mysql_database, db_name ] }
                     wp_db_user: { get_property: [ mysql_database, db_user ] }
                     wp_db_password: { get_property: [ mysql_database, \
                     db_password ] }
                     wp_db_port: { get_ref_property: [ database_endpoint, \
                     database_endpoint, port ] }
        '''
        expectedmessage = ('Interfaces of template wordpress contain(s) '
                           'unknown field: "inputs", refer to the definition'
                           ' to verify valid values.')
        self._single_node_template_content_test(tpl_snippet,
                                                exception.UnknownFieldError,
                                                expectedmessage)

    def test_relationship_template_properties(self):
        tpl_snippet = '''
        relationship_templates:
            storage_attachto:
                type: AttachesTo
                properties:
                  device: test_device
        '''
        expectedmessage = ('Properties of template '
                           'storage_attachto is missing required field: '
                           '"[\'location\']".')
        self._single_rel_template_content_test(
            tpl_snippet,
            exception.MissingRequiredFieldError,
            expectedmessage)

    def _single_rel_template_content_test(self, tpl_snippet, expectederror,
                                          expectedmessage):
        rel_template = (translator.toscalib.utils.yamlparser.
                        simple_parse(tpl_snippet))['relationship_templates']
        name = list(rel_template.keys())[0]
        rel_template = RelationshipTemplate(rel_template[name], name)
        err = self.assertRaises(expectederror, rel_template.validate)
        self.assertEqual(expectedmessage, six.text_type(err))

    def test_invalid_template_version(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/test_invalid_template_version.yaml")
        err = self.assertRaises(exception.InvalidTemplateVersion,
                                ToscaTemplate, tosca_tpl)
        valid_versions = ', '.join(ToscaTemplate.VALID_TEMPLATE_VERSIONS)
        ex_err_msg = ('The template version "tosca_xyz" is invalid. '
                      'The valid versions are: "%s"' % valid_versions)
        self.assertEqual(six.text_type(err), ex_err_msg)

    def test_node_template_capabilities_properties(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: { get_input: cpus }
              mem_size: 4096
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
              scalable:
                properties:
                  min_instances: 1
                  default_instances: 5
        '''
        expectedmessage = ('Properties of template server is missing '
                           'required field: '
                           '"[\'max_instances\']".')

        self._single_node_template_content_test(
            tpl_snippet,
            exception.MissingRequiredFieldError,
            expectedmessage)

        # validatating capability property values
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.WebServer
            capabilities:
              http_endpoint:
                properties:
                  initiator: test
        '''
        expectedmessage = ('initiator: test is not an valid value '
                           '"[source, target, peer]".')

        self._single_node_template_content_test(
            tpl_snippet,
            exception.ValidationError,
            expectedmessage)

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: { get_input: cpus }
              mem_size: 4096
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
              scalable:
                properties:
                  min_instances: 1
                  max_instances: 3
                  default_instances: 5
        '''
        expectedmessage = ('Properties of template server : '
                           'default_instances value is not between'
                           ' min_instances and max_instances')

        self._single_node_template_content_test(
            tpl_snippet,
            exception.ValidationError,
            expectedmessage)
