# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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


import logging

from translator.toscalib.elements.capabilitytype import CapabilityTypeDef
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.nodetype import NodeType
from translator.toscalib.properties import Property
from translator.toscalib.utils.gettextutils import _

SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
            INTERFACES, CAPABILITIES) = \
           ('derived_from', 'properties', 'requirements', 'interfaces',
            'capabilities')

log = logging.getLogger('tosca')


class NodeTemplate(object):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, node_templates):
        self.name = name
        self.node_type = NodeType(node_templates[name]['type'])
        self.node_templates = node_templates
        self.node_template = node_templates[self.name]
        self.type = self.node_template['type']
        self.related = {}

    @property
    def requirements(self):
        return self.node_type.get_value(REQUIREMENTS, self.node_template)

    @property
    def relationship(self):
        relation = {}
        requires = self.requirements
        if requires:
            for r in requires:
                for cap, node in r.items():
                    for rtype in self.node_type.relationship.keys():
                        if cap == rtype.capability_name:
                            rtpl = NodeTemplate(node, self.node_templates)
                            relation[rtype] = rtpl
        return relation

    @property
    def capabilities(self):
        capability = []
        properties = {}
        cap_type = None
        caps = self.node_type.get_value(CAPABILITIES, self.node_template)
        if caps:
            for name, value in caps.items():
                for prop, val in value.items():
                    properties = val
                for c in self.node_type.capabilities:
                    if c.name == name:
                        cap_type = c.type
                cap = CapabilityTypeDef(name, cap_type,
                                        self.name, properties)
                capability.append(cap)
        return capability

    @property
    def interfaces(self):
        interfaces = []
        ifaces = self.node_type.get_value(INTERFACES, self.node_template)
        if ifaces:
            for i in ifaces:
                for name, value in ifaces.items():
                    for ops, val in value.items():
                        iface = InterfacesDef(None, name, self.name,
                                              ops, val)
                        interfaces.append(iface)
        return interfaces

    @property
    def properties(self):
        props = []
        properties = self.node_type.get_value(PROPERTIES, self.node_template)
        requiredprop = []
        for p in self.node_type.properties_def:
            if p.required:
                requiredprop.append(p.name)
        if properties:
            #make sure it's not missing any property required by a node type
            missingprop = []
            for r in requiredprop:
                if r not in properties.keys():
                    missingprop.append(r)
            if missingprop:
                raise ValueError(_("Node template %(tpl)s is missing "
                                   "one or more required properties %(prop)s")
                                 % {'tpl': self.name, 'prop': missingprop})
            for name, value in properties.items():
                for p in self.node_type.properties_def:
                    if p.name == name:
                        prop = Property(name, value, p.schema)
                        props.append(prop)
        else:
            if requiredprop:
                raise ValueError(_("Node template %(tpl)s is missing"
                                   "one or more required properties %(prop)s")
                                 % {'tpl': self.name, 'prop': requiredprop})
        return props

    def _add_next(self, nodetpl, relationship):
        self.related[nodetpl] = relationship

    @property
    def related_nodes(self):
        if not self.related:
            for relation, node in self.node_type.relationship.items():
                for tpl in self.node_templates:
                    if tpl == node.type:
                        self.related[NodeTemplate(tpl)] = relation
        return self.related.keys()

    def ref_property(self, cap, cap_name, property):
        requires = self.node_type.requirements
        name = None
        if requires:
            for r in requires:
                for cap, node in r.items():
                    if cap == cap:
                        name = node
                        break
            if name:
                tpl = NodeTemplate(name, self.node_templates)
                caps = tpl.capabilities
                for c in caps:
                    if c.name == cap_name:
                        if c.property == property:
                            return c.property_value

    def validate(self):
        for prop in self.properties:
            prop.validate()
