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


class GroupType(StatefulEntityType):
    '''TOSCA built-in group type.'''

    SECTIONS = (DERIVED_FROM, VERSION, METADATA, DESCRIPTION, PROPERTIES,
                MEMBERS, INTERFACES) = \
               ("derived_from", "version", "metadata", "description",
                "properties", "members", "interfaces")

    def __init__(self, grouptype, custom_def=None):
        super(GroupType, self).__init__(grouptype, self.GROUP_PREFIX,
                                        custom_def)
        self.custom_def = custom_def
        self.grouptype = grouptype
        self._validate_fields()
        self.group_description = None
        if self.DESCRIPTION in self.defs:
            self.group_description = self.defs[self.DESCRIPTION]

        self.group_version = None
        if self.VERSION in self.defs:
            self.group_version = self.defs[self.VERSION]

        self.group_properties = None
        if self.PROPERTIES in self.defs:
            self.group_properties = self.defs[self.PROPERTIES]

        self.group_members = None
        if self.MEMBERS in self.defs:
            self.group_members = self.defs[self.MEMBERS]

        if self.METADATA in self.defs:
            self.meta_data = self.defs[self.METADATA]
            self._validate_metadata(self.meta_data)

    @property
    def parent_type(self):
        '''Return a group statefulentity of this entity is derived from.'''
        if not hasattr(self, 'defs'):
            return None
        pgroup_entity = self.derived_from(self.defs)
        if pgroup_entity:
            return GroupType(pgroup_entity, self.custom_def)

    @property
    def description(self):
        return self.group_description

    @property
    def version(self):
        return self.group_version

    @property
    def interfaces(self):
        return self.get_value(self.INTERFACES)

    def _validate_fields(self):
        if self.defs:
            for name in self.defs.keys():
                if name not in self.SECTIONS:
                    ExceptionCollector.appendException(
                        UnknownFieldError(what='Group Type %s'
                                          % self.grouptype, field=name))

    def _validate_metadata(self, meta_data):
        if not meta_data.get('type') in ['map', 'tosca:map']:
            ExceptionCollector.appendException(
                InvalidTypeError(what='"%s" defined in group for '
                                 'metadata' % (meta_data.get('type'))))
        for entry_schema, entry_schema_type in meta_data.items():
            if isinstance(entry_schema_type, dict) and not \
                    entry_schema_type.get('type') == 'string':
                ExceptionCollector.appendException(
                    InvalidTypeError(what='"%s" defined in group for '
                                     'metadata "%s"'
                                     % (entry_schema_type.get('type'),
                                        entry_schema)))
