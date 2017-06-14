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
    params = {'db_name': 'my_wordpress', 'db_user': 'my_db_user',
              'db_root_pwd': '12345678'}
    tosca = ToscaTemplate(tosca_tpl, parsed_params=params)

    def _get_node(self, node_name, tosca=None):
        if tosca is None:
            tosca = self.tosca
        return [
            node for node in tosca.nodetemplates
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
        self.assertIsInstance(wp_db_password, functions.GetProperty)
        result = wp_db_password.result()
        self.assertEqual('wp_pass', result)

    def test_get_property_with_input_param(self):
        wordpress = self._get_node('wordpress')
        operation = self._get_operation(wordpress.interfaces, 'configure')
        wp_db_user = operation.inputs['wp_db_user']
        self.assertIsInstance(wp_db_user, functions.GetProperty)
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
            self.assertIsInstance(prop.value, functions.GetInput)
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
        self.assertEqual(dbms_root_password.result(), '12345678')

    def test_get_property_with_host(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_get_property_with_host.yaml")
        mysql_database = self._get_node('mysql_database',
                                        ToscaTemplate(tosca_tpl,
                                                      parsed_params={
                                                          'db_root_pwd': '123'
                                                      }))
        operation = self._get_operation(mysql_database.interfaces, 'configure')
        db_port = operation.inputs['db_port']
        self.assertIsInstance(db_port, functions.GetProperty)
        result = db_port.result()
        self.assertEqual(3306, result)
        test = operation.inputs['test']
        self.assertIsInstance(test, functions.GetProperty)
        result = test.result()
        self.assertEqual(1, result)

    def test_get_property_with_nested_params(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/tosca_nested_property_names_indexes.yaml")
        webserver = self._get_node('wordpress',
                                   ToscaTemplate(tosca_tpl,
                                                 parsed_params={
                                                     'db_root_pwd': '1234'}))
        operation = self._get_operation(webserver.interfaces, 'configure')
        wp_endpoint_prot = operation.inputs['wp_endpoint_protocol']
        self.assertIsInstance(wp_endpoint_prot, functions.GetProperty)
        self.assertEqual('tcp', wp_endpoint_prot.result())
        wp_list_prop = operation.inputs['wp_list_prop']
        self.assertIsInstance(wp_list_prop, functions.GetProperty)
        self.assertEqual(3, wp_list_prop.result())

    def test_get_property_with_capabilties_inheritance(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_capabilties_inheritance.yaml")
        some_node = self._get_node('some_node',
                                   ToscaTemplate(tosca_tpl,
                                                 parsed_params={
                                                     'db_root_pwd': '1234'}))
        operation = self._get_operation(some_node.interfaces, 'configure')
        some_input = operation.inputs['some_input']
        self.assertIsInstance(some_input, functions.GetProperty)
        self.assertEqual('someval', some_input.result())

    def test_get_property_source_target_keywords(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_get_property_source_target_keywords.yaml")
        tosca = ToscaTemplate(tosca_tpl,
                              parsed_params={'db_root_pwd': '1234'})

        for node in tosca.nodetemplates:
            for relationship, trgt in node.relationships.items():
                rel_template = trgt.get_relationship_template()[0]
                break

        operation = self._get_operation(rel_template.interfaces,
                                        'pre_configure_source')
        target_test = operation.inputs['target_test']
        self.assertIsInstance(target_test, functions.GetProperty)
        self.assertEqual(1, target_test.result())
        source_port = operation.inputs['source_port']
        self.assertIsInstance(source_port, functions.GetProperty)
        self.assertEqual(3306, source_port.result())

    def test_get_prop_cap_host(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_get_prop_cap_host.yaml")
        some_node = self._get_node('some_node',
                                   ToscaTemplate(tosca_tpl))
        some_prop = some_node.get_properties()['some_prop']
        self.assertIsInstance(some_prop.value, functions.GetProperty)
        self.assertEqual('someval', some_prop.value.result())

    def test_get_prop_cap_bool(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_get_prop_cap_bool.yaml")
        some_node = self._get_node('software',
                                   ToscaTemplate(tosca_tpl))
        some_prop = some_node.get_properties()['some_prop']
        self.assertIsInstance(some_prop.value, functions.GetProperty)
        self.assertEqual(False, some_prop.value.result())


class GetAttributeTest(TestCase):

    def _load_template(self, filename):
        return ToscaTemplate(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data',
            filename),
            parsed_params={'db_root_pwd': '1234'})

    def _get_operation(self, interfaces, operation):
        return [
            interface for interface in interfaces
            if interface.name == operation][0]

    def test_get_attribute_in_outputs(self):
        tpl = self._load_template('tosca_single_instance_wordpress.yaml')
        website_url_output = [
            x for x in tpl.outputs if x.name == 'website_url'][0]
        self.assertIsInstance(website_url_output.value, functions.GetAttribute)
        self.assertEqual('server', website_url_output.value.node_template_name)
        self.assertEqual('private_address',
                         website_url_output.value.attribute_name)

    def test_get_attribute_invalid_args(self):
        expected_msg = _('Illegal arguments for function "get_attribute".'
                         ' Expected arguments: "node-template-name", '
                         '"req-or-cap"(optional), "property name"')
        err = self.assertRaises(ValueError,
                                functions.get_function, None, None,
                                {'get_attribute': []})
        self.assertIn(expected_msg, six.text_type(err))
        err = self.assertRaises(ValueError,
                                functions.get_function, None, None,
                                {'get_attribute': ['x']})
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

    def test_get_attribute_with_index(self):
        self._load_template(
            'functions/test_get_attribute_with_index.yaml')

    def test_get_attribute_with_index_error(self):
        self.assertRaises(
            exception.ValidationError, self._load_template,
            'functions/test_get_attribute_with_index_error.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Illegal arguments for function "get_attribute". '
              'Unexpected attribute/index value "0"'))

    def test_get_attribute_source_target_keywords(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/functions/test_get_attribute_source_target_keywords.yaml")
        tosca = ToscaTemplate(tosca_tpl,
                              parsed_params={'db_root_pwd': '12345678'})

        for node in tosca.nodetemplates:
            for relationship, trgt in node.relationships.items():
                rel_template = trgt.get_relationship_template()[0]
                break

        operation = self._get_operation(rel_template.interfaces,
                                        'pre_configure_source')
        target_test = operation.inputs['target_test']
        self.assertIsInstance(target_test, functions.GetAttribute)
        source_port = operation.inputs['source_port']
        self.assertIsInstance(source_port, functions.GetAttribute)

    def test_get_attribute_with_nested_params(self):
        self._load_template(
            'functions/test_get_attribute_with_nested_params.yaml')

    def test_implicit_attribute(self):
        self.assertIsNotNone(self._load_template(
            'functions/test_get_implicit_attribute.yaml'))

    def test_get_attribute_capability_inheritance(self):
        self.assertIsNotNone(self._load_template(
            'functions/test_container_cap_child.yaml'))


class ConcatTest(TestCase):

    def _load_template(self, filename):
        return ToscaTemplate(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename))

    def test_validate_concat(self):
        tosca = self._load_template("data/functions/test_concat.yaml")
        server_url_output = [
            output for output in tosca.outputs if output.name == 'url'][0]
        func = functions.get_function(self, tosca.outputs,
                                      server_url_output.value)
        self.assertIsInstance(func, functions.Concat)

        self.assertRaises(exception.ValidationError, self._load_template,
                          'data/functions/test_concat_invalid.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Invalid arguments for function "concat". Expected at least '
              'one arguments.'))


class TokenTest(TestCase):

    def _load_template(self, filename):
        return ToscaTemplate(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename))

    def test_validate_token(self):
        tosca = self._load_template("data/functions/test_token.yaml")
        server_url_output = [
            output for output in tosca.outputs if output.name == 'url'][0]
        func = functions.get_function(self, tosca.outputs,
                                      server_url_output.value)
        self.assertIsInstance(func, functions.Token)

        self.assertRaises(exception.ValidationError, self._load_template,
                          'data/functions/test_token_invalid.yaml')
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Invalid arguments for function "token". Expected at least '
              'three arguments.'))
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Invalid arguments for function "token". Expected '
              'integer value as third argument.'))
        exception.ExceptionCollector.assertExceptionMessage(
            ValueError,
            _('Invalid arguments for function "token". Expected '
              'single char value as second argument.'))
