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


class NodeGroup(object):

    def __init__(self, name, group_templates, member_nodes):
        self.name = name
        self.tpl = group_templates
        self.members = member_nodes

    @property
    def member_names(self):
        return self.tpl.get('members')

    @property
    def policies(self):
        return self.tpl.get('policies')
