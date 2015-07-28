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

import json
from translator.common.utils import TranslationUtils
from translator.tests.base import TestCase


class ToscaHotTranslationTest(TestCase):

    def test_hot_translate_single_server(self):
        tosca_file = \
            '../toscalib/tests/data/tosca_single_server.yaml'
        hot_file = '../toscalib/tests/data/hot_output/hot_single_server.yaml'
        params = {'cpus': 1}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_wordpress_single_instance(self):
        tosca_file = \
            '../toscalib/tests/data/tosca_single_instance_wordpress.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
            'hot_single_instance_wordpress.yaml'
        params = {'db_name': 'wordpress',
                  'db_user': 'wp_user',
                  'db_pwd': 'wp_pass',
                  'db_root_pwd': 'passw0rd',
                  'db_port': 3366,
                  'cpus': 8}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_helloworld(self):
        tosca_file = \
            '../toscalib/tests/data/tosca_helloworld.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
            'hot_tosca_helloworld.yaml'
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   {})
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_host_assignment(self):
        tosca_file = \
            '../toscalib/tests/data/test_host_assignment.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
            'hot_host_assignment.yaml'
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   {})
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_elk(self):
        tosca_file = \
            '../toscalib/tests/data/tosca_elk.yaml'
        hot_file = '../toscalib/tests/data/hot_output/hot_elk.yaml'
        params = {'github_url':
                  'http://github.com/paypal/rest-api-sample-app-nodejs.git',
                  'my_cpus': 4}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_nodejs_mongodb_two_instances(self):
        tosca_file = \
            '../toscalib/tests/data/tosca_nodejs_mongodb_two_instances.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
                   'hot_nodejs_mongodb_two_instances.yaml'
        params = {'github_url':
                  'http://github.com/paypal/rest-api-sample-app-nodejs.git',
                  'my_cpus': 4}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_blockstorage_with_attachment(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_blockstorage_with_attachment.yaml'
        hot_file = '../toscalib/tests/data/hot_output/storage/' \
                   'hot_blockstorage_with_attachment.yaml'
        params = {'cpus': 1,
                  'storage_location': '/dev/vdc',
                  'storage_size': '2000 MB',
                  'storage_snapshot_id': 'ssid'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_blockstorage_with_custom_relationship_type(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_blockstorage_with_custom_relationship_type.yaml'
        hot_file = '../toscalib/tests/data/hot_output/storage/' \
                   'hot_blockstorage_with_custom_relationship_type.yaml'
        params = {'cpus': 1,
                  'storage_location': '/dev/vdc',
                  'storage_size': '1 GB',
                  'storage_snapshot_id': 'ssid'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_blockstorage_with_relationship_template(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_blockstorage_with_relationship_template.yaml'
        hot_file = '../toscalib/tests/data/hot_output/storage/' \
                   'hot_blockstorage_with_relationship_template.yaml'
        params = {'cpus': 1,
                  'storage_location': '/dev/vdc',
                  'storage_size': '1 GB'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_blockstorage_with_attachment_notation1(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_blockstorage_with_attachment_notation1.yaml'
        hot_file1 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_blockstorage_with_attachment_notation1_alt1.yaml'
        hot_file2 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_blockstorage_with_attachment_notation1_alt2.yaml'
        params = {'cpus': 1,
                  'storage_location': 'some_folder',
                  'storage_size': '1 GB',
                  'storage_snapshot_id': 'ssid'}
        diff1 = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                    hot_file1,
                                                                    params)
        try:
            self.assertEqual({}, diff1, '<difference> : ' +
                             json.dumps(diff1, indent=4,
                                        separators=(', ', ': ')))
        except Exception:
            diff2 = TranslationUtils.compare_tosca_translation_with_hot(
                tosca_file, hot_file2, params)
            self.assertEqual({}, diff2, '<difference> : ' +
                             json.dumps(diff2, indent=4,
                                        separators=(', ', ': ')))

    def test_hot_translate_blockstorage_with_attachment_notation2(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_blockstorage_with_attachment_notation2.yaml'
        hot_file1 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_blockstorage_with_attachment_notation2_alt1.yaml'
        hot_file2 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_blockstorage_with_attachment_notation2_alt2.yaml'
        params = {'cpus': 1,
                  'storage_location': '/dev/vdc',
                  'storage_size': '1 GB',
                  'storage_snapshot_id': 'ssid'}
        diff1 = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                    hot_file1,
                                                                    params)
        try:
            self.assertEqual({}, diff1, '<difference> : ' +
                             json.dumps(diff1, indent=4,
                                        separators=(', ', ': ')))
        except Exception:
            diff2 = TranslationUtils.compare_tosca_translation_with_hot(
                tosca_file, hot_file2, params)
            self.assertEqual({}, diff2, '<difference> : ' +
                             json.dumps(diff2, indent=4,
                                        separators=(', ', ': ')))

    def test_hot_translate_multiple_blockstorage_with_attachment(self):
        tosca_file = \
            '../toscalib/tests/data/storage/' \
            'tosca_multiple_blockstorage_with_attachment.yaml'
        hot_file1 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_multiple_blockstorage_with_attachment_alt1.yaml'
        hot_file2 = '../toscalib/tests/data/hot_output/storage/' \
                    'hot_multiple_blockstorage_with_attachment_alt2.yaml'
        params = {'cpus': 1,
                  'storage_location': '/dev/vdc',
                  'storage_size': '1 GB',
                  'storage_snapshot_id': 'ssid'}
        diff1 = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                    hot_file1,
                                                                    params)
        try:
            self.assertEqual({}, diff1, '<difference> : ' +
                             json.dumps(diff1, indent=4,
                                        separators=(', ', ': ')))
        except Exception:
            diff2 = TranslationUtils.compare_tosca_translation_with_hot(
                tosca_file, hot_file2, params)
            self.assertEqual({}, diff2, '<difference> : ' +
                             json.dumps(diff2, indent=4,
                                        separators=(', ', ': ')))

    def test_hot_translate_single_object_store(self):
        tosca_file = \
            '../toscalib/tests/data/storage/tosca_single_object_store.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
                   'hot_single_object_store.yaml'
        params = {'objectstore_name': 'myobjstore'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_one_server_one_network(self):
        tosca_file = \
            '../toscalib/tests/data/network/tosca_one_server_one_network.yaml'
        hot_file = '../toscalib/tests/data/hot_output/network/' \
                   'hot_one_server_one_network.yaml'
        params = {'network_name': 'private_net'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_server_on_existing_network(self):
        tosca_file = '../toscalib/tests/data/network/' \
                     'tosca_server_on_existing_network.yaml'
        hot_file = '../toscalib/tests/data/hot_output/network/' \
                   'hot_server_on_existing_network.yaml'
        params = {'network_name': 'private_net'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_two_servers_one_network(self):
        tosca_file = \
            '../toscalib/tests/data/network/tosca_two_servers_one_network.yaml'
        hot_file = '../toscalib/tests/data/hot_output/network/' \
                   'hot_two_servers_one_network.yaml'
        params = {'network_name': 'my_private_net',
                  'network_cidr': '10.0.0.0/24',
                  'network_start_ip': '10.0.0.100',
                  'network_end_ip': '10.0.0.150'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_one_server_three_networks(self):
        tosca_file = '../toscalib/tests/data/network/' \
                     'tosca_one_server_three_networks.yaml'
        hot_file = '../toscalib/tests/data/hot_output/network/' \
                   'hot_one_server_three_networks.yaml'
        params = {}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_software_component(self):
        tosca_file = '../toscalib/tests/data/tosca_software_component.yaml'
        hot_file = '../toscalib/tests/data/hot_output/' \
                   'hot_software_component.yaml'
        params = {'cpus': '1',
                  'download_url': 'http://www.software.com/download'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))

    def test_hot_translate_web_application(self):
        tosca_file = '../toscalib/tests/data/tosca_web_application.yaml'
        hot_file = '../toscalib/tests/data/hot_output/hot_web_application.yaml'
        params = {'cpus': '2', 'context_root': 'my_web_app'}
        diff = TranslationUtils.compare_tosca_translation_with_hot(tosca_file,
                                                                   hot_file,
                                                                   params)
        self.assertEqual({}, diff, '<difference> : ' +
                         json.dumps(diff, indent=4, separators=(', ', ': ')))
