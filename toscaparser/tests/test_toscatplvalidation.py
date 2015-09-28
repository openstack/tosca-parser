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

from toscaparser.common import exception
from toscaparser.imports import ImportsLoader
from toscaparser.nodetemplate import NodeTemplate
from toscaparser.parameters import Input
from toscaparser.parameters import Output
from toscaparser.relationship_template import RelationshipTemplate
from toscaparser.tests.base import TestCase
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils.gettextutils import _

import toscaparser.utils.yamlparser


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
        inputs = (toscaparser.utils.yamlparser.
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

    def _imports_content_test(self, tpl_snippet, path, custom_type_def):
        imports = (toscaparser.utils.yamlparser.
                   simple_parse(tpl_snippet)['imports'])
        loader = ImportsLoader(imports, path, custom_type_def)
        return loader.get_custom_defs()

    def test_imports_without_templates(self):
        tpl_snippet = '''
        imports:
          # omitted here for brevity
        '''
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        errormsg = _("imports keyname defined without "
                     "including templates")
        err = self.assertRaises(exception.ValidationError,
                                self._imports_content_test,
                                tpl_snippet,
                                path,
                                "node_types")
        self.assertEqual(errormsg, err.__str__())

    def test_imports_with_name_without_templates(self):
        tpl_snippet = '''
        imports:
          - some_definitions:
        '''
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        errormsg = _("Input tosca template is not provided with import"
                     " 'some_definitions' definition.")
        err = self.assertRaises(exception.ValidationError,
                                self._imports_content_test,
                                tpl_snippet, path, None)
        self.assertEqual(errormsg, err.__str__())

    def test_imports_without_import_name(self):
        tpl_snippet = '''
        imports:
          - custom_types/paypalpizzastore_nodejs_app.yaml
          - https://raw.githubusercontent.com/openstack/\
tosca-parser/master/toscaparser/tests/data/custom_types/wordpress.yaml
        '''
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        custom_defs = self._imports_content_test(tpl_snippet,
                                                 path,
                                                 "node_types")
        self.assertTrue(custom_defs)

    def test_imports_wth_import_name(self):
        tpl_snippet = '''
        imports:
          - some_definitions: custom_types/paypalpizzastore_nodejs_app.yaml
          - more_definitions:
              file: toscaparser/tests/data/custom_types/wordpress.yaml
              repository: tosca-parser/master
              namespace_uri: https://raw.githubusercontent.com/openstack
              namespace_prefix: single_instance_wordpress
        '''
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        custom_defs = self._imports_content_test(tpl_snippet,
                                                 path,
                                                 "node_types")
        self.assertTrue(custom_defs.get("tosca.nodes."
                                        "WebApplication.WordPress"))

    def test_imports_with_no_main_template(self):
        tpl_snippet = '''
        imports:
          - some_definitions: https://raw.githubusercontent.com/openstack/\
tosca-parser/master/toscaparser/tests/data/custom_types/wordpress.yaml
          - some_definitions:
              file: my_defns/my_typesdefs_n.yaml
        '''
        errormsg = _('Input tosca template is not provided')
        err = self.assertRaises(exception.ValidationError,
                                self._imports_content_test,
                                tpl_snippet, None, None)
        self.assertEqual(errormsg, err.__str__())

    def test_imports_duplicate_name(self):
        tpl_snippet = '''
        imports:
          - some_definitions: https://raw.githubusercontent.com/openstack/\
tosca-parser/master/toscaparser/tests/data/custom_types/wordpress.yaml
          - some_definitions:
              file: my_defns/my_typesdefs_n.yaml
        '''
        errormsg = _('Duplicate Import name found some_definitions')
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        err = self.assertRaises(exception.ValidationError,
                                self._imports_content_test,
                                tpl_snippet, path, None)
        self.assertEqual(errormsg, err.__str__())

    def test_imports_missing_req_field_in_def(self):
        tpl_snippet = '''
        imports:
          - more_definitions:
              file1: my_defns/my_typesdefs_n.yaml
              repository: my_company_repo
              namespace_uri: http://mycompany.com/ns/tosca/2.0
              namespace_prefix: mycompany
        '''
        errormsg = _('Import of template more_definitions is missing'
                     ' required field: "file".')
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        err = self.assertRaises(exception.MissingRequiredFieldError,
                                self._imports_content_test,
                                tpl_snippet, path, None)
        self.assertEqual(errormsg, err.__str__())

    def test_imports_file_with_uri(self):
        tpl_snippet = '''
        imports:
          - more_definitions:
              file: https://raw.githubusercontent.com/openstack/\
tosca-parser/master/toscaparser/tests/data/custom_types/wordpress.yaml
              namespace_prefix: mycompany
        '''
        path = 'https://raw.githubusercontent.com/openstack/\
tosca-parser/master/toscaparser/tests/data/\
tosca_single_instance_wordpress_with_url_import.yaml'
        custom_defs = self._imports_content_test(tpl_snippet,
                                                 path,
                                                 "node_types")
        self.assertTrue(custom_defs.get("tosca.nodes."
                                        "WebApplication.WordPress"))

    def test_imports_file_namespace_fields(self):
        tpl_snippet = '''
        imports:
          - more_definitions:
              file: heat-translator/master/translator/tests/data/\
custom_types/wordpress.yaml
              namespace_uri: https://raw.githubusercontent.com/openstack/
              namespace_prefix: mycompany
        '''
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        custom_defs = self._imports_content_test(tpl_snippet,
                                                 path,
                                                 "node_types")
        self.assertTrue(custom_defs.get("tosca.nodes."
                                        "WebApplication.WordPress"))

    def test_import_error_namespace_uri(self):
        tpl_snippet = '''
        imports:
          - more_definitions:
              file: toscaparser/tests/data/tosca_elk.yaml
              namespace_uri: mycompany.com/ns/tosca/2.0
              namespace_prefix: mycompany
        '''
        errormsg = _("namespace_uri mycompany.com/ns/tosca/2.0 is not "
                     "valid in import 'more_definitions' definition")
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        err = self.assertRaises(ImportError,
                                self._imports_content_test,
                                tpl_snippet, path, None)
        self.assertEqual(errormsg, err.__str__())

    def test_import_single_line_error(self):
        tpl_snippet = '''
        imports:
          - some_definitions: abc.com/tests/data/tosca_elk.yaml
        '''
        errormsg = _('Import abc.com/tests/data/tosca_elk.yaml is not valid')
        path = 'toscaparser/tests/data/tosca_elk.yaml'
        err = self.assertRaises(ImportError,
                                self._imports_content_test,
                                tpl_snippet, path, None)
        self.assertEqual(errormsg, err.__str__())

    def test_outputs(self):
        tpl_snippet = '''
        outputs:
          server_address:
            description: IP address of server instance.
            values: { get_property: [server, private_address] }
        '''
        outputs = (toscaparser.utils.yamlparser.
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
        outputs = (toscaparser.utils.yamlparser.
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
        custom_type = toscaparser.utils.yamlparser.load_yaml(def_file)
        node_types = custom_type['node_types']
        for name in node_types:
            defintion = node_types[name]
            custom_types[name] = defintion
        return custom_types

    def _single_node_template_content_test(self, tpl_snippet):
        nodetemplates = (toscaparser.utils.yamlparser.
                         simple_ordered_parse(tpl_snippet))['node_templates']
        name = list(nodetemplates.keys())[0]
        nodetemplate = NodeTemplate(name, nodetemplates,
                                    self._custom_types())
        nodetemplate.validate()
        nodetemplate.requirements
        nodetemplate.get_capabilities_objects()
        nodetemplate.get_properties_objects()
        nodetemplate.interfaces

    def test_node_templates(self):
        tpl_snippet = '''
        node_templates:
          server:
            capabilities:
              host:
                properties:
                  disk_size: 10
                  num_cpus: 4
                  mem_size: 4096
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18.0
        '''
        expectedmessage = ('Template server is missing '
                           'required field: "type".')
        err = self.assertRaises(
            exception.MissingRequiredFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_wrong_properties_keyname(self):
        """Node template keyname 'properties' given as 'propertiessss'."""
        tpl_snippet = '''
        node_templates:
          mysql_dbms:
            type: tosca.nodes.DBMS
            propertiessss:
              root_password: aaa
              port: 3376
        '''
        expectedmessage = ('Node template mysql_dbms '
                           'contain(s) unknown field: "propertiessss", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_wrong_requirements_keyname(self):
        """Node template keyname 'requirements' given as 'requirement'."""
        tpl_snippet = '''
        node_templates:
          mysql_dbms:
            type: tosca.nodes.DBMS
            properties:
              root_password: aaa
              port: 3376
            requirement:
              - host: server
        '''
        expectedmessage = ('Node template mysql_dbms '
                           'contain(s) unknown field: "requirement", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_wrong_interfaces_keyname(self):
        """Node template keyname 'interfaces' given as 'interfac'."""
        tpl_snippet = '''
        node_templates:
          mysql_dbms:
            type: tosca.nodes.DBMS
            properties:
              root_password: aaa
              port: 3376
            requirements:
              - host: server
            interfac:
              Standard:
                configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Node template mysql_dbms '
                           'contain(s) unknown field: "interfac", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_wrong_capabilities_keyname(self):
        """Node template keyname 'capabilities' given as 'capabilitiis'."""
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            properties:
              db_name: { get_input: db_name }
              db_user: { get_input: db_user }
              db_password: { get_input: db_pwd }
            capabilitiis:
              database_endpoint:
                properties:
                  port: { get_input: db_port }
        '''
        expectedmessage = ('Node template mysql_database '
                           'contain(s) unknown field: "capabilitiis", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_wrong_artifacts_keyname(self):
        """Node template keyname 'artifacts' given as 'artifactsss'."""
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            artifactsss:
              db_content:
                implementation: files/my_db_content.txt
                type: tosca.artifacts.File
        '''
        expectedmessage = ('Node template mysql_database '
                           'contain(s) unknown field: "artifactsss", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_with_multiple_wrong_keynames(self):
        """Node templates given with multiple wrong keynames."""
        tpl_snippet = '''
        node_templates:
          mysql_dbms:
            type: tosca.nodes.DBMS
            propertieees:
              root_password: aaa
              port: 3376
            requirements:
              - host: server
            interfacs:
              Standard:
                configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Node template mysql_dbms '
                           'contain(s) unknown field: "propertieees", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            properties:
              name: { get_input: db_name }
              user: { get_input: db_user }
              password: { get_input: db_pwd }
            capabilitiiiies:
              database_endpoint:
              properties:
                port: { get_input: db_port }
            requirementsss:
              - host:
                  node: mysql_dbms
            interfac:
              Standard:
                 configure: mysql_database_configure.sh

        '''
        expectedmessage = ('Node template mysql_database '
                           'contain(s) unknown field: "capabilitiiiies", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

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
              Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Type "tosca.nodes.Databases" is not '
                           'a valid type.')
        err = self.assertRaises(
            exception.InvalidTypeError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements(self):
        tpl_snippet = '''
        node_templates:
          webserver:
            type: tosca.nodes.WebServer
            requirements:
              host: server
            interfaces:
              Standard:
                create: webserver_install.sh
                start: d.sh
        '''
        expectedmessage = ('Requirements of template webserver '
                           'must be of type: "list".')
        err = self.assertRaises(
            exception.TypeMismatchError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

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
              Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "database_endpoint", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_with_wrong_node_keyname(self):
        """Node template requirements keyname 'node' given as 'nodes'."""
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  nodes: mysql_dbms

        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "nodes", refer to the '
                           'definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_with_wrong_capability_keyname(self):
        """Incorrect node template requirements keyname

        Node template requirements keyname 'capability' given as
        'capabilityy'.
        """
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  node: mysql_dbms
              - log_endpoint:
                  node: logstash
                  capabilityy: log_endpoint
                  relationship:
                    type: tosca.relationships.ConnectsTo

        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "capabilityy", refer to '
                           'the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_with_wrong_relationship_keyname(self):
        """Incorrect node template requirements keyname

        Node template requirements keyname 'relationship' given as
        'relationshipppp'.
        """
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  node: mysql_dbms
              - log_endpoint:
                  node: logstash
                  capability: log_endpoint
                  relationshipppp:
                    type: tosca.relationships.ConnectsTo

        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "relationshipppp", refer'
                           ' to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_with_wrong_occurrences_keyname(self):
        """Incorrect node template requirements keyname

        Node template requirements keyname 'occurrences' given as
        'occurences'.
        """
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  node: mysql_dbms
              - log_endpoint:
                  node: logstash
                  capability: log_endpoint
                  relationship:
                    type: tosca.relationships.ConnectsTo
                  occurences: [0, UNBOUNDED]
        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "occurences", refer'
                           ' to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_with_multiple_wrong_keynames(self):
        """Node templates given with multiple wrong requirements keynames."""
        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  node: mysql_dbms
              - log_endpoint:
                  nod: logstash
                  capabilit: log_endpoint
                  relationshipppp:
                    type: tosca.relationships.ConnectsTo

        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "nod", refer'
                           ' to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          mysql_database:
            type: tosca.nodes.Database
            requirements:
              - host:
                  node: mysql_dbms
              - log_endpoint:
                  node: logstash
                  capabilit: log_endpoint
                  relationshipppp:
                    type: tosca.relationships.ConnectsTo

        '''
        expectedmessage = ('Requirements of template mysql_database '
                           'contain(s) unknown field: "capabilit", refer'
                           ' to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_invalid_occurrences(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: [0, -1]
        '''
        expectedmessage = ('Value of property "[0, -1]" is invalid.')
        err = self.assertRaises(
            exception.InvalidPropertyValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: [a, w]
        '''
        expectedmessage = ('"a" is not an integer.')
        err = self.assertRaises(
            ValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: -1
        '''
        expectedmessage = ('"-1" is not a list.')
        err = self.assertRaises(
            ValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: [5, 1]
        '''
        expectedmessage = ('Value of property "[5, 1]" is invalid.')
        err = self.assertRaises(
            exception.InvalidPropertyValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: [0, 0]
        '''
        expectedmessage = ('Value of property "[0, 0]" is invalid.')
        err = self.assertRaises(
            exception.InvalidPropertyValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_requirements_valid_occurrences(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            requirements:
              - log_endpoint:
                  capability: log_endpoint
                  occurrences: [2, 2]
        '''
        self._single_node_template_content_test(tpl_snippet)

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
              Standard:
                 configure: mysql_database_configure.sh
        '''
        expectedmessage = ('Capabilities of template mysql_database '
                           'contain(s) unknown field: "http_endpoint", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_properties(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              os_image: F18_x86_64
            capabilities:
              host:
                properties:
                  disk_size: 10 GB
                  num_cpus: { get_input: cpus }
                  mem_size: 4096 MB
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18.0
        '''
        expectedmessage = ('Properties of template server contain(s) '
                           'unknown field: "os_image", refer to the '
                           'definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_interfaces(self):
        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              Standards:
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
                           '"Standards", '
                           'refer to the definition to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              Standard:
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
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          wordpress:
            type: tosca.nodes.WebApplication.WordPress
            requirements:
              - host: webserver
              - database_endpoint: mysql_database
            interfaces:
              Standard:
                 create: wordpress_install.sh
                 configure:
                   implementation: wordpress_configure.sh
                   input:
                     wp_db_name: { get_property: [ mysql_database, db_name ] }
                     wp_db_user: { get_property: [ mysql_database, db_user ] }
                     wp_db_password: { get_property: [ mysql_database, \
                     db_password ] }
                     wp_db_port: { get_ref_property: [ database_endpoint, \
                     database_endpoint, port ] }
        '''
        expectedmessage = ('Interfaces of template wordpress contain(s) '
                           'unknown field: "input", refer to the definition'
                           ' to verify valid values.')
        err = self.assertRaises(
            exception.UnknownFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

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
        rel_template = (toscaparser.utils.yamlparser.
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
            capabilities:
              host:
                properties:
                  disk_size: 10 GB
                  num_cpus: { get_input: cpus }
                  mem_size: 4096 MB
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18.0
              scalable:
                properties:
                  min_instances: 1
                  default_instances: 5
        '''
        expectedmessage = ('Properties of template server is missing '
                           'required field: '
                           '"[\'max_instances\']".')
        err = self.assertRaises(
            exception.MissingRequiredFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        # validating capability property values
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.WebServer
            capabilities:
              data_endpoint:
                properties:
                  initiator: test
        '''
        expectedmessage = ('initiator: test is not a valid value. Expected a '
                           'value from "[source, target, peer]".')

        err = self.assertRaises(
            exception.ValidationError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            capabilities:
              host:
                properties:
                  disk_size: 10 GB
                  num_cpus: { get_input: cpus }
                  mem_size: 4096 MB
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18.0
              scalable:
                properties:
                  min_instances: 1
                  max_instances: 3
                  default_instances: 5
        '''
        expectedmessage = ('Properties of template server : '
                           'default_instances value is not between'
                           ' min_instances and max_instances')
        err = self.assertRaises(
            exception.ValidationError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_objectstorage_without_required_property(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.ObjectStorage
            properties:
              maxsize: 1 GB
        '''
        expectedmessage = ('Properties of template server is missing '
                           'required field: '
                           '"[\'name\']".')
        err = self.assertRaises(
            exception.MissingRequiredFieldError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_objectstorage_with_invalid_scalar_unit(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.ObjectStorage
            properties:
              name: test
              maxsize: -1
        '''
        expectedmessage = ('"-1" is not a valid scalar-unit')
        err = self.assertRaises(
            ValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_node_template_objectstorage_with_invalid_scalar_type(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.ObjectStorage
            properties:
              name: test
              maxsize: 1 XB
        '''
        expectedmessage = ('"1 XB" is not a valid scalar-unit')
        err = self.assertRaises(
            ValueError,
            lambda: self._single_node_template_content_test(tpl_snippet))
        self.assertEqual(expectedmessage, err.__str__())

    def test_special_keywords(self):
        """Test special keywords

           Test that special keywords, e.g.  metadata, which are not part
           of specification do not throw any validation error.
        """
        tpl_snippet_metadata_map = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            metadata:
              name: server A
              role: master
        '''
        self._single_node_template_content_test(tpl_snippet_metadata_map)

        tpl_snippet_metadata_inline = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            metadata: none
        '''
        self._single_node_template_content_test(tpl_snippet_metadata_inline)
