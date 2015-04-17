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
