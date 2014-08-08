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

# A design issue to be resolved is how to translate the generic TOSCA server
# properties to OpenStack flavors and images.  At the Atlanta design summit,
# there was discussion on using Glance to store metadata and Graffiti to
# describe artifacts.  We will follow these projects to see if they can be
# leveraged for this TOSCA translation.
# For development purpose at this time, we temporarily hardcode a list of
# flavors and images here
FLAVORS = {'m1.xlarge': {'mem_size': 16384, 'disk_size': 160, 'num_cpus': 8},
           'm1.large': {'mem_size': 8192, 'disk_size': 80, 'num_cpus': 4},
           'm1.medium': {'mem_size': 4096, 'disk_size': 40, 'num_cpus': 2},
           'm1.small': {'mem_size': 2048, 'disk_size': 20, 'num_cpus': 1},
           'm1.tiny': {'mem_size': 512, 'disk_size': 1, 'num_cpus': 1},
           'm1.micro': {'mem_size': 128, 'disk_size': 0, 'num_cpus': 1},
           'm1.nano': {'mem_size': 64, 'disk_size': 0, 'num_cpus': 1}}

IMAGES = {'fedora-amd64-heat-config': {'os_arch': 'x86_64',
                                       'os_type': 'Linux',
                                       'os_distribution': 'Fedora',
                                       'os_version': '18'},
          'F18-x86_64-cfntools': {'os_arch': 'x86_64',
                                  'os_type': 'Linux',
                                  'os_distribution': 'Fedora',
                                  'os_version': '19'},
          'Fedora-x86_64-20-20131211.1-sda': {'os_arch': 'x86_64',
                                              'os_type': 'Linux',
                                              'os_distribution': 'Fedora',
                                              'os_version': '20'},
          'cirros-0.3.1-x86_64-uec': {'os_arch': 'x86_64',
                                      'os_type': 'Linux',
                                      'os_distribution': 'CirrOS',
                                      'os_version': '0.3.1'}}


class ToscaCompute(HotResource):
    '''Translate TOSCA node type tosca.nodes.Compute.'''

    toscatype = 'tosca.nodes.Compute'

    def __init__(self, nodetemplate):
        super(ToscaCompute, self).__init__(nodetemplate,
                                           type='OS::Nova::Server')
        pass

    def handle_properties(self):
        self.properties = self.translate_compute_flavor_and_image(
            self.nodetemplate.properties)
        self.properties['user_data_format'] = 'SOFTWARE_CONFIG'
        # TODO(anyone): handle user key
        # hardcoded here for testing
        self.properties['key_name'] = 'userkey'

    # To be reorganized later based on new development in Glance and Graffiti
    def translate_compute_flavor_and_image(self, properties):
        hot_properties = {}
        tosca_props = {}
        for prop in properties:
            tosca_props[prop.name] = prop.value
        flavor = self._best_flavor(tosca_props)
        image = self._best_image(tosca_props)
        hot_properties['flavor'] = flavor
        hot_properties['image'] = image
        # TODO(anyone): consider adding the flavor or image as a template
        # parameter if no match is found.
        return hot_properties

    def _best_flavor(self, properties):
        # start with all flavors
        match_all = FLAVORS.keys()

        # TODO(anyone): Handle the case where the value contains something like
        # get_input instead of a value.
        # flavors that fit the CPU count
        cpu = properties.get('num_cpus')
        match_cpu = self._match_flavors(match_all, FLAVORS, 'num_cpus', cpu)

        # flavors that fit the mem size
        mem = properties.get('mem_size')
        match_cpu_mem = self._match_flavors(match_cpu, FLAVORS,
                                            'mem_size', mem)
        # flavors that fit the disk size
        disk = properties.get('disk_size')
        match_cpu_mem_disk = self._match_flavors(match_cpu_mem, FLAVORS,
                                                 'disk_size', disk)
        # for now just pick the first flavor
        # the selection can be based on some heuristic, e.g. pick one with the
        # least resource
        if len(match_cpu_mem_disk):
            return match_cpu_mem_disk[0]

    def _best_image(self, properties):
        match_all = IMAGES.keys()
        os_arch = properties.get('os_arch')
        match_arch = self._match_images(match_all, IMAGES, 'os_arch', os_arch)
        os_type = properties.get('os_type')
        match_type = self._match_images(match_arch, IMAGES, 'os_type', os_type)
        os_distribution = properties.get('os_distribution')
        match_distribution = self._match_images(match_type, IMAGES,
                                                'os_distribution',
                                                os_distribution)
        os_version = properties.get('os_version')
        match_version = self._match_images(match_distribution, IMAGES,
                                           'os_version', os_version)

        if len(match_version):
            return match_version[0]

    def _match_flavors(self, this_list, this_dict, attr, size):
        if not size:
            return this_list
        matching_flavors = []
        for flavor in this_list:
            if isinstance(size, int):
                if this_dict[flavor][attr] >= size:
                    matching_flavors.append(flavor)
        return matching_flavors

    def _match_images(self, this_list, this_dict, attr, prop):
        if not prop:
            return this_list
        matching_images = []
        for image in this_list:
            if this_dict[image][attr] == str(prop):
                matching_images.append(image)
        return matching_images
