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
from translator.toscalib.elements.relationshiptype import RelationshipType
from translator.toscalib.entity_template import EntityTemplate
from translator.toscalib.relationship_template import RelationshipTemplate
from translator.toscalib.utils.gettextutils import _

log = logging.getLogger('tosca')


class NodeTemplate(EntityTemplate):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, node_templates, custom_def=None,
                 available_rel_tpls=None):
        super(NodeTemplate, self).__init__(name, node_templates[name],
                                           'node_type',
                                           custom_def)
        self.templates = node_templates
        self.custom_def = custom_def
        self.related = {}
        self.relationship_tpl = []
        self.available_rel_tpls = available_rel_tpls
        self._relationships = {}

    @property
    def relationships(self):
        if not self._relationships:
            requires = self.requirements
            if requires:
                for r in requires:
                    for r1, value in r.items():
                        if isinstance(value, dict):
                            explicit = self._get_explicit_relationship(
                                r, value)
                            if explicit:
                                for key, value in explicit.items():
                                    self._relationships[key] = value
                        else:
                            keys = self.type_definition.relationship.keys()
                            for rtype in keys:
                                if r1 == rtype.capability_name:
                                    related_tpl = NodeTemplate(
                                        value, self.templates,
                                        self.custom_def)
                                    self._relationships[rtype] = related_tpl
                                    related_tpl._add_relationship_template(
                                        r, rtype.type)
        return self._relationships

    def _get_explicit_relationship(self, req, value):
        """Handle explicit relationship

        For example,
        - req:
            node: DBMS
            relationship: tosca.relationships.HostedOn
        """
        explicit_relation = {}
        node = value.get('node')
        if node:
            #TODO(spzala) implement look up once Glance meta data is available
            #to find a matching TOSCA node using the TOSCA types
            msg = _('Lookup by TOSCA types are not supported. '
                    'Requirement for %s can not be full-filled.') % self.name
            if (node in list(self.type_definition.TOSCA_DEF.keys())
               or node in self.custom_def):
                    raise NotImplementedError(msg)
            related_tpl = NodeTemplate(node, self.templates, self.custom_def)
            relationship = value.get('relationship')
            if relationship:
                found_relationship_tpl = False
                #apply available relationship templates if found
                for tpl in self.available_rel_tpls:
                    if tpl.name == relationship:
                        rtype = RelationshipType(tpl.type)
                        explicit_relation[rtype] = related_tpl
                        self.relationship_tpl.append(tpl)
                        found_relationship_tpl = True
                #create relationship template object.
                if not found_relationship_tpl:
                    if isinstance(relationship, dict):
                        relationship = relationship.get('type')
                    for rtype in self.type_definition.relationship.keys():
                        if rtype.type == relationship:
                            explicit_relation[rtype] = related_tpl
                            related_tpl._add_relationship_template(req,
                                                                   rtype.type)
        return explicit_relation

    def _add_relationship_template(self, requirement, rtype):
        req = requirement.copy()
        req['type'] = rtype
        tpl = RelationshipTemplate(req, rtype, None)
        self.relationship_tpl.append(tpl)

    def get_relationship_template(self):
        return self.relationship_tpl

    def _add_next(self, nodetpl, relationship):
        self.related[nodetpl] = relationship

    @property
    def related_nodes(self):
        if not self.related:
            for relation, node in self.type_definition.relationship.items():
                for tpl in self.templates:
                    if tpl == node.type:
                        self.related[NodeTemplate(tpl)] = relation
        return self.related.keys()

    def validate(self, tosca_tpl=None):
        self._validate_capabilities()
        self._validate_requirements()
        self._validate_properties(self.entity_tpl, self.type_definition)
        self._validate_interfaces()
        for prop in self.get_properties_objects():
            prop.validate()

    def _validate_requirements(self):
        type_requires = self.type_definition.get_all_requirements()
        allowed_reqs = ["template"]
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
                for r1, value in req.items():
                    if isinstance(value, dict):
                        allowed_reqs.append(r1)
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
