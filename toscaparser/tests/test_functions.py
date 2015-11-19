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
from toscaparser import functions
from toscaparser.tests.base import TestCase
from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils.gettextutils import _


class IntrinsicFunctionsTest(TestCase):

    tosca_tpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/tosca_single_instance_wordpress.yaml")
    params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user'}
    tosca = ToscaTemplate(tosca_tpl, parsed_params=params)

    def _get_node(self, node_name):
        return [
            node for node in self.tosca.nodetemplates
            if node.name == node_name][0]

    def _get_operation(self, interfaces, operation):
        return [
            interface for interface in interfaces
            if interface.name == operation][0]

    def _get_property(self, node_template, property_name):
        return [prop.value for prop in node_template.get_properties_objects()
                if prop.name == property_name][0]

    def _get_inputs_dict(self):
        inputs = {}
        for input in self.tosca.inputs:
            inputs[input.name] = input.default
        return inputs

    def _get_input(self, name):
        self._get_inputs_dict()[name]

    def test_get_property(self):
        wordpress = self._get_node('wordpress')
        operation = self._get_operation(wordpress.interfaces, 'configure')
        wp_db_password = operation.inputs['wp_db_password']
        self.assertTrue(isinstance(wp_db_password, functions.GetProperty))
        result = wp_db_password.result()
        self.assertEqual('wp_pass', result)

    def test_get_property_with_input_param(self):
        wordpress = self._get_node('wordpress')
        operation = self._get_operation(wordpress.interfaces, 'configure')
        wp_db_user = operation.inputs['wp_db_user']
        self.assertTrue(isinstance(wp_db_user, functions.GetProperty))
        result = wp_db_user.result()
        self.assertEqual('my_db_user', result)

    def test_unknown_capability_property(self):
        self.assertRaises(exception.ValidationError, self._load_template,
                          'functions/test_unknown_capability_property.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError,
            _('\'Property "unknown" was not found in capability '
              '"database_endpoint" of node template "database" referenced '
              'from node template "database".\''))

    def test_get_input_in_properties(self):
        mysql_dbms = self._get_node('mysql_dbms')
        expected_inputs = ['db_root_pwd', 'db_port']
        props = mysql_dbms.get_properties()
        for key in props.keys():
            prop = props[key]
            self.assertTrue(isinstance(prop.value, functions.GetInput))
            expected_inputs.remove(prop.value.input_name)
        self.assertListEqual(expected_inputs, [])

    def test_get_input_validation(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_unknown_input_in_property.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownInputError,
            _('Unknown input "objectstore_name".'))

        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_unknown_input_in_interface.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            exception.UnknownInputError,
            _('Unknown input "image_id".'))

        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_invalid_function_signature.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Expected one argument for function "get_input" but received '
              '"[\'cpus\', \'cpus\']".'))

    def test_get_input_default_value_result(self):
        mysql_dbms = self._get_node('mysql_dbms')
        dbms_port = self._get_property(mysql_dbms, 'port')
        self.assertEqual(3306, dbms_port.result())
        dbms_root_password = self._get_property(mysql_dbms,
                                                'root_password')
        self.assertIsNone(dbms_root_password.result())


class GetAttributeTest(TestCase):

    def _load_template(self, filename):
        return ToscaTemplate(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            filename))

    def test_get_attribute_in_outputs(self):
        tpl = self._load_template('tosca_single_instance_wordpress.yaml')
        website_url_output = [
            x for x in tpl.outputs if x.name == 'website_url'][0]
        self.assertIsInstance(website_url_output.value, functions.GetAttribute)
        self.assertEqual('server', website_url_output.value.node_template_name)
        self.assertEqual('private_address',
                         website_url_output.value.attribute_name)

    def test_get_attribute_invalid_args(self):
        expected_msg = _('Expected arguments: "node-template-name", '
                         '"attribute-name"')
        err = self.assertRaises(ValueError,
                                functions.get_function, None, None,
                                {'get_attribute': []})
        self.assertIn(expected_msg, six.text_type(err))
        err = self.assertRaises(ValueError,
                                functions.get_function, None, None,
                                {'get_attribute': ['x']})
        self.assertIn(expected_msg, six.text_type(err))
        err = self.assertRaises(ValueError,
                                functions.get_function, None, None,
                                {'get_attribute': ['x', 'y', 'z']})
        self.assertIn(expected_msg, six.text_type(err))

    def test_get_attribute_unknown_node_template_name(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_get_attribute_unknown_node_template_name.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError,
            _('\'Node template "unknown_node_template" was not found.\''))

    def test_get_attribute_unknown_attribute(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_get_attribute_unknown_attribute_name.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            KeyError,
            _('\'Attribute "unknown_attribute" was not found in node template '
              '"server".\''))

    def test_get_attribute_host_keyword(self):
        tpl = self._load_template(
            'functions/test_get_attribute_host_keyword.yaml')

        def assert_get_attribute_host_functionality(node_template_name):
            node = [x for x in tpl.nodetemplates
                    if x.name == node_template_name][0]
            configure_op = [
                x for x in node.interfaces if x.name == 'configure'][0]
            ip_addr_input = configure_op.inputs['ip_address']
            self.assertIsInstance(ip_addr_input, functions.GetAttribute)
            self.assertEqual('server',
                             ip_addr_input.get_referenced_node_template().name)

        assert_get_attribute_host_functionality('dbms')
        assert_get_attribute_host_functionality('database')

    def test_get_attribute_host_not_found(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_get_attribute_host_not_found.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('"get_attribute: [ HOST, ... ]" was used in node template '
              '"server" but "tosca.relationships.HostedOn" was not found in '
              'the relationship chain.'))

    def test_get_attribute_illegal_host_in_outputs(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_get_attribute_illegal_host_in_outputs.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('"get_attribute: [ HOST, ... ]" is not allowed in "outputs" '
              'section of the TOSCA template.'))
