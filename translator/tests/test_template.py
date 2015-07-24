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
from translator.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate


class ToscaMongoNodejsTest(TestCase):
    parsed_params = {'storage_snapshot_id': 'test_id',
                     'storage_location': '/test', 'cpus': '1',
                     'storage_size': '1'}

    '''TOSCA template with nodejs, app and mongodb on 2 servers.'''
    tosca_tpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../toscalib/tests/data/tosca_nodejs_mongodb_two_instances.yaml")
    tosca = ToscaTemplate(tosca_tpl, parsed_params)

    def test_relationship_def(self):
        expected_relationship = ['tosca.relationships.HostedOn']
        expected_capabilities_names = ['node']
        for tpl in self.tosca.nodetemplates:
            if tpl.name == 'nodejs':
                def_keys = tpl.type_definition.relationship.keys()
                self.assertEqual(
                    expected_relationship,
                    sorted([x.type for x in def_keys]))
                self.assertEqual(
                    expected_capabilities_names,
                    sorted([x.capability_name for x in def_keys]))

    def test_relationships(self):
        expected_relationship = ['tosca.relationships.HostedOn']
        expected_relatednodes = ['app_server']
        for tpl in self.tosca.nodetemplates:
            rels = tpl.relationships
            if rels:
                if tpl.name == 'nodejs':
                    self.assertEqual(
                        expected_relationship,
                        sorted([x.type for x in tpl.relationships.keys()]))
                    self.assertEqual(
                        expected_relatednodes,
                        sorted([y.name for y in tpl.relationships.values()]))

    def test_related_nodes(self):
        expected_nodejs = ['app_server']
        actual_nodejs = []
        for tpl in self.tosca.nodetemplates:
            if tpl.name == 'nodejs':
                for node in tpl.related_nodes:
                    actual_nodejs.append(node.name)
        self.assertEqual(sorted(actual_nodejs), expected_nodejs)
