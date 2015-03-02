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
from translator.hot.tosca_translator import TOSCATranslator
from translator.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate
import translator.toscalib.utils.yamlparser


class ToscaMongoNodejsTest(TestCase):
    parsed_params = {'storage_snapshot_id': 'test_id',
                     'storage_location': '/test', 'cpus': '1',
                     'storage_size': '1'}

    '''TOSCA template with nodejs, app and mongodb on 2 servers.'''
    tosca_tpl = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/tosca_elk.yaml")
    tosca = ToscaTemplate(tosca_tpl)

    def test_relationship_def(self):
        expected_relationship = ['tosca.relationships.HostedOn']
        expected_capabilities_names = ['host']
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

    def test_translate_nodejs_mongodb(self):
        translate = TOSCATranslator(self.tosca, self.parsed_params)
        output = translate.translate()

        expected_resource = {'mongo_dbms_create_config':
                             {'properties':
                              {'config':
                               {'get_file': 'mongodb/create.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'mongo_dbms_configure_config':
                             {'properties':
                              {'config':
                               {'get_file': 'mongodb/config.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'mongo_dbms_start_config':
                             {'properties':
                              {'config':
                               {'get_file': 'mongodb/start.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'nodejs_create_config':
                             {'properties':
                              {'config':
                               {'get_file': 'nodejs/create.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'nodejs_configure_config':
                             {'properties':
                              {'config':
                               {'get_file': 'nodejs/config.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'nodejs_start_config':
                             {'properties':
                              {'config':
                               {'get_file': 'nodejs/start.sh'},
                               'group': 'script'},
                              'type': 'OS::Heat::SoftwareConfig'},
                             'mongo_dbms_create_deploy':
                             {'properties':
                              {'config':
                               {'get_resource': 'mongo_dbms_create_config'},
                               'server':
                               {'get_resource': 'mongo_server'}},
                              'type': 'OS::Heat::SoftwareDeployment'},
                             'mongo_dbms_configure_deploy':
                             {'type': 'OS::Heat::SoftwareDeployment',
                              'depends_on':
                              ['mongo_dbms_create_deploy'],
                              'properties':
                              {'config':
                               {'get_resource': 'mongo_dbms_configure_config'},
                               'input_values':
                               {'mongodb_ip':
                                {'get_attr':
                                 ['mongo_server', 'networks', 'private', 0]}},
                               'server':
                               {'get_resource': 'mongo_server'}}},
                             'mongo_dbms_start_deploy':
                             {'type': 'OS::Heat::SoftwareDeployment',
                              'depends_on': ['mongo_dbms_configure_deploy'],
                              'properties':
                              {'config':
                               {'get_resource': 'mongo_dbms_start_config'},
                               'server':
                               {'get_resource': 'mongo_server'}}},
                             'nodejs_create_deploy':
                             {'properties':
                              {'config':
                               {'get_resource': 'nodejs_create_config'},
                               'server':
                               {'get_resource': 'app_server'}},
                              'type': 'OS::Heat::SoftwareDeployment'},
                             'nodejs_configure_deploy':
                             {'depends_on':
                              ['nodejs_create_deploy'],
                              'properties':
                              {'config':
                               {'get_resource': 'nodejs_configure_config'},
                               'input_values':
                               {'github_url':
                                'https://github.com/sample.git',
                                'mongodb_ip':
                                {'get_attr':
                                 ['mongo_server', 'networks', 'private', 0]}},
                               'server':
                               {'get_resource': 'app_server'}},
                              'type': 'OS::Heat::SoftwareDeployment'},
                             'nodejs_start_deploy':
                             {'depends_on': ['nodejs_configure_deploy'],
                              'properties':
                              {'config':
                               {'get_resource': 'nodejs_start_config'},
                               'server':
                               {'get_resource': 'app_server'}},
                              'type': 'OS::Heat::SoftwareDeployment'},
                             'app_server':
                             {'properties':
                              {'flavor': 'm1.medium',
                               'image': 'ubuntu-software-config-os-init',
                               'key_name': 'userkey',
                               'user_data_format': 'SOFTWARE_CONFIG'},
                              'type': 'OS::Nova::Server'},
                             'mongo_server':
                             {'properties':
                              {'flavor': 'm1.medium',
                               'image': 'ubuntu-software-config-os-init',
                               'key_name': 'userkey',
                               'user_data_format': 'SOFTWARE_CONFIG'},
                              'type': 'OS::Nova::Server'}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)

        resources = output_dict.get('resources')
        for resource_name in resources:
            translated_value = resources.get(resource_name)
            expected_value = expected_resource.get(resource_name)
            self.assertEqual(translated_value, expected_value)
