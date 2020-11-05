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
from toscaparser.utils import validateutils

SECTIONS = (DESCRIPTION, EVENT, SCHEDULE, METRIC, METADATA,
            TARGET_FILTER, CONDITION, ACTION) = \
           ('description', 'event_type', 'schedule', 'metric',
            'metadata', 'target_filter', 'condition', 'action')
CONDITION_KEYNAMES = (CONSTRAINT, GRANULARITY, EVALUATIONS, AGGREGATION_METHOD,
                      THRESHOLD, COMPARISON_OPERATOR, RESOURCE_TYPE, STATE) = \
                     ('constraint', 'granularity', 'evaluations',
                      'aggregation_method', 'threshold', 'comparison_operator',
                      'resource_type', 'state')
log = logging.getLogger('tosca')


class Triggers(EntityTemplate):

    '''Triggers defined in policies of topology template'''

    def __init__(self, name, trigger_tpl):
        """
        Initialize the input.

        Args:
            self: (todo): write your description
            name: (str): write your description
            trigger_tpl: (todo): write your description
        """
        self.name = name
        self.trigger_tpl = trigger_tpl
        self._validate_keys()
        self._validate_condition()
        self._validate_input()

    def get_description(self):
        """
        Get description of the trigger.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['description']

    def get_event(self):
        """
        Get the event.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['event_type']

    def get_schedule(self):
        """
        Return the schedule.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['schedule']

    def get_target_filter(self):
        """
        Return the filter filter.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['target_filter']

    def get_condition(self):
        """
        Get the current condition.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['condition']

    def get_action(self):
        """
        Return the action of the trigger.

        Args:
            self: (todo): write your description
        """
        return self.trigger_tpl['action']

    def _validate_keys(self):
        """
        Validate all the fields are_keys.

        Args:
            self: (todo): write your description
        """
        for key in self.trigger_tpl.keys():
            if key not in SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Triggers "%s"' % self.name,
                                      field=key))

    def _validate_condition(self):
        """
        Validate the condition condition.

        Args:
            self: (todo): write your description
        """
        for key in self.get_condition():
            if key not in CONDITION_KEYNAMES:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Triggers "%s"' % self.name,
                                      field=key))

    def _validate_input(self):
        """
        Validate the input.

        Args:
            self: (todo): write your description
        """
        for key, value in self.get_condition().items():
            if key in [GRANULARITY, EVALUATIONS]:
                validateutils.validate_integer(value)
            elif key == THRESHOLD:
                validateutils.validate_numeric(value)
            elif key in [METRIC, AGGREGATION_METHOD]:
                validateutils.validate_string(value)
