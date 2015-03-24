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
from translator.toscalib.common.exception import InvalidPropertyValueError


class ToscaNetwork(HotResource):
    '''Translate TOSCA node type tosca.nodes.network.Network.'''

    toscatype = 'tosca.nodes.network.Network'
    SUBNET_SUFFIX = '_subnet'
    NETWORK_PROPS = ['network_name', 'network_id', 'segmentation_id']
    SUBNET_PROPS = ['ip_version', 'cidr', 'start_ip', 'end_ip', 'gateway_ip']

    existing_resource_id = None

    def __init__(self, nodetemplate):
        super(ToscaNetwork, self).__init__(nodetemplate,
                                           type='OS::Neutron::Net')
        pass

    def handle_properties(self):
        tosca_props = self._get_tosca_props(
            self.nodetemplate.get_properties_objects())

        net_props = {}
        for key, value in tosca_props.items():
            if key in self.NETWORK_PROPS:
                if key == 'network_name':
                    # If CIDR is specified network_name should
                    # be used as the name for the new network.
                    if 'cidr' in tosca_props.keys():
                        net_props['name'] = value
                    # If CIDR is not specified network_name will be used
                    # to lookup existing network. If network_id is specified
                    # together with network_name then network_id should be
                    # used to lookup the network instead
                    elif 'network_id' not in tosca_props.keys():
                        self.hide_resource = True
                        self.existing_resource_id = value
                        break
                elif key == 'network_id':
                    self.hide_resource = True
                    self.existing_resource_id = value
                    break
                elif key == 'segmentation_id':
                    net_props['segmentation_id'] =  \
                        tosca_props['segmentation_id']
                    # Hardcode to vxlan for now until we add the network type
                    # and physical network to the spec.
                    net_props['value_specs'] = {'provider:segmentation_id':
                                                value, 'provider:network_type':
                                                'vxlan'}
        self.properties = net_props

    def handle_expansion(self):
        # If the network resource should not be output (they are hidden),
        # there is no need to generate subnet resource
        if self.hide_resource:
            return

        tosca_props = self._get_tosca_props(
            self.nodetemplate.get_properties_objects())

        subnet_props = {}

        ip_pool_start = None
        ip_pool_end = None

        for key, value in tosca_props.items():
            if key in self.SUBNET_PROPS:
                if key == 'start_ip':
                    ip_pool_start = value
                elif key == 'end_ip':
                    ip_pool_end = value
                elif key == 'dhcp_enabled':
                    subnet_props['enable_dhcp'] = value
                else:
                    subnet_props[key] = value

        if 'network_id' in tosca_props:
            subnet_props['network'] = tosca_props['network_id']
        else:
            subnet_props['network'] = '{ get_resource: %s }' % (self.name)

        # Handle allocation pools
        # Do this only if both start_ip and end_ip are provided
        # If one of them is missing throw an exception.
        if ip_pool_start and ip_pool_end:
            allocation_pool = {}
            allocation_pool['start'] = ip_pool_start
            allocation_pool['end'] = ip_pool_end
            allocation_pools = [allocation_pool]
            subnet_props['allocation_pools'] = allocation_pools
        elif ip_pool_start:
            raise InvalidPropertyValueError(what='start_ip')
        elif ip_pool_end:
            raise InvalidPropertyValueError(what='end_ip')

        subnet_resource_name = self.name + self.SUBNET_SUFFIX

        hot_resources = [HotResource(self.nodetemplate,
                                     type='OS::Neutron::Subnet',
                                     name=subnet_resource_name,
                                     properties=subnet_props)]
        return hot_resources
