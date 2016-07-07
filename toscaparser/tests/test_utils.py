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

from toscaparser.tests.base import TestCase
import toscaparser.utils.urlutils
import toscaparser.utils.yamlparser

YAML_LOADER = toscaparser.utils.yamlparser.load_yaml


class UrlUtilsTest(TestCase):

    url_utils = toscaparser.utils.urlutils.UrlUtils

    def test_urlutils_validate_url(self):
        self.assertTrue(self.url_utils.validate_url("http://www.github.com/"))
        self.assertTrue(
            self.url_utils.validate_url("https://github.com:81/a/2/a.b"))
        self.assertTrue(self.url_utils.validate_url("ftp://github.com"))
        self.assertFalse(self.url_utils.validate_url("github.com"))
        self.assertFalse(self.url_utils.validate_url("123"))
        self.assertFalse(self.url_utils.validate_url("a/b/c"))
        self.assertTrue(self.url_utils.validate_url("file:///dir/file.ext"))

    def test_urlutils_join_url(self):
        self.assertEqual(
            self.url_utils.join_url("http://github.com/proj1", "proj2"),
            "http://github.com/proj2")
        self.assertEqual(
            self.url_utils.join_url("http://github.com/proj1/scripts/a.js",
                                    "b.js"),
            "http://github.com/proj1/scripts/b.js")
        self.assertEqual(
            self.url_utils.join_url("http://github.com/proj1/scripts", "b.js"),
            "http://github.com/proj1/b.js")
        self.assertEqual(
            self.url_utils.join_url("http://github.com/proj1/scripts",
                                    "scripts/b.js"),
            "http://github.com/proj1/scripts/b.js")
