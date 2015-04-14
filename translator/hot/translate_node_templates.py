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

import six

from translator.hot.tosca.tosca_block_storage import ToscaBlockStorage
from translator.hot.tosca.tosca_block_storage_attachment import (
    ToscaBlockStorageAttachment
    )
from translator.hot.tosca.tosca_compute import ToscaCompute
from translator.hot.tosca.tosca_database import ToscaDatabase
from translator.hot.tosca.tosca_dbms import ToscaDbms
from translator.hot.tosca.tosca_network_network import ToscaNetwork
from translator.hot.tosca.tosca_network_port import ToscaNetworkPort
from translator.hot.tosca.tosca_nodejs import ToscaNodejs
from translator.hot.tosca.tosca_webserver import ToscaWebserver
from translator.hot.tosca.tosca_wordpress import ToscaWordpress
from translator.toscalib.functions import GetAttribute
from translator.toscalib.functions import GetInput
from translator.toscalib.functions import GetProperty
from translator.toscalib.relationship_template import RelationshipTemplate


SECTIONS = (TYPE, PROPERTIES, REQUIREMENTS, INTERFACES, LIFECYCLE, INPUT) = \
           ('type', 'properties', 'requirements',
            'interfaces', 'lifecycle', 'input')

# TODO(anyone):  the following requirement names should not be hard-coded
# in the translator.  Since they are basically arbitrary names, we have to get
# them from TOSCA type definitions.
# To be fixed with the blueprint:
# https://blueprints.launchpad.net/heat-translator/+spec/tosca-custom-types
REQUIRES = (CONTAINER, DEPENDENCY, DATABASE_ENDPOINT, CONNECTION, HOST) = \
           ('container', 'dependency', 'database_endpoint',
            'connection', 'host')

INTERFACES_STATE = (CREATE, START, CONFIGURE, START, DELETE) = \
                   ('create', 'stop', 'configure', 'start', 'delete')

# dict to look up HOT translation class,
# TODO(replace with function to scan the classes in translator.hot.tosca)
TOSCA_TO_HOT_TYPE = {'tosca.nodes.Compute': ToscaCompute,
                     'tosca.nodes.WebServer': ToscaWebserver,
                     'tosca.nodes.DBMS': ToscaDbms,
                     'tosca.nodes.Database': ToscaDatabase,
                     'tosca.nodes.WebApplication.WordPress': ToscaWordpress,
                     'tosca.nodes.BlockStorage': ToscaBlockStorage,
                     'tosca.nodes.SoftwareComponent.Nodejs': ToscaNodejs,
                     'tosca.nodes.network.Network': ToscaNetwork,
                     'tosca.nodes.network.Port': ToscaNetworkPort}

TOSCA_TO_HOT_REQUIRES = {'container': 'server', 'host': 'server',
                         'dependency': 'depends_on', "connects": 'depends_on'}

TOSCA_TO_HOT_PROPERTIES = {'properties': 'input'}


