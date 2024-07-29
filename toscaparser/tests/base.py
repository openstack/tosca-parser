# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import codecs
import os

import fixtures
import testscenarios
import testtools

from toscaparser.tests import utils
from toscaparser.tosca_template import ToscaTemplate

_TRUE_VALUES = ('True', 'true', '1', 'yes')


class TestCase(testscenarios.TestWithScenarios, testtools.TestCase):

    """Test case base class for all unit tests."""

    def setUp(self):
        """Run before each test method to initialize test environment."""

        super(TestCase, self).setUp()
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

        self.useFixture(fixtures.NestedTempfile())
        self.useFixture(fixtures.TempHomeDir())

        if os.environ.get('OS_STDOUT_CAPTURE') in _TRUE_VALUES:
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if os.environ.get('OS_STDERR_CAPTURE') in _TRUE_VALUES:
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))

        self.log_fixture = self.useFixture(fixtures.FakeLogger())

    def _load_template(self, filename):
        """Load a Tosca template from tests data folder.

        :param filename: Tosca template file name to load.
        :return: ToscaTemplate
        """
        return ToscaTemplate(os.path.join(
            utils.get_sample_test_path('data'), filename))


class MockTestClass():
    comp_urldict = {}

    def mock_urlopen_method(self, path: str):
        """Open local file instead of opening file at external URL.

        When using this method, you need to set the URL to be replaced and the
        file path to open instead in "comp_urldict".
        This method checks whether the URL passed as an argument exists in the
        key of "comp_urldict", and if it exists, opens the file with the path
        set in the value of "comp_urldict".
        """
        if self.comp_urldict.get(path):
            file_path = self.comp_urldict.get(path)
        else:
            file_path = path

        return codecs.open(file_path, encoding='utf-8', errors='strict')
