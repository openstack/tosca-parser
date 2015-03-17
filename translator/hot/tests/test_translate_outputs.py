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
from translator.toscalib.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate
import translator.toscalib.utils.yamlparser


class ToscaTemplateOutputTest(TestCase):

    def test_translate_output(self):
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../tests/data/tosca_elk.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        translate = TOSCATranslator(tosca, [])
        hot_translation = translate.translate()

        expected_output = {'nodejs_url':
                           {'description': 'URL for the nodejs '
                            'server, http://<IP>:3000',
                            'value':
                            {'get_attr':
                             ['app_server', 'networks', 'private', 0]}},
                           'mongodb_url':
                           {'description': 'URL for the mongodb server.',
                            'value':
                            {'get_attr':
                             ['mongo_server', 'networks', 'private', 0]}}}

        hot_translation_dict = \
            translator.toscalib.utils.yamlparser.simple_parse(hot_translation)

        outputs = hot_translation_dict.get('outputs')
        for resource_name in outputs:
            translated_value = outputs.get(resource_name)
            expected_value = expected_output.get(resource_name)
            self.assertEqual(translated_value, expected_value)
