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


class ToscaBlockStorageAttachment(HotResource):
    '''Translate TOSCA relationship AttachesTo for Compute and BlockStorage.'''

    def __init__(self, template, nodetemplates, instace_uuid, volume_id):
        super(ToscaBlockStorageAttachment,
              self).__init__(template, type='OS::Cinder::VolumeAttachment')
        self.nodetemplates = nodetemplates
        self.instace_uuid = instace_uuid
        self.volume_id = volume_id

    def handle_properties(self):
        tosca_props = {}
        for prop in self.nodetemplate.get_properties_objects():
            if isinstance(prop.value, GetInput):
                tosca_props[prop.name] = {'get_param': prop.value.input_name}
            else:
                tosca_props[prop.name] = prop.value
        self.properties = tosca_props
        #instance_uuid and volume_id for Cinder volume attachment
        self.properties['instance_uuid'] = self.instace_uuid
        self.properties['volume_id'] = self.volume_id

    def handle_life_cycle(self):
        pass
