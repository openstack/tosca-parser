# Copyright (C) 2018 NTT DATA
# All Rights Reserved.
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

import logging

from toscaparser.common.exception import UnknownFieldError
from toscaparser.entity_template import EntityTemplate
from toscaparser.entity_template import MissingRequiredFieldError


SECTIONS = (START_ACTIONS, BEFORE_END_ACTIONS, END_ACTIONS, PROPERTIES) = \
           ('start_actions', 'before_end_actions', 'end_actions', 'properties')

log = logging.getLogger('tosca')


class Reservation(EntityTemplate):

    '''Reservation defined in policies of topology template'''

    def __init__(self, reservation_tpl):
        self.reservation_tpl = reservation_tpl
        self._validate_keys()
        self._validate_missing_field()

    def _validate_keys(self):
        for key in self.reservation_tpl.keys():
            if key not in SECTIONS:
                raise UnknownFieldError(what='Reservation', field=key)

    def _validate_missing_field(self):
        for key in SECTIONS:
            if key not in self.reservation_tpl.keys():
                raise MissingRequiredFieldError(what='Reservation',
                                                required=key)
