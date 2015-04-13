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
from translator.toscalib.functions import GetInput


class ToscaBlockStorage(HotResource):
    '''Translate TOSCA node type tosca.nodes.BlockStorage.'''

    def __init__(self, nodetemplate):
        super(ToscaBlockStorage, self).__init__(nodetemplate,
                                                type='OS::Cinder::Volume')
        pass

    def handle_properties(self):
        tosca_props = {}
        for prop in self.nodetemplate.get_properties_objects():
            if isinstance(prop.value, GetInput):
                tosca_props[prop.name] = {'get_param': prop.value.input_name}
        self.properties = tosca_props

    def get_hot_attribute(self, attribute, args):
        attr = {}
        # Convert from a TOSCA attribute for a nodetemplate to a HOT
        # attribute for the matching resource.  Unless there is additional
        # runtime support, this should be a one to one mapping.
        if attribute == 'volume_id':
            attr['get_resource'] = args[0]
        return attr
