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

from collections import OrderedDict

from translator.hot.syntax.hot_parameter import CONSTRAINTS
from translator.hot.syntax.hot_parameter import DEFAULT
from translator.hot.syntax.hot_parameter import DESCRIPTION
from translator.hot.syntax.hot_parameter import HIDDEN
from translator.hot.syntax.hot_parameter import HotParameter
from translator.hot.syntax.hot_parameter import LABEL
from translator.hot.syntax.hot_parameter import TYPE
from translator.toscalib.tests.base import TestCase

TEST_CONSTRAINTS = {'equal': 'allowed_values', 'greater_than': 'range'}


class HotParameterTest(TestCase):

    # This test ensures the variables set during the creation of a HotParameter
    # object are returned in an OrderedDict when calling get_dict_output().
    def test_dict_output(self):
        name = 'HotParameterTest'
        hot_parameter = HotParameter(name, 'Type',
                                     label='Label',
                                     description='Description',
                                     default='Default',
                                     hidden=True,
                                     constraints=TEST_CONSTRAINTS)
        expected_dict = OrderedDict([(TYPE, 'Type'), (LABEL, 'Label'),
                                     (DESCRIPTION, 'Description'),
                                     (DEFAULT, 'Default'), (HIDDEN, True),
                                     (CONSTRAINTS, TEST_CONSTRAINTS)])

        self.assertEqual(hot_parameter.get_dict_output()[name], expected_dict)
