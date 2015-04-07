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

    def test_translate_single_storage(self):
        '''TOSCA template with single BlockStorage and Attachment.'''
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/tosca_blockstorage_with_attachment.yaml")

        tosca = ToscaTemplate(tosca_tpl)
        translate = TOSCATranslator(tosca, self.parsed_params)
        output = translate.translate()

        expected_resouce = {'attachesto_1':
                            {'type': 'OS::Cinder::VolumeAttachment',
                             'properties':
                             {'instance_uuid': 'my_server',
                              'location': {'get_param': 'storage_location'},
                              'volume_id': 'my_storage'}}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)

        resources = output_dict.get('resources')
        translated_value = resources.get('attachesto_1')
        expected_value = expected_resouce.get('attachesto_1')
        self.assertEqual(translated_value, expected_value)

        outputs = output_dict['outputs']
        self.assertIn('private_ip', outputs)
        self.assertEqual(
            'Private IP address of the newly created compute instance.',
            outputs['private_ip']['description'])
        self.assertEqual({'get_attr': ['my_server', 'networks', 'private', 0]},
                         outputs['private_ip']['value'])
        self.assertIn('volume_id', outputs)
        self.assertEqual('The volume id of the block storage instance.',
                         outputs['volume_id']['description'])
        self.assertEqual({'get_resource': 'my_storage'},
                         outputs['volume_id']['value'])

    def test_translate_storage_notation1(self):
        '''TOSCA template with single BlockStorage and Attachment.'''
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/tosca_blockstorage_with_attachment_notation1.yaml")

        tosca = ToscaTemplate(tosca_tpl)
        translate = TOSCATranslator(tosca, self.parsed_params)
        output = translate.translate()

        expected_resource_1 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_web_app_tier_1',
                                'location': '/default_location',
                                'volume_id': 'my_storage'}}
        expected_resource_2 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_web_app_tier_2',
                                'location': '/some_other_data_location',
                                'volume_id': 'my_storage'}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)

        resources = output_dict.get('resources')
        self.assertIn('myattachto_1', resources.keys())
        self.assertIn('myattachto_2', resources.keys())
        self.assertIn(expected_resource_1, resources.values())
        self.assertIn(expected_resource_2, resources.values())

    def test_translate_storage_notation2(self):
        '''TOSCA template with single BlockStorage and Attachment.'''
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/tosca_blockstorage_with_attachment_notation2.yaml")

        tosca = ToscaTemplate(tosca_tpl)
        translate = TOSCATranslator(tosca, self.parsed_params)
        output = translate.translate()

        expected_resource_1 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_web_app_tier_1',
                                'location': '/my_data_location',
                                'volume_id': 'my_storage'}}
        expected_resource_2 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_web_app_tier_2',
                                'location': '/some_other_data_location',
                                'volume_id': 'my_storage'}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)

        resources = output_dict.get('resources')
        # Resource name suffix depends on nodetemplates order in dict, which is
        # not certain. So we have two possibilities of resources name.
        if resources.get('storage_attachesto_1_1'):
            self.assertIn('storage_attachesto_1_1', resources.keys())
            self.assertIn('storage_attachesto_2_2', resources.keys())
        else:
            self.assertIn('storage_attachesto_1_2', resources.keys())
            self.assertIn('storage_attachesto_2_1', resources.keys())

        self.assertIn(expected_resource_1, resources.values())
        self.assertIn(expected_resource_2, resources.values())

    def test_translate_multi_storage(self):
        '''TOSCA template with multiple BlockStorage and Attachment.'''
        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/tosca_multiple_blockstorage_with_attachment.yaml")
        tosca = ToscaTemplate(tosca_tpl)
        translated_volume_attachment = []
        translate = TOSCATranslator(tosca, self.parsed_params)
        output = translate.translate()

        expected_resource_1 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_server',
                                'location': {'get_param': 'storage_location'},
                                'volume_id': 'my_storage'}}

        expected_resource_2 = {'type': 'OS::Cinder::VolumeAttachment',
                               'properties':
                               {'instance_uuid': 'my_server2',
                                'location': {'get_param': 'storage_location'},
                                'volume_id': 'my_storage2'}}

        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)
        resources = output_dict.get('resources')
        translated_volume_attachment.append(resources.get('attachesto_1'))
        translated_volume_attachment.append(resources.get('attachesto_2'))
        self.assertIn(expected_resource_1, translated_volume_attachment)
        self.assertIn(expected_resource_2, translated_volume_attachment)
