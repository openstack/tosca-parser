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

from translator.common.utils import CompareUtils
from translator.hot.tosca_translator import TOSCATranslator
from translator.toscalib.tests.base import TestCase
from translator.toscalib.tosca_template import ToscaTemplate


class ToscaTemplateOutputOrderTest(TestCase):

    def test_translate_output_order(self):
        tosca_yaml_file = "data/tosca_single_server.yaml"
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            tosca_yaml_file)
        parsed_params = {'cpus': 2}
        tosca = ToscaTemplate(tosca_tpl)
        translate = TOSCATranslator(tosca, parsed_params)
        hot_translated_output = translate.translate()

        # load expected hot yaml file
        hot_yaml_file = "data/hot_output/hot_single_server.yaml"
        hot_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            hot_yaml_file)
        with open(hot_tpl) as f:
            hot_expected_output = f.read()

        # compare generated and expected hot templates
        status = CompareUtils.compare_hot_yamls(hot_translated_output,
                                                hot_expected_output)
        self.assertEqual(status, True)
