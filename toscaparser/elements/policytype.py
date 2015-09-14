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

from toscaparser.elements.statefulentitytype import StatefulEntityType


class PolicyType(StatefulEntityType):
    '''TOSCA built-in policies type.'''

    def __init__(self, ptype, custom_def=None):
        super(PolicyType, self).__init__(ptype, self.POLICY_PREFIX,
                                         custom_def)
        self.type = ptype
        self.properties = None
        if self.PROPERTIES in self.defs:
            self.properties = self.defs[self.PROPERTIES]
        self.parent_policies = self._get_parent_policies()

    def _get_parent_policies(self):
        policies = {}
        parent_policy = self.parent_type
        if parent_policy:
            while parent_policy != 'tosca.policies.Root':
                policies[parent_policy] = self.TOSCA_DEF[parent_policy]
                parent_policy = policies[parent_policy]['derived_from']
        return policies

    @property
    def parent_type(self):
        '''Return a policy this policy is derived from.'''
        return self.derived_from(self.defs)

    def get_policy(self, name):
        '''Return the definition of a policy field by name.'''
        if name in self.defs:
            return self.defs[name]
