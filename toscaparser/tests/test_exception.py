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

from toscaparser.common import exception
from toscaparser.tests.base import TestCase
from toscaparser.utils.gettextutils import _


class ExceptionTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        exception.TOSCAException.set_fatal_format_exception(False)

    def test_message(self):
        ex = exception.MissingRequiredFieldError(what='Template',
                                                 required='type')
        self.assertEqual(_('Template is missing required field "type".'),
                         ex.__str__())

    def test_set_flag(self):
        exception.TOSCAException.set_fatal_format_exception('True')
        self.assertFalse(
            exception.TOSCAException._FATAL_EXCEPTION_FORMAT_ERRORS)

    def test_format_error(self):
        ex = exception.UnknownFieldError(what='Template')
        self.assertEqual(_('An unknown exception occurred.'), ex.__str__(),)
        self.assertRaises(KeyError, self._formate_exception)

    def _formate_exception(self):
        exception.UnknownFieldError.set_fatal_format_exception(True)
        raise exception.UnknownFieldError(what='Template')
