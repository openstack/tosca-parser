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
from toscaparser.common.exception import UnknownFieldError
from toscaparser.elements.statefulentitytype import StatefulEntityType


class RelationshipType(StatefulEntityType):
    '''TOSCA built-in relationship type.'''
    SECTIONS = (DERIVED_FROM, VALID_TARGET_TYPES, INTERFACES,
                ATTRIBUTES, PROPERTIES, DESCRIPTION, VERSION,
                CREDENTIAL) = ('derived_from', 'valid_target_types',
                               'interfaces', 'attributes', 'properties',
                               'description', 'version', 'credential')

    def __init__(self, type, capability_name=None, custom_def=None):
        """
        Initialize the underlying capability.

        Args:
            self: (todo): write your description
            type: (str): write your description
            capability_name: (str): write your description
            custom_def: (todo): write your description
        """
        super(RelationshipType, self).__init__(type, self.RELATIONSHIP_PREFIX,
                                               custom_def)
        self.capability_name = capability_name
        self.custom_def = custom_def
        self._validate_keys()

    @property
    def parent_type(self):
        '''Return a relationship this reletionship is derived from.'''
        prel = self.derived_from(self.defs)
        if prel:
            return RelationshipType(prel, self.custom_def)

    @property
    def valid_target_types(self):
        """
        Validate the target types.

        Args:
            self: (todo): write your description
        """
        return self.entity_value(self.defs, 'valid_target_types')

    def _validate_keys(self):
        """
        Ensure that all of the fields

        Args:
            self: (todo): write your description
        """
        for key in self.defs.keys():
            if key not in self.SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Relationshiptype "%s"' % self.type,
                                      field=key))
