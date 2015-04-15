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

from collections import OrderedDict
import six

from translator.toscalib.functions import GetInput
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.utils.gettextutils import _


SECTIONS = (TYPE, PROPERTIES, MEDADATA, DEPENDS_ON, UPDATE_POLICY,
            DELETION_POLICY) = \
           ('type', 'properties', 'metadata',
            'depends_on', 'update_policy', 'deletion_policy')


class HotResource(object):
    '''Base class for TOSCA node type translation to Heat resource type.'''

    def __init__(self, nodetemplate, name=None, type=None, properties=None,
                 metadata=None, depends_on=None,
                 update_policy=None, deletion_policy=None):
        self.nodetemplate = nodetemplate
        if name:
            self.name = name
        else:
            self.name = nodetemplate.name
        self.type = type
        self.properties = properties or {}
        # special case for HOT softwareconfig
        if type == 'OS::Heat::SoftwareConfig':
            self.properties['group'] = 'script'
        self.metadata = metadata

        # The difference between depends_on and depends_on_nodes is
        # that depends_on defines dependency in the context of the
        # HOT template and it is used during the template output.
        # Depends_on_nodes defines the direct dependency between the
        # tosca nodes and is not used during the output of the
        # HOT template but for internal processing only. When a tosca
        # node depends on another node it will be always added to
        # depends_on_nodes but not always to depends_on. For example
        # if the source of dependency is a server, the dependency will
        # be added as properties.get_resource and not depends_on
        if depends_on:
            self.depends_on = depends_on
            self.depends_on_nodes = depends_on
        else:
            self.depends_on = []
            self.depends_on_nodes = []
        self.update_policy = update_policy
        self.deletion_policy = deletion_policy
        self.group_dependencies = {}
        # if hide_resource is set to true, then this resource will not be
        # generated in the output yaml.
        self.hide_resource = False

    def handle_properties(self):
        # the property can hold a value or the intrinsic function get_input
        # for value, copy it
        # for get_input, convert to get_param
        for prop in self.nodetemplate.get_properties_objects():
            pass

    def handle_life_cycle(self):
        hot_resources = []
        deploy_lookup = {}
        # TODO(anyone):  sequence for life cycle needs to cover different
        # scenarios and cannot be fixed or hard coded here
        interfaces_deploy_sequence = ['create', 'configure', 'start']

        # create HotResource for each interface used for deployment:
        # create, start, configure
        # ignore the other interfaces
        # observe the order:  create, start, configure
        # use the current HotResource for the first interface in this order

        # hold the original name since it will be changed during
        # the transformation
        node_name = self.name
        reserve_current = 'NONE'
        interfaces_actual = []
        for interface in self.nodetemplate.interfaces:
            interfaces_actual.append(interface.name)
        for operation in interfaces_deploy_sequence:
            if operation in interfaces_actual:
                reserve_current = operation
                break

        # create the set of SoftwareDeployment and SoftwareConfig for
        # the interface operations
        hosting_server = None
        if self.nodetemplate.requirements is not None:
            hosting_server = self._get_hosting_server()
        for interface in self.nodetemplate.interfaces:
            if interface.name in interfaces_deploy_sequence:
                config_name = node_name + '_' + interface.name + '_config'
                deploy_name = node_name + '_' + interface.name + '_deploy'
                hot_resources.append(
                    HotResource(self.nodetemplate,
                                config_name,
                                'OS::Heat::SoftwareConfig',
                                {'config':
                                    {'get_file': interface.implementation}}))

                # hosting_server is None if requirements is None
                hosting_on_server = (hosting_server.name if
                                     hosting_server else None)
                if interface.name == reserve_current:
                    deploy_resource = self
                    self.name = deploy_name
                    self.type = 'OS::Heat::SoftwareDeployment'
                    self.properties = {'config': {'get_resource': config_name},
                                       'server': {'get_resource':
                                                  hosting_on_server}}
                    deploy_lookup[interface.name] = self
                else:
                    sd_config = {'config': {'get_resource': config_name},
                                 'server': {'get_resource':
                                            hosting_on_server}}
                    deploy_resource = \
                        HotResource(self.nodetemplate,
                                    deploy_name,
                                    'OS::Heat::SoftwareDeployment',
                                    sd_config)
                    hot_resources.append(deploy_resource)
                    deploy_lookup[interface.name] = deploy_resource
                lifecycle_inputs = self._get_lifecycle_inputs(interface)
                if lifecycle_inputs:
                    deploy_resource.properties['input_values'] = \
                        lifecycle_inputs

        # Add dependencies for the set of HOT resources in the sequence defined
        # in interfaces_deploy_sequence
        # TODO(anyone): find some better way to encode this implicit sequence
        group = {}
        for op, hot in deploy_lookup.items():
            # position to determine potential preceding nodes
            op_index = interfaces_deploy_sequence.index(op)
            for preceding_op in \
                    reversed(interfaces_deploy_sequence[:op_index]):
                preceding_hot = deploy_lookup.get(preceding_op)
                if preceding_hot:
                    hot.depends_on.append(preceding_hot)
                    hot.depends_on_nodes.append(preceding_hot)
                    group[preceding_hot] = hot
                    break

        # save this dependency chain in the set of HOT resources
        self.group_dependencies.update(group)
        for hot in hot_resources:
            hot.group_dependencies.update(group)

        return hot_resources

    def handle_expansion(self):
        pass

    def handle_hosting(self):
        # handle hosting server for the OS:HEAT::SoftwareDeployment
        # from the TOSCA nodetemplate, traverse the relationship chain
        # down to the server
        if self.type == 'OS::Heat::SoftwareDeployment':
            # skip if already have hosting
            # If type is NodeTemplate, look up corresponding HotResrouce
            host_server = self.properties.get('server')
            if host_server is None or not host_server['get_resource']:
                raise Exception(_("Internal Error: expecting host "
                                  "in software deployment"))
            elif isinstance(host_server['get_resource'], NodeTemplate):
                self.properties['server']['get_resource'] = \
                    host_server['get_resource'].name

    def top_of_chain(self):
        dependent = self.group_dependencies.get(self)
        if dependent is None:
            return self
        else:
            return dependent.top_of_chain()

    def get_dict_output(self):
        resource_sections = OrderedDict()
        resource_sections[TYPE] = self.type
        if self.properties:
            resource_sections[PROPERTIES] = self.properties
        if self.metadata:
            resource_sections[MEDADATA] = self.metadata
        if self.depends_on:
            resource_sections[DEPENDS_ON] = []
            for depend in self.depends_on:
                resource_sections[DEPENDS_ON].append(depend.name)
        if self.update_policy:
            resource_sections[UPDATE_POLICY] = self.update_policy
        if self.deletion_policy:
            resource_sections[DELETION_POLICY] = self.deletion_policy

        return {self.name: resource_sections}

    def _get_lifecycle_inputs(self, interface):
        # check if this lifecycle operation has input values specified
        # extract and convert to HOT format
        if isinstance(interface.value, six.string_types):
            # the interface has a static string
            return {}
        else:
            # the interface is a dict {'implemenation': xxx, 'input': yyy}
            inputs = interface.value.get('inputs')
            deploy_inputs = {}
            if inputs:
                for name, value in six.iteritems(inputs):
                    deploy_inputs[name] = value
            return deploy_inputs

    def _get_hosting_server(self, node_template=None):
        # find the server that hosts this software by checking the
        # requirements and following the hosting chain
        this_node_template = self.nodetemplate \
            if node_template is None else node_template
        for requirement in this_node_template.requirements:
            for requirement_name, node_name in six.iteritems(requirement):
                for check_node in this_node_template.related_nodes:
                    # check if the capability is Container
                    if node_name == check_node.name:
                        if self._is_container_type(requirement_name,
                                                   check_node):
                            return check_node
                        elif check_node.related_nodes:
                            return self._get_hosting_server(check_node)
        return None

    def _is_container_type(self, requirement_name, node):
        # capability is a list of dict
        # For now just check if it's type tosca.nodes.Compute
        # TODO(anyone): match up requirement and capability
        if node.type == 'tosca.nodes.Compute':
            return True
        else:
            return False

    def get_hot_attribute(self, attribute, args):
        # this is a place holder and should be implemented by the subclass
        # if translation is needed for the particular attribute
        raise Exception(_("No translation in TOSCA type {0} for attribute "
                          "{1}").format(self.nodetemplate.type, attribute))

    def _get_tosca_props(self, properties):
        tosca_props = {}
        for prop in self.nodetemplate.get_properties_objects():
            if isinstance(prop.value, GetInput):
                tosca_props[prop.name] = {'get_param': prop.value.input_name}
            else:
                tosca_props[prop.name] = prop.value
        return tosca_props
