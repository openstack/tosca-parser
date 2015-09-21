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

from toscaparser.common.exception import InvalidPropertyValueError
from toscaparser.common.exception import TypeMismatchError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.dataentity import DataEntity
from toscaparser.elements.interfaces import CONFIGURE
from toscaparser.elements.interfaces import CONFIGURE_SHORTNAME
from toscaparser.elements.interfaces import InterfacesDef
from toscaparser.elements.interfaces import LIFECYCLE
from toscaparser.elements.interfaces import LIFECYCLE_SHORTNAME
from toscaparser.elements.relationshiptype import RelationshipType
from toscaparser.entity_template import EntityTemplate
from toscaparser.relationship_template import RelationshipTemplate
from toscaparser.utils.gettextutils import _

log = logging.getLogger('tosca')


class NodeTemplate(EntityTemplate):
    '''Node template from a Tosca profile.'''
    def __init__(self, name, node_templates, custom_def=None,
                 available_rel_tpls=None, available_rel_types=None):
        super(NodeTemplate, self).__init__(name, node_templates[name],
                                           'node_type',
                                           custom_def)
        self.templates = node_templates
        self._validate_fields(node_templates[name])
        self.custom_def = custom_def
        self.related = {}
        self.relationship_tpl = []
        self.available_rel_tpls = available_rel_tpls
        self.available_rel_types = available_rel_types
        self._relationships = {}

    @property
    def relationships(self):
        if not self._relationships:
            requires = self.requirements
            if requires:
                for r in requires:
                    for r1, value in r.items():
                        explicit = self._get_explicit_relationship(r, value)
                        if explicit:
                            for key, value in explicit.items():
                                self._relationships[key] = value
        return self._relationships

    def _get_explicit_relationship(self, req, value):
        """Handle explicit relationship

        For example,
        - req:
            node: DBMS
            relationship: tosca.relationships.HostedOn
        """
        explicit_relation = {}
        node = value.get('node') if isinstance(value, dict) else value

        if node:
            # TODO(spzala) implement look up once Glance meta data is available
            # to find a matching TOSCA node using the TOSCA types
            msg = _('Lookup by TOSCA types are not supported. '
                    'Requirement for %s can not be full-filled.') % self.name
            if (node in list(self.type_definition.TOSCA_DEF.keys())
               or node in self.custom_def):
                    raise NotImplementedError(msg)
            related_tpl = NodeTemplate(node, self.templates, self.custom_def)
            relationship = value.get('relationship') \
                if isinstance(value, dict) else None
            # check if it's type has relationship defined
            if not relationship:
                parent_reqs = self.type_definition.get_all_requirements()
                for key in req.keys():
                    for req_dict in parent_reqs:
                        if key in req_dict.keys():
                            relationship = (req_dict.get(key).
                                            get('relationship'))
                            break
            if relationship:
                found_relationship_tpl = False
                # apply available relationship templates if found
                for tpl in self.available_rel_tpls:
                    if tpl.name == relationship:
                        rtype = RelationshipType(tpl.type, None,
                                                 self.custom_def)
                        explicit_relation[rtype] = related_tpl
                        self.relationship_tpl.append(tpl)
                        found_relationship_tpl = True
                # create relationship template object.
                rel_prfx = self.type_definition.RELATIONSHIP_PREFIX
                if not found_relationship_tpl:
                    if isinstance(relationship, dict):
                        relationship = relationship.get('type')
                        if self.available_rel_types and \
                           relationship in self.available_rel_types.keys():
                            pass
                        elif not relationship.startswith(rel_prfx):
                            relationship = rel_prfx + relationship
                    for rtype in self.type_definition.relationship.keys():
                        if rtype.type == relationship:
                            explicit_relation[rtype] = related_tpl
                            related_tpl._add_relationship_template(req,
                                                                   rtype.type)
                        elif self.available_rel_types:
                            if relationship in self.available_rel_types.keys():
                                rel_type_def = self.available_rel_types.\
                                    get(relationship)
                                if 'derived_from' in rel_type_def:
                                    super_type = \
                                        rel_type_def.get('derived_from')
                                    if not super_type.startswith(rel_prfx):
                                        super_type = rel_prfx + super_type
                                    if rtype.type == super_type:
                                        explicit_relation[rtype] = related_tpl
                                        related_tpl.\
                                            _add_relationship_template(
                                                req, rtype.type)
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
                for key, value in treq.items():
                    allowed_reqs.append(key)
                    if isinstance(value, dict):
                        for key in value:
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
                        self._validate_requirements_keys(value)
                        self._validate_requirements_properties(value)
                        allowed_reqs.append(r1)
                self._common_validate_field(req, allowed_reqs, 'Requirements')

    def _validate_requirements_properties(self, requirements):
        # TODO(anyone): Only occurences property of the requirements is
        # validated here. Validation of other requirement properties are being
        # validated in different files. Better to keep all the requirements
        # properties validation here.
        for key, value in requirements.items():
            if key == 'occurrences':
                self._validate_occurrences(value)
                break

    def _validate_occurrences(self, occurrences):
        DataEntity.validate_datatype('list', occurrences)
        for value in occurrences:
            DataEntity.validate_datatype('integer', value)
        if len(occurrences) != 2 or not (0 <= occurrences[0] <= occurrences[1]) \
            or occurrences[1] == 0:
            raise InvalidPropertyValueError(what=(occurrences))

    def _validate_requirements_keys(self, requirement):
        for key in requirement.keys():
            if key not in self.REQUIREMENTS_SECTION:
                raise UnknownFieldError(
                    what='Requirements of template %s' % self.name,
                    field=key)

    def _validate_interfaces(self):
        ifaces = self.type_definition.get_value(self.INTERFACES,
                                                self.entity_tpl)
        if ifaces:
            for i in ifaces:
                for name, value in ifaces.items():
                    if name in (LIFECYCLE, LIFECYCLE_SHORTNAME):
                        self._common_validate_field(
                            value, InterfacesDef.
                            interfaces_node_lifecycle_operations,
                            'Interfaces')
                    elif name in (CONFIGURE, CONFIGURE_SHORTNAME):
                        self._common_validate_field(
                            value, InterfacesDef.
                            interfaces_relationship_confiure_operations,
                            'Interfaces')
                    else:
                        raise UnknownFieldError(
                            what='Interfaces of template %s' % self.name,
                            field=name)

    def _validate_fields(self, nodetemplate):
        for name in nodetemplate.keys():
            if name not in self.SECTIONS and name not in self.SPECIAL_SECTIONS:
                raise UnknownFieldError(what='Node template %s'
                                        % self.name, field=name)
