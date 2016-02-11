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

SECTIONS = (DESCRIPTION, EVENT, SCHEDULE, TARGET_FILTER, CONDITION, ACTION) = \
           ('description', 'event_type', 'schedule',
            'target_filter', 'condition', 'action')
CONDITION_KEYNAMES = (CONTRAINT, PERIOD, EVALUATIONS, METHOD) = \
                     ('constraint', 'period', 'evaluations', 'method')
log = logging.getLogger('tosca')


class Triggers(EntityTemplate):

    '''Triggers defined in policies of topology template'''

    def __init__(self, name, trigger_tpl):
        self.name = name
        self.trigger_tpl = trigger_tpl
        self._validate_keys()
        self._validate_condition()

    def get_description(self):
        return self.trigger_tpl['description']

    def get_event(self):
        return self.trigger_tpl['event_type']

    def get_schedule(self):
        return self.trigger_tpl['schedule']

    def get_target_filter(self):
        return self.trigger_tpl['target_filter']

    def get_condition(self):
        return self.trigger_tpl['condition']

    def get_action(self):
        return self.trigger_tpl['action']

    def _validate_keys(self):
        for key in self.trigger_tpl.keys():
            if key not in SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Triggers "%s"' % self.name,
                                      field=key))

    def _validate_condition(self):
        for key in self.get_condition():
            if key not in CONDITION_KEYNAMES:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Triggers "%s"' % self.name,
                                      field=key))
