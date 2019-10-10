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
import shutil
import zipfile

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import URLException
from toscaparser.common.exception import ValidationError
from toscaparser.prereq.csar import CSAR
from toscaparser.tests.base import TestCase
import toscaparser.utils
from toscaparser.utils.gettextutils import _


class CSARPrereqTest(TestCase):

    base_path = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        super(CSARPrereqTest, self).setUp()
        ExceptionCollector.clear()
        ExceptionCollector.stop()

    def test_file_exists(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_not_there.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" does not exist.') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_file_is_zip(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_not_zip.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" is not a valid zip file.') % path, str(error))

    def test_url_is_zip(self):
        path = "https://github.com/openstack/tosca-parser/raw/master/" \
               "toscaparser/tests/data/CSAR/csar_not_zip.zip"
        csar = CSAR(path, False)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" is not a valid zip file.') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_metadata_file_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_no_metadata_file.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" is not a valid CSAR as it does not contain '
                           'the required file "TOSCA.meta" in the folder '
                           '"TOSCA-Metadata".') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_valid_metadata_file_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wrong_metadata_file.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" is not a valid CSAR as it does not contain '
                           'the required file "TOSCA.meta" in the folder '
                           '"TOSCA-Metadata".') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_metadata_is_yaml(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_metadata_not_yaml.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The file "TOSCA-Metadata/TOSCA.meta" in the CSAR '
                           '"%s" does not contain valid YAML content.') % path,
                         str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_metadata_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_missing_metadata.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The CSAR "%s" is missing the required metadata '
                           '"Entry-Definitions" in '
                           '"TOSCA-Metadata/TOSCA.meta".') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_entry_def_exists(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_invalid_entry_def.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('The "Entry-Definitions" file defined in the CSAR '
                           '"%s" does not exist.') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_invalid_import_path(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_import_path.zip")
        csar = CSAR(path)
        error = self.assertRaises(ImportError, csar.validate)
        self.assertEqual(_('Import "Invalid_import_path/wordpress.yaml" is'
                           ' not valid.'), str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_invalid_import_url(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_import_url.zip")
        csar = CSAR(path)
        error = self.assertRaises(URLException, csar.validate)
        self.assertEqual(_('Failed to reach server '
                           '"https://raw.githubusercontent.com/openstack/'
                           'tosca-parser/master/toscaparser/tests/data/CSAR/'
                           'tosca_single_instance_wordpress/Definitions/'
                           'wordpress1.yaml". Reason is: Not Found.'),
                         str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_invalid_script_path(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_script_path.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValueError, csar.validate)
        self.assertTrue(
            str(error) == _('The resource "Scripts/WordPress/install.sh" does '
                            'not exist.') or
            str(error) == _('The resource "Scripts/WordPress/configure.sh" '
                            'does not exist.'))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_invalid_script_url(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_wordpress_invalid_script_url.zip")
        csar = CSAR(path)
        error = self.assertRaises(URLException, csar.validate)
        self.assertEqual(_('The resource at '
                           '"https://raw.githubusercontent.com/openstack/'
                           'tosca-parser/master/toscaparser/tests/data/CSAR/'
                           'tosca_single_instance_wordpress/Scripts/WordPress/'
                           'install1.sh" cannot be accessed.'),
                         str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_valid_csar(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        self.assertTrue(csar.validate())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_valid_csar_with_url_import_and_script(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_wordpress_with_url"
                            "_import_and_script.zip")
        csar = CSAR(path)
        self.assertTrue(csar.validate())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_metadata_invalid_csar(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_metadata_not_yaml.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.get_author)
        self.assertEqual(_('The file "TOSCA-Metadata/TOSCA.meta" in the CSAR '
                           '"%s" does not contain valid YAML content.') % path,
                         str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_metadata_valid_csar(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        expected_meta = {'TOSCA-Meta-File-Version': 1.0,
                         'CSAR-Version': 1.1,
                         'Created-By': 'OASIS TOSCA TC',
                         'Entry-Definitions': 'tosca_helloworld.yaml'}
        self.assertEqual(expected_meta, csar.get_metadata(),
                         'The extracted metadata of the CSAR %(csar)s does '
                         'not match the expected metadata %(meta)s'
                         % {'csar': path, 'meta': expected_meta.__str__()})
        self.assertEqual(1.1, csar.get_version())
        self.assertEqual('OASIS TOSCA TC', csar.get_author())
        self.assertEqual('tosca_helloworld.yaml', csar.get_main_template())
        self.assertEqual('Template for deploying a single server with '
                         'predefined properties.', csar.get_description())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_main_template(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data/tosca_helloworld.yaml")
        expected_yaml = toscaparser.utils.yamlparser.load_yaml(yaml_file)
        self.assertEqual(expected_yaml, csar.get_main_template_yaml())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_decompress(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_hello_world.zip")
        csar = CSAR(path)
        csar.decompress()
        zf = zipfile.ZipFile(path)
        for name in zf.namelist():
            tmp_path = os.path.join(csar.temp_dir, name)
            self.assertTrue(os.path.isdir(tmp_path) or
                            os.path.isfile(tmp_path))
        shutil.rmtree(csar.temp_dir)
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_alternate_csar_extension(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_elk.csar")
        csar = CSAR(path)
        self.assertTrue(csar.validate())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_with_root_level_yaml(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_root_level_yaml.zip")
        csar = CSAR(path)
        yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data/CSAR/root_level_file.yaml")
        expected_yaml = toscaparser.utils.yamlparser.load_yaml(yaml_file)
        self.assertEqual(expected_yaml, csar.get_main_template_yaml())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_with_multiple_root_level_yaml_files_error(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_two_root_level_yaml.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('CSAR file should contain only one root level'
                           ' yaml file. Found "2" yaml file(s).'), str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_with_root_level_yaml_and_tosca_metadata(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_root_level_"
                            "yaml_and_tosca_metadata.zip")
        csar = CSAR(path)
        yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data/CSAR/tosca_meta_file.yaml")
        expected_yaml = toscaparser.utils.yamlparser.load_yaml(yaml_file)
        self.assertEqual(expected_yaml, csar.get_main_template_yaml())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_root_yaml_with_tosca_definition_1_0_error(self):
        path = os.path.join(self.base_path, "data/CSAR/csar_root_yaml"
                                            "_with_tosca_definition1_0.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValidationError, csar.validate)
        self.assertEqual(_('"%s" is not a valid CSAR as it does not contain'
                           ' the required file "TOSCA.meta" in the folder '
                           '"TOSCA-Metadata".') % path, str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_with_multilevel_imports_valid(self):
        path = os.path.join(
            self.base_path,
            "data/CSAR/csar_valid_multilevel_imports_validation.zip")
        csar = CSAR(path)
        yaml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "data/CSAR/multi_level_imports_response.yaml")
        expected_yaml = toscaparser.utils.yamlparser.load_yaml(yaml_file)
        self.assertEqual(expected_yaml, csar.get_main_template_yaml())
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))

    def test_csar_with_multilevel_imports_invalid(self):
        path = os.path.join(self.base_path,
                            "data/CSAR/csar_invalid_multilevel"
                            "_imports_validation.zip")
        csar = CSAR(path)
        error = self.assertRaises(ValueError, csar.validate)
        self.assertEqual(_(
            'The resource "%s" does '
            'not exist.') % 'Files/images/'
                            'cirros-0.4.0-x86_64-disk.img', str(error))
        self.assertTrue(csar.temp_dir is None or
                        not os.path.exists(csar.temp_dir))
