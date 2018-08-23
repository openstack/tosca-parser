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

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTypeError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.elements.statefulentitytype import StatefulEntityType
from toscaparser.utils.validateutils import TOSCAVersionProperty


class PolicyType(StatefulEntityType):

    '''TOSCA built-in policies type.'''
    SECTIONS = (DERIVED_FROM, METADATA, PROPERTIES, VERSION, DESCRIPTION,
                TARGETS, TRIGGERS, TYPE, RESERVATION) = \
               ('derived_from', 'metadata', 'properties', 'version',
                'description', 'targets', 'triggers', 'type', 'reservation')

    def __init__(self, ptype, custom_def=None):
        super(PolicyType, self).__init__(ptype, self.POLICY_PREFIX,
                                         custom_def)
        self.type = ptype
        self.custom_def = custom_def
        self._validate_keys()

        self.meta_data = None
        if self.METADATA in self.defs:
            self.meta_data = self.defs[self.METADATA]
            self._validate_metadata(self.meta_data)

        self.properties = None
        if self.PROPERTIES in self.defs:
            self.properties = self.defs[self.PROPERTIES]
        self.parent_policies = self._get_parent_policies()

        self.policy_version = None
        if self.VERSION in self.defs:
            self.policy_version = TOSCAVersionProperty(
                self.defs[self.VERSION]).get_version()

        self.policy_description = self.defs[self.DESCRIPTION] \
            if self.DESCRIPTION in self.defs else None

        self.targets_list = None
        if self.TARGETS in self.defs:
            self.targets_list = self.defs[self.TARGETS]
            self._validate_targets(self.targets_list, custom_def)

        self.reservation = None
        if self.RESERVATION in self.defs:
            self.reservation = self.defs[self.RESERVATION]

    def _get_parent_policies(self):
        policies = {}
        parent_policy = self.parent_type.type if self.parent_type else None
        if parent_policy:
            while parent_policy != 'tosca.policies.Root':
                if parent_policy in self.TOSCA_DEF:
                    policies[parent_policy] = self.TOSCA_DEF[parent_policy]
                    parent_policy = policies[parent_policy]['derived_from']
                elif self.custom_def and parent_policy in self.custom_def:
                    policies[parent_policy] = self.custom_def[parent_policy]
                    parent_policy = policies[parent_policy]['derived_from']
        return policies

    @property
    def parent_type(self):
        '''Return a policy statefulentity of this node is derived from.'''
        if not hasattr(self, 'defs'):
            return None
        ppolicy_entity = self.derived_from(self.defs)
        if ppolicy_entity:
            return PolicyType(ppolicy_entity, self.custom_def)

    def get_policy(self, name):
        '''Return the definition of a policy field by name.'''
        if name in self.defs:
            return self.defs[name]

    @property
    def targets(self):
        '''Return targets.'''
        return self.targets_list

    @property
    def description(self):
        return self.policy_description

    @property
    def version(self):
        return self.policy_version

    def _validate_keys(self):
        for key in self.defs.keys():
            if key not in self.SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Policy "%s"' % self.type,
                                      field=key))

    def _validate_targets(self, targets_list, custom_def):
        for nodetype in targets_list:
            if nodetype not in custom_def:
                ExceptionCollector.appendException(
                    InvalidTypeError(what='"%s" defined in targets for '
                                     'policy "%s"' % (nodetype, self.type)))

    def _validate_metadata(self, meta_data):
        if not meta_data.get('type') in ['map', 'tosca:map']:
            ExceptionCollector.appendException(
                InvalidTypeError(what='"%s" defined in policy for '
                                 'metadata' % (meta_data.get('type'))))

        for entry_schema, entry_schema_type in meta_data.items():
            if isinstance(entry_schema_type, dict) and not \
                    entry_schema_type.get('type') == 'string':
                ExceptionCollector.appendException(
                    InvalidTypeError(what='"%s" defined in policy for '
                                     'metadata "%s"'
                                     % (entry_schema_type.get('type'),
                                        entry_schema)))
