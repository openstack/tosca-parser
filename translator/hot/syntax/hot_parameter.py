#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import OrderedDict

KEYS = (TYPE, DESCRIPTION, DEFAULT, CONSTRAINTS, HIDDEN, LABEL) = \
       ('type', 'description', 'default', 'constraints', 'hidden', 'label')


class HotParameter(object):
    '''Attributes for HOT parameter section.'''

    def __init__(self, name, type, label=None, description=None, default=None,
                 hidden=None, constraints=None):
        self.name = name
        self.type = type
        self.label = label
        self.description = description
        self.default = default
        self.hidden = hidden
        self.constraints = constraints

    def get_dict_output(self):
        param_sections = OrderedDict()
        param_sections[TYPE] = self.type
        if self.label:
            param_sections[LABEL] = self.label
        if self.description:
            param_sections[DESCRIPTION] = self.description
        if self.default:
            param_sections[DEFAULT] = self.default
        if self.hidden:
            param_sections[HIDDEN] = self.hidden
        if self.constraints:
            param_sections[CONSTRAINTS] = self.constraints

        return {self.name: param_sections}
