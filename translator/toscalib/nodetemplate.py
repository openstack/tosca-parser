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
from translator.toscalib.elements.properties import PropertyDef
from translator.toscalib.utils.gettextutils import _

SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
            INTERFACES, CAPABILITIES) = \
           ('derived_from', 'properties', 'requirements', 'interfaces',
            'capabilities')

log = logging.getLogger('tosca')


class NodeTemplate(NodeType):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, nodetemplates):
        super(NodeTemplate, self).__init__(nodetemplates[name]['type'])
        self.name = name
        self.nodetemplates = nodetemplates
        self.nodetemplate = nodetemplates[self.name]
        self.type = self.nodetemplate['type']
        self.type_properties = self.properties_def
        self.type_capabilities = self.capabilities
        self.type_lifecycle_ops = self.lifecycle_operations
        self.type_relationship = self.relationship
        self.related = {}

    @property
    def tpl_requirements(self):
        return self._get_value(REQUIREMENTS, self.nodetemplate)

    @property
    def tpl_relationship(self):
        tpl_relation = {}
        requires = self.tpl_requirements
        if requires:
            for r in requires:
                for cap, node in r.items():
                    for relationship_type in self.type_relationship.keys():
                        if cap == relationship_type.capability_name:
                            rtpl = NodeTemplate(node, self.nodetemplates)
                            tpl_relation[relationship_type] = rtpl
        return tpl_relation

    @property
    def tpl_capabilities(self):
        tpl_cap = []
        properties = {}
        cap_type = None
        caps = self._get_value(CAPABILITIES, self.nodetemplate)
        if caps:
            for name, value in caps.items():
                for prop, val in value.items():
                    properties = val
                for c in self.type_capabilities:
                    if c.name == name:
                        cap_type = c.type
                cap = CapabilityTypeDef(name, cap_type,
                                        self.name, properties)
                tpl_cap.append(cap)
        return tpl_cap

    @property
    def tpl_interfaces(self):
        tpl_ifaces = []
        ifaces = self._get_value(INTERFACES, self.nodetemplate)
        if ifaces:
            for i in ifaces:
                for name, value in ifaces.items():
                    for ops, val in value.items():
                        iface = InterfacesDef(None, name, self.name,
                                              ops, val)
                        tpl_ifaces.append(iface)
        return tpl_ifaces

    @property
    def properties(self):
        tpl_props = []
        properties = self._get_value(PROPERTIES, self.nodetemplate)
        requiredprop = []
        for p in self.type_properties:
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
                prop = PropertyDef(name, self.type, value, self.name)
                tpl_props.append(prop)
        else:
            if requiredprop:
                raise ValueError(_("Node template %(tpl)s is missing"
                                   "one or more required properties %(prop)s")
                                 % {'tpl': self.name, 'prop': requiredprop})
        return tpl_props

    def _add_next(self, nodetpl, relationship):
        self.related[nodetpl] = relationship

    @property
    def related_nodes(self):
        if not self.related:
            for relation, node in self.tpl_relationship.items():
                for tpl in self.nodetemplates:
                    if tpl == node.type:
                        self.related[NodeTemplate(tpl)] = relation
        return self.related.keys()

    def ref_property(self, cap, cap_name, property):
        requires = self.tpl_requirements
        tpl_name = None
        if requires:
            for r in requires:
                for cap, node in r.items():
                    if cap == cap:
                        tpl_name = node
                        break
            if tpl_name:
                tpl = NodeTemplate(tpl_name, self.nodetemplates)
                caps = tpl.tpl_capabilities
                for c in caps:
                    if c.name == cap_name:
                        if c.property == property:
                            return c.property_value

    def validate(self):
        for prop in self.properties:
            prop.validate()
