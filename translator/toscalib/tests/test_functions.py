# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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
from translator.toscalib import functions
from translator.toscalib.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate


class IntrinsicFunctionsTest(TestCase):

    tosca_tpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/tosca_single_instance_wordpress.yaml")
    tosca = ToscaTemplate(tosca_tpl)

    def _load_template(self, filename):
        return ToscaTemplate(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'data/functions',
            filename))

    def _get_node(self, node_name):
        return [
            node for node in self.tosca.nodetemplates
            if node.name == node_name][0]

    def _get_operation(self, interfaces, operation):
        return [
            interface for interface in interfaces
            if interface.name == operation][0]

    def test_get_property(self):
        mysql_dbms = self._get_node('mysql_dbms')
        operation = self._get_operation(mysql_dbms.interfaces, 'configure')
        db_root_password = operation.input['db_root_password']
        self.assertTrue(isinstance(db_root_password, functions.GetProperty))
        result = db_root_password.result()
        self.assertTrue(isinstance(result, functions.GetInput))

    def test_get_requirement_property(self):
        wordpress = self._get_node('wordpress')
        operation = self._get_operation(wordpress.interfaces, 'configure')
        wp_db_port = operation.input['wp_db_port']
        self.assertTrue(isinstance(wp_db_port, functions.GetProperty))
        result = wp_db_port.result()
        self.assertTrue(isinstance(result, functions.GetInput))
        self.assertEqual('db_port', result.input_name)

    def test_get_capability_property(self):
        mysql_database = self._get_node('mysql_database')
        operation = self._get_operation(mysql_database.interfaces, 'configure')
        db_port = operation.input['db_port']
        self.assertTrue(isinstance(db_port, functions.GetProperty))
        result = db_port.result()
        self.assertTrue(isinstance(result, functions.GetInput))
        self.assertEqual('db_port', result.input_name)

    def test_unknown_capability_property(self):
        err = self.assertRaises(KeyError,
                                self._load_template,
                                'test_unknown_capability_property.yaml')
        self.assertIn("'unknown'", six.text_type(err))
        self.assertIn("'database_endpoint'", six.text_type(err))
        self.assertIn("'database'", six.text_type(err))

    def test_get_input_in_properties(self):
        mysql_dbms = self._get_node('mysql_dbms')
        self.assertTrue(isinstance(mysql_dbms.properties[0].value,
                                   functions.GetInput))
        self.assertTrue(mysql_dbms.properties[0].value.input_name,
                        'db_root_pwd')
        self.assertTrue(isinstance(mysql_dbms.properties[1].value,
                                   functions.GetInput))
        self.assertTrue(mysql_dbms.properties[1].value.input_name,
                        'db_port')

    def test_get_input_in_interface(self):
        mysql_dbms = self._get_node('mysql_dbms')
        operation = self._get_operation(mysql_dbms.interfaces, 'configure')
        db_user = operation.input['db_user']
        self.assertTrue(isinstance(db_user, functions.GetInput))

    def test_get_input_validation(self):
        self.assertRaises(exception.UnknownInputError,
                          self._load_template,
                          'test_unknown_input_in_property.yaml')
        self.assertRaises(exception.UnknownInputError,
                          self._load_template,
                          'test_unknown_input_in_interface.yaml')
