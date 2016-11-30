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
from toscaparser.tosca_template import ToscaTemplate


class CustomRelationshipTypesTest(TestCase):

    '''TOSCA template.'''
    tosca_tpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/relationship/test_custom_relationship.yaml")
    tosca = ToscaTemplate(tosca_tpl)

    def test_version(self):
        self.assertEqual(self.tosca.version, "tosca_simple_yaml_1_0")

    def test_custom_types(self):
        expected_custom_types = ['tosca.capabilities.HA',
                                 'tosca.nodes.HACompute',
                                 'tosca.relationships.HA']
        self.assertItemsEqual(self.tosca.topology_template.custom_defs.keys(),
                              expected_custom_types)
