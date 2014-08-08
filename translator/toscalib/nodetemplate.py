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

from translator.toscalib.common.exception import TypeMismatchError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.interfaces import LIFECYCLE, CONFIGURE
from translator.toscalib.entity_template import EntityTemplate

log = logging.getLogger('tosca')


class NodeTemplate(EntityTemplate):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, node_templates, custom_def=None):
        super(NodeTemplate, self).__init__(name, node_templates[name],
                                           'node_type',
                                           custom_def)
        self.templates = node_templates
        self.related = {}

    @property
    def relationship(self):
        relation = {}
        requires = self.requirements
        if requires:
            for r in requires:
                for cap, node in r.items():
                    for rtype in self.type_definition.relationship.keys():
                        if cap == rtype.capability_name:
                            rtpl = NodeTemplate(node, self.templates)
                            relation[rtype] = rtpl
        return relation

    def _add_next(self, nodetpl, relationship):
        self.related[nodetpl] = relationship

    @property
    def related_nodes(self):
        if not self.related:
            for relation, node in self.type_definition.relationship.items():
                for tpl in self.node_templates:
                    if tpl == node.type:
                        self.related[NodeTemplate(tpl)] = relation
        return self.related.keys()

    def ref_property(self, cap, cap_name, property):
        requires = self.type_definition.requirements
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
        self._validate_requirements()
        self._validate_properties(self.entity_tpl, self.type_definition)
        self._validate_interfaces()
        for prop in self.properties:
            prop.validate()

    def _validate_requirements(self):
        type_requires = self.type_definition.get_all_requirements()
        allowed_reqs = ['type', 'properties', 'interfaces']
        if type_requires:
            for treq in type_requires:
                for key in treq:
                    allowed_reqs.append(key)
        requires = self.type_definition.get_value(self.REQUIREMENTS,
                                                  self.entity_tpl)
        if requires:
            if not isinstance(requires, list):
                raise TypeMismatchError(
                    what='Requirements of template %s' % self.name,
                    type='list')
            for req in requires:
                self._common_validate_field(req, allowed_reqs, 'Requirements')

    def _validate_interfaces(self):
        ifaces = self.type_definition.get_value(self.INTERFACES,
                                                self.entity_tpl)
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
                            what='Interfaces of template %s' % self.name,
                            field=name)
