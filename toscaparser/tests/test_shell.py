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

from toscaparser.common import exception
import toscaparser.shell as shell
from toscaparser.tests.base import TestCase
from toscaparser.utils.gettextutils import _


class ShellTest(TestCase):

    tosca_helloworld = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/tosca_helloworld.yaml")

    errornous_template = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/test_multiple_validation_errors.yaml")

    def test_missing_arg(self):
        self.assertRaises(SystemExit, shell.main, '')

    def test_invalid_arg(self):
        self.assertRaises(SystemExit, shell.main, 'parse me')

    def test_template_not_exist(self):
        error = self.assertRaises(
            ValueError, shell.main, ['--template-file=template.txt'])
        self.assertEqual(_('"template.txt" is not a valid file.'), str(error))

    def test_template_invalid(self):
        arg = '--template-file=' + self.errornous_template
        self.assertRaises(exception.ValidationError, shell.main, [arg])

    def test_template_valid(self):
        arg = '--template-file=' + self.tosca_helloworld
        try:
            shell.main([arg])
        except Exception:
            self.fail(_('The program raised an exception unexpectedly.'))
