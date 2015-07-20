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


class ToscaBlockStorageTest(TestCase):
    parsed_params = {'storage_snapshot_id': 'test_id',
                     'storage_location': '/test', 'cpus': '1',
                     'storage_size': '1'}

    def test_translate_multi_storage(self):
        '''TOSCA template with multiple BlockStorage and Attachment.'''
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../toscalib/tests/data/storage/"
            "tosca_multiple_blockstorage_with_attachment.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        translated_volume_attachment = []
        translate = TOSCATranslator(tosca, self.parsed_params)
        output = translate.translate()

        expected_resource_1 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': {'get_resource': 'my_server'},
                                'mountpoint':
                                {'get_param': 'storage_location'},
                                'volume_id': {'get_resource': 'my_storage'}}}

        expected_resource_2 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid':
                                {'get_resource': 'my_server2'},
                                'mountpoint':
                                {'get_param': 'storage_location'},
                                'volume_id': {'get_resource': 'my_storage2'}}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)
        resources = output_dict.get('resources')
        translated_volume_attachment.append(resources.get('attachesto_1'))
        translated_volume_attachment.append(resources.get('attachesto_2'))
        self.assertIn(expected_resource_1, translated_volume_attachment)
        self.assertIn(expected_resource_2, translated_volume_attachment)