class TranslateNodeTemplates():
    '''Translate TOSCA NodeTemplates to Heat Resources.'''

    def __init__(self, tosca, hot_template):
        self.tosca = tosca
        self.nodetemplates = self.tosca.nodetemplates
        self.hot_template = hot_template
        # list of all HOT resources generated
        self.hot_resources = []
        # mapping between TOSCA nodetemplate and HOT resource
        self.hot_lookup = {}

    def translate(self):
        return self._translate_nodetemplates()

    def _recursive_handle_properties(self, resource):
        '''Recursively handle the properties of the depends_on_nodes nodes.'''
        # Use of hashtable (dict) here should be faster?
        if resource in self.processed_resources:
            return
        self.processed_resources.append(resource)
        for depend_on in resource.depends_on_nodes:
            self._recursive_handle_properties(depend_on)

        resource.handle_properties()

    def _translate_nodetemplates(self):

        suffix = 0
        # Copy the TOSCA graph: nodetemplate
        for node in self.nodetemplates:
            hot_node = TOSCA_TO_HOT_TYPE[node.type](node)
            self.hot_resources.append(hot_node)
            self.hot_lookup[node] = hot_node

            # BlockStorage Attachment is a special case,
            # which doesn't match to Heat Resources 1 to 1.
            if node.type == "tosca.nodes.Compute":
                volume_name = None
                requirements = node.requirements
                if requirements:
                    # Find the name of associated BlockStorage node
                    for requires in requirements:
                        for value in requires.values():
                            for n in self.nodetemplates:
                                if n.name == value:
                                    volume_name = value
                                    break
                    suffix = suffix + 1
                    attachment_node = self._get_attachment_node(node,
                                                                suffix,
                                                                volume_name)
                    if attachment_node:
                        self.hot_resources.append(attachment_node)

        # Handle life cycle operations: this may expand each node
        # into multiple HOT resources and may change their name
        lifecycle_resources = []
        for resource in self.hot_resources:
            expanded = resource.handle_life_cycle()
            if expanded:
                lifecycle_resources += expanded
        self.hot_resources += lifecycle_resources

        # Copy the initial dependencies based on the relationship in
        # the TOSCA template
        for node in self.nodetemplates:
            for node_depend in node.related_nodes:
                # if the source of dependency is a server, add dependency
                # as properties.get_resource
                if node_depend.type == 'tosca.nodes.Compute':
                    self.hot_lookup[node].properties['server'] = \
                        {'get_resource': self.hot_lookup[node_depend].name}
                # for all others, add dependency as depends_on
                else:
                    self.hot_lookup[node].depends_on.append(
                        self.hot_lookup[node_depend].top_of_chain())

                self.hot_lookup[node].depends_on_nodes.append(
                    self.hot_lookup[node_depend].top_of_chain())

        # handle hosting relationship
        for resource in self.hot_resources:
            resource.handle_hosting()

        # handle built-in properties of HOT resources
        # if a resource depends on other resources,
        # their properties need to be handled first.
        # Use recursion to handle the properties of the
        # dependent nodes in correct order
        self.processed_resources = []
        for resource in self.hot_resources:
            self._recursive_handle_properties(resource)

        # handle resources that need to expand to more than one HOT resource
        expansion_resources = []
        for resource in self.hot_resources:
            expanded = resource.handle_expansion()
            if expanded:
                expansion_resources += expanded
        self.hot_resources += expansion_resources

        # Resolve function calls:  GetProperty, GetAttribute, GetInput
        # at this point, all the HOT resources should have been created
        # in the graph.
        for resource in self.hot_resources:
            # traverse the reference chain to get the actual value
            inputs = resource.properties.get('input_values')
            if inputs:
                for name, value in six.iteritems(inputs):
                    if isinstance(value, GetAttribute):
                        # for the attribute
                        # get the proper target type to perform the translation
                        args = value.result()
                        target = args[0]
                        hot_target = self.find_hot_resource(target)

                        inputs[name] = hot_target.get_hot_attribute(args[1],
                                                                    args)
                    else:
                        if isinstance(value, GetProperty) or \
                                isinstance(value, GetInput):
                            inputs[name] = value.result()

        return self.hot_resources

    def _get_attachment_node(self, node, suffix, volume_name):
        attach = False
        ntpl = self.nodetemplates
        for key, value in node.relationships.items():
            if key.type == 'tosca.relationships.AttachesTo':
                if value.type == 'tosca.nodes.BlockStorage':
                    attach = True
            if attach:
                relationship_tpl = None
                for req in node.requirements:
                    for rkey, rval in req.items():
                        if rkey == 'type':
                            relationship_tpl = req
                        elif rkey == 'template':
                            relationship_tpl = \
                                self.tosca._tpl_relationship_templates()[rval]
                        else:
                            continue
                        if relationship_tpl:
                            rval_new = rval + "_" + str(suffix)
                            att = RelationshipTemplate(
                                relationship_tpl, rval_new,
                                self.tosca._tpl_relationship_types())
                            hot_node = ToscaBlockStorageAttachment(att, ntpl,
                                                                   node.name,
                                                                   volume_name
                                                                   )
                            return hot_node

    def find_hot_resource(self, name):
        for resource in self.hot_resources:
            if resource.name == name:
                return resource
