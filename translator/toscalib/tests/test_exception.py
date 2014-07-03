# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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

from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import TOSCAException
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.tests.base import TestCase


class ExceptionTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        TOSCAException.set_fatal_format_exception(False)

    def test_message(self):
        ex = MissingRequiredFieldError(what='Template', required='type')
        self.assertEqual('Template is missing required field: "type".',
                         ex.__str__())

    def test_set_flag(self):
        TOSCAException.set_fatal_format_exception('True')
        self.assertFalse(TOSCAException._FATAL_EXCEPTION_FORMAT_ERRORS)

    def test_format_error(self):
        ex = UnknownFieldError(what='Template')
        self.assertEqual('An unknown exception occurred.', ex.__str__(),)
        self.assertRaises(KeyError, self._formate_exception)

    def _formate_exception(self):
        UnknownFieldError.set_fatal_format_exception(True)
        raise UnknownFieldError(what='Template')
