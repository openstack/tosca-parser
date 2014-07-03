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

from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import TypeMismatchError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.elements.capabilitytype import CapabilityTypeDef
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.interfaces import LIFECYCLE, CONFIGURE
from translator.toscalib.elements.nodetype import NodeType
from translator.toscalib.properties import Property


SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
            INTERFACES, CAPABILITIES, TYPE) = \
           ('derived_from', 'properties', 'requirements', 'interfaces',
            'capabilities', 'type')

log = logging.getLogger('tosca')


class NodeTemplate(object):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, node_templates, custom_def=None):
        self.name = name
        self.node_templates = node_templates
        self._validate_field()
        self.node_template = node_templates[self.name]
        self.type = self.node_template[TYPE]
        self.node_type = NodeType(self.type, custom_def)
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
        type_interfaces = self.node_type.get_value(INTERFACES,
                                                   self.node_template)
        if type_interfaces:
            for interface_type, value in type_interfaces.items():
                for op, op_def in value.items():
                    iface = InterfacesDef(self.node_type,
                                          interfacetype=interface_type,
                                          node_template=self,
                                          name=op,
                                          value=op_def)
                    interfaces.append(iface)
        return interfaces

    @property
    def properties(self):
        props = []
        properties = self.node_type.get_value(PROPERTIES, self.node_template)
        if properties:
            for name, value in properties.items():
                for p in self.node_type.properties_def:
                    if p.name == name:
                        prop = Property(name, value, p.schema)
                        props.append(prop)
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
        self._validate_capabilities()
        self._validate_requirments()
        self._validate_properties()
        self._validate_interfaces()
        for prop in self.properties:
            prop.validate()

    def _validate_capabilities(self):
        type_capabilities = self.node_type.capabilities
        allowed_caps = []
        if type_capabilities:
            for tcap in type_capabilities:
                allowed_caps.append(tcap.name)
        capabilities = self.node_type.get_value(CAPABILITIES,
                                                self.node_template)
        if capabilities:
            self._common_validate_field(capabilities, allowed_caps,
                                        'Capabilities')

    def _validate_requirments(self):
        type_requires = self.node_type.get_all_requirements()
        allowed_reqs = []
        if type_requires:
            for treq in type_requires:
                for key in treq:
                    allowed_reqs.append(key)
        requires = self.node_type.get_value(REQUIREMENTS, self.node_template)
        if requires:
            if not isinstance(requires, list):
                raise TypeMismatchError(
                    what='Requirements of node template %s' % self.name,
                    type='list')
            for req in requires:
                self._common_validate_field(req, allowed_reqs, 'Requirements')

    def _validate_interfaces(self):
        ifaces = self.node_type.get_value(INTERFACES, self.node_template)
        if ifaces:
            for i in ifaces:
                for name, value in ifaces.items():
                    if name == LIFECYCLE:
                        self._common_validate_field(
                            value, InterfacesDef.
                            interfaces_node_lifecycle_operations,
                            'Interfaces')
                    elif name == CONFIGURE:
                        self._common_validate_field(
                            value, InterfacesDef.
                            interfaces_relationship_confiure_operations,
                            'Interfaces')
                    else:
                        raise UnknownFieldError(
                            what='Interfaces of node template %s' % self.name,
                            field=name)

    def _validate_properties(self):
        properties = self.node_type.get_value(PROPERTIES, self.node_template)
        allowed_props = []
        required_props = []
        for p in self.node_type.properties_def:
            allowed_props.append(p.name)
            if p.required:
                required_props.append(p.name)
        if properties:
            self._common_validate_field(properties, allowed_props,
                                        'Properties')
            #make sure it's not missing any property required by a node type
            missingprop = []
            for r in required_props:
                if r not in properties.keys():
                    missingprop.append(r)
            if missingprop:
                raise MissingRequiredFieldError(
                    what='Properties of node template %s' % self.name,
                    required=missingprop)
        else:
            if required_props:
                raise MissingRequiredFieldError(
                    what='Properties of node template %s' % self.name,
                    required=missingprop)

    def _validate_field(self):
        if not isinstance(self.node_templates[self.name], dict):
            raise MissingRequiredFieldError(
                what='Node template %s' % self.name, required=TYPE)
        try:
            self.node_templates[self.name][TYPE]
        except KeyError:
            raise MissingRequiredFieldError(
                what='Node template %s' % self.name, required=TYPE)
        self._common_validate_field(self.node_templates[self.name], SECTIONS,
                                    'Second level')

    def _common_validate_field(self, schema, allowedlist, section):
        for name in schema:
            if name not in allowedlist:
                raise UnknownFieldError(
                    what='%(section)s of node template %(nodename)s'
                    % {'section': section, 'nodename': self.name},
                    field=name)
