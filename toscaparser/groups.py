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
from toscaparser.entity_template import EntityTemplate
from toscaparser.utils import validateutils

SECTIONS = (TYPE, METADATA, DESCRIPTION, PROPERTIES, MEMBERS, INTERFACES) = \
           ('type', 'metadata', 'description',
            'properties', 'members', 'interfaces')


class Group(EntityTemplate):

    def __init__(self, name, group_templates, member_nodes, custom_defs=None):
        """
        Initialize the meta data.

        Args:
            self: (todo): write your description
            name: (str): write your description
            group_templates: (todo): write your description
            member_nodes: (str): write your description
            custom_defs: (todo): write your description
        """
        super(Group, self).__init__(name,
                                    group_templates,
                                    'group_type',
                                    custom_defs)
        self.name = name
        self.tpl = group_templates
        self.meta_data = None
        if self.METADATA in self.tpl:
            self.meta_data = self.tpl.get(self.METADATA)
            validateutils.validate_map(self.meta_data)
        self.member_nodes = member_nodes
        self._validate_keys()

    @property
    def members(self):
        """
        Returns the members of the entity.

        Args:
            self: (todo): write your description
        """
        return self.entity_tpl.get('members')

    @property
    def description(self):
        """
        Return the description of the entity.

        Args:
            self: (todo): write your description
        """
        return self.entity_tpl.get('description')

    def get_member_nodes(self):
        """
        Returns a list of all the nodes in this node.

        Args:
            self: (todo): write your description
        """
        return self.member_nodes

    def _validate_keys(self):
        """
        Ensure that the key fields exist.

        Args:
            self: (todo): write your description
        """
        for key in self.entity_tpl.keys():
            if key not in SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Groups "%s"' % self.name,
                                      field=key))
