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

from toscaparser.common.exception import ValidationError
from toscaparser.prereq.csar import CSAR
from toscaparser.tests.base import TestCase
from toscaparser.utils.gettextutils import _


class CSARPrereqTest(TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def test_file_exists(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_not_there.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file %s does not exist.') % path, str(error))

    def test_file_is_zip(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_not_zip.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file %s is not a valid zip file.') % path,
                         str(error))

    def test_metadata_file_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_no_metadata_file.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file %s is not a valid CSAR as it does not '
                           'contain the required file "TOSCA.meta" in the '
                           'folder "TOSCA-Metadata".') % path, str(error))

    def test_valid_metadata_file_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wrong_metadata_file.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file %s is not a valid CSAR as it does not '
                           'contain the required file "TOSCA.meta" in the '
                           'folder "TOSCA-Metadata".') % path, str(error))

    def test_metadata_is_yaml(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_metadata_not_yaml.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file "TOSCA-Metadata/TOSCA.meta" in %s does '
                           'not contain valid YAML content.') % path,
                         str(error))

    def test_metadata_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_missing_metadata.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The CSAR file "%s" is missing the required '
                           'metadata "Entry-Definitions" in '
                           '"TOSCA-Metadata/TOSCA.meta".') % path, str(error))

    def test_entry_def_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_invalid_entry_def.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The "Entry-Definitions" file defined in the CSAR '
                           '"%s" does not exist.') % path, str(error))

    def test_valid_csar(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        self.assertIsNone(csar.validate())

    def test_metadata_invalid_csar(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_metadata_not_yaml.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.get_author)
        self.assertEqual(_('The file "TOSCA-Metadata/TOSCA.meta" in %s does '
                           'not contain valid YAML content.') % path,
                         str(error))

    def test_metadata_valid_csar(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        expected_meta = {'TOSCA-Meta-File-Version': 1.0,
                         'CSAR-Version': 1.1,
                         'Created-By': 'OASIS TOSCA TC',
                         'Entry-Definitions': 'tosca_helloworld.yaml'}
        self.assertEqual(expected_meta, csar.get_metadata(),
                         'The extracted metadata of the CSAR file %(csar)s '
                         'does not match the expected metadata %(meta)s'
                         % {'csar': path, 'meta': expected_meta.__str__()})
        self.assertEqual(1.1, csar.get_version())
        self.assertEqual('OASIS TOSCA TC', csar.get_author())
        self.assertEqual('tosca_helloworld.yaml', csar.get_main_template())
