#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from translator.hot.syntax.hot_resource import HotResource


class ToscaNodejs(HotResource):
    '''Translate TOSCA node type tosca.nodes.SoftwareComponent.Nodejs.'''
    # TODO(anyone): this is a custom TOSCA type so it should be kept separate
    # from the TOSCA base types;  need to come up with a scheme so new custom
    # types can be added by users.

    toscatype = 'tosca.nodes.SoftwareComponent.Nodejs'

    def __init__(self, nodetemplate):
        super(ToscaNodejs, self).__init__(nodetemplate)
        pass

    def handle_properties(self):
        pass
