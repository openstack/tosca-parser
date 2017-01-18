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


import logging

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import UnknownFieldError
from toscaparser.entity_template import EntityTemplate
from toscaparser.triggers import Triggers
from toscaparser.utils import validateutils


SECTIONS = (TYPE, METADATA, DESCRIPTION, PROPERTIES, TARGETS, TRIGGERS) = \
           ('type', 'metadata', 'description',
            'properties', 'targets', 'triggers')

log = logging.getLogger('tosca')


class Policy(EntityTemplate):
    '''Policies defined in Topology template.'''
    def __init__(self, name, policy, targets=None, targets_type=None,
                 custom_def=None):
        super(Policy, self).__init__(name,
                                     policy,
                                     'policy_type',
                                     custom_def)
        self.meta_data = None
        if self.METADATA in policy:
            self.meta_data = policy.get(self.METADATA)
            validateutils.validate_map(self.meta_data)
        self.targets_list = targets
        self.targets_type = targets_type
        self.triggers = self._triggers(policy.get(TRIGGERS))
        self.properties = None
        if 'properties' in policy:
            self.properties = policy['properties']
        self._validate_keys()

    @property
    def targets(self):
        return self.entity_tpl.get('targets')

    @property
    def description(self):
        return self.entity_tpl.get('description')

    @property
    def metadata(self):
        return self.entity_tpl.get('metadata')

    def get_targets_type(self):
        return self.targets_type

    def get_targets_list(self):
        return self.targets_list

    def _triggers(self, triggers):
        triggerObjs = []
        if triggers:
            for name, trigger_tpl in triggers.items():
                triggersObj = Triggers(name, trigger_tpl)
                triggerObjs.append(triggersObj)
        return triggerObjs

    def _validate_keys(self):
        for key in self.entity_tpl.keys():
            if key not in SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Policy "%s"' % self.name,
                                      field=key))
