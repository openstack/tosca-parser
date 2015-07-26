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

import logging
from translator.hot.syntax.hot_resource import HotResource
from translator.toscalib.common.exception import InvalidPropertyValueError
from translator.toscalib.elements.scalarunit import ScalarUnit_Size
from translator.toscalib.functions import GetInput
from translator.toscalib.utils.gettextutils import _

log = logging.getLogger("tosca")


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
            else:
                if prop.name == "size":
                    size_value = (ScalarUnit_Size(prop.value).
                                  get_num_from_scalar_unit('GiB'))
                    if size_value == 0:
                        # OpenStack Heat expects size in GB
                        raise InvalidPropertyValueError(
                            what=_('Cinder Volume Size unit should be in GBs'))
                    elif int(size_value) < size_value:
                        size_value = int(size_value) + 1
                        log.warning(_("Cinder unit value should be in "
                                      "multiples of GBs. so corrected "
                                      " %(prop_val)s to %(size_value)s GB.")
                                    % {'prop_val': prop.value,
                                       'size_value': size_value})
                    tosca_props[prop.name] = int(size_value)
                else:
                    tosca_props[prop.name] = prop.value
        self.properties = tosca_props

    def get_hot_attribute(self, attribute, args):
        attr = {}
        # Convert from a TOSCA attribute for a nodetemplate to a HOT
        # attribute for the matching resource.  Unless there is additional
        # runtime support, this should be a one to one mapping.
        if attribute == 'volume_id':
            attr['get_resource'] = args[0]
        return attr
