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


class ToscaNetworkPort(HotResource):
    '''Translate TOSCA node type tosca.nodes.network.Port.'''

    toscatype = 'tosca.nodes.network.Port'

    def __init__(self, nodetemplate):
        super(ToscaNetworkPort, self).__init__(nodetemplate,
                                               type='OS::Neutron::Port')
        # Default order
        self.order = 0
        pass

    def _generate_networks_for_compute(self, port_resources):
        '''Generate compute networks property list from the port resources.'''
        networks = []
        for resource in port_resources:
            networks.append({'port': '{ get_resource: %s }' % (resource.name)})
        return networks

    def _insert_sorted_resource(self, resources, resource):
        '''Insert a resource in the list of resources and keep the order.'''
        lo = 0
        hi = len(resources)
        while lo < hi:
            mid = (lo + hi) // 2
            if resource.order < resources[mid].order:
                hi = mid
            else:
                lo = mid + 1
        resources.insert(lo, resource)

    def handle_properties(self):
        tosca_props = self._get_tosca_props(
            self.nodetemplate.get_properties_objects())

        port_props = {}
        for key, value in tosca_props.items():
            if key == 'ip_address':
                fixed_ip = []
                fixed_ip['ip_address'] = value
                fixed_ip['subnet'] = ''
                port_props['fixed_ips'] = [fixed_ip]
            elif key == 'order':
                self.order = value
            #TODO(sdmonov). Need to implement the properties below
            elif key == 'is_default':
                pass
            elif key == 'ip_range_start':
                pass
            elif key == 'ip_range_end':
                pass
            else:
                port_props[key] = value

        # Get the nodetype relationships
        relationships = {relation.type: node for relation, node in
                         self.nodetemplate.relationships.items()}

        # Check for LinksTo relations. If found add a network property with
        # the network name into the port
        links_to = None
        if 'tosca.relationships.network.LinksTo' in relationships:
            links_to = relationships['tosca.relationships.network.LinksTo']

            network_resource = None
            for hot_resource in self.depends_on_nodes:
                if links_to.name == hot_resource.name:
                    network_resource = hot_resource
                    break

            if network_resource.existing_resource_id:
                port_props['network'] =\
                    str(network_resource.existing_resource_id)
                self.depends_on = None
            else:
                port_props['network'] = '{ get_resource: %s }'\
                    % (links_to.name)

        # Check for BindsTo relationship. If found add network to the networks
        # property of the corresponding compute resource
        binds_to = None
        if 'tosca.relationships.network.BindsTo' in relationships:
            binds_to = relationships['tosca.relationships.network.BindsTo']
            compute_resource = None
            for hot_resource in self.depends_on_nodes:
                if binds_to.name == hot_resource.name:
                    compute_resource = hot_resource
                    break
            if compute_resource:
                port_resources = compute_resource.assoc_port_resources
                self._insert_sorted_resource(port_resources, self)
                #TODO(sdmonov). Using generate networks every time we add a
                # network is not the fastest way to do the things. We should
                # do this only once at the end.
                networks = self._generate_networks_for_compute(port_resources)
                compute_resource.properties['networks'] = networks

        self.properties = port_props
