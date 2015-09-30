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
import zipfile

from toscaparser.common.exception import URLException
from toscaparser.common.exception import ValidationError
from toscaparser.prereq.csar import CSAR
from toscaparser.tests.base import TestCase
import toscaparser.utils
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

    def test_csar_invalid_import_path(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_import_path.zip")
        csar = CSAR(path)
        error = self.assertRaises(ImportError, csar.validate)
        self.assertEqual(_('Import Definitions/wordpress.yaml is not valid'),
                         str(error))

    def test_csar_invalid_import_url(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_import_url.zip")
        csar = CSAR(path)
        error = self.assertRaises(URLException, csar.validate)
        self.assertEqual(_('URLException "Failed to reach server '
                           'https://raw.githubusercontent.com/openstack/'
                           'tosca-parser/master/toscaparser/tests/data/CSAR/'
                           'tosca_single_instance_wordpress/Definitions/'
                           'wordpress1.yaml. Reason is : Not Found".'),
                         str(error))

    def test_csar_invalid_script_path(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_script_path.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValueError, csar.validate)
        self.assertTrue(
            str(error) == _('The resource Scripts/WordPress/install.sh does '
                            'not exist.') or
            str(error) == _('The resource Scripts/WordPress/configure.sh does '
                            'not exist.'))

    def test_csar_invalid_script_url(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_script_url.zip")
        csar = CSAR(path)
        error = self.assertRaises(URLException, csar.validate)
        self.assertEqual(_('URLException "The resource at '
                           'https://raw.githubusercontent.com/openstack/'
                           'tosca-parser/master/toscaparser/tests/data/CSAR/'
                           'tosca_single_instance_wordpress/Scripts/WordPress/'
                           'install1.sh cannot be accessed".'),
                         str(error))

    def test_valid_csar(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        self.assertIsNone(csar.validate())

    def test_valid_csar_with_url_import_and_script(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_wordpress_with_url"
                            "_import_and_script.zip")
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
        self.assertEqual('Template for deploying a single server with '
                         'predefined properties.', csar.get_description())

    def test_csar_main_template(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data/tosca_helloworld.yaml")
        expected_yaml = toscaparser.utils.yamlparser.load_yaml(yaml_file)
        self.assertEqual(expected_yaml, csar.get_main_template_yaml())

    def test_decompress(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        tmp_dir = csar.decompress()
        zf = zipfile.ZipFile(path)
        for name in zf.namelist():
            tmp_path = os.path.join(tmp_dir, name)
            self.assertTrue(os.path.isdir(tmp_path) or
                            os.path.isfile(tmp_path))
