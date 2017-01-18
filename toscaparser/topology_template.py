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

from toscaparser.common import exception
from toscaparser.dataentity import DataEntity
from toscaparser import functions
from toscaparser.groups import Group
from toscaparser.nodetemplate import NodeTemplate
from toscaparser.parameters import Input
from toscaparser.parameters import Output
from toscaparser.policy import Policy
from toscaparser.relationship_template import RelationshipTemplate
from toscaparser.substitution_mappings import SubstitutionMappings
from toscaparser.tpl_relationship_graph import ToscaGraph
from toscaparser.utils.gettextutils import _


# Topology template key names
SECTIONS = (DESCRIPTION, INPUTS, NODE_TEMPLATES,
            RELATIONSHIP_TEMPLATES, OUTPUTS, GROUPS,
            SUBSTITUION_MAPPINGS, POLICIES) = \
           ('description', 'inputs', 'node_templates',
            'relationship_templates', 'outputs', 'groups',
            'substitution_mappings', 'policies')

log = logging.getLogger("tosca.model")


class TopologyTemplate(object):

    '''Load the template data.'''
    def __init__(self, template, custom_defs,
                 rel_types=None, parsed_params=None,
                 sub_mapped_node_template=None):
        self.tpl = template
        self.sub_mapped_node_template = sub_mapped_node_template
        if self.tpl:
            self.custom_defs = custom_defs
            self.rel_types = rel_types
            self.parsed_params = parsed_params
            self._validate_field()
            self.description = self._tpl_description()
            self.inputs = self._inputs()
            self.relationship_templates = self._relationship_templates()
            self.nodetemplates = self._nodetemplates()
            self.outputs = self._outputs()
            if hasattr(self, 'nodetemplates'):
                self.graph = ToscaGraph(self.nodetemplates)
            self.groups = self._groups()
            self.policies = self._policies()
            self._process_intrinsic_functions()
            self.substitution_mappings = self._substitution_mappings()

    def _inputs(self):
        inputs = []
        for name, attrs in self._tpl_inputs().items():
            input = Input(name, attrs)
            if self.parsed_params and name in self.parsed_params:
                input.validate(self.parsed_params[name])
            else:
                default = input.default
                if default:
                    input.validate(default)
            if (self.parsed_params and input.name not in self.parsed_params
                or self.parsed_params is None) and input.required \
                    and input.default is None:
                log.warning(_('The required parameter %s '
                              'is not provided') % input.name)

            inputs.append(input)
        return inputs

    def _nodetemplates(self):
        nodetemplates = []
        tpls = self._tpl_nodetemplates()
        if tpls:
            for name in tpls:
                tpl = NodeTemplate(name, tpls, self.custom_defs,
                                   self.relationship_templates,
                                   self.rel_types)
                if (tpl.type_definition and
                    (tpl.type in tpl.type_definition.TOSCA_DEF or
                     (tpl.type not in tpl.type_definition.TOSCA_DEF and
                      bool(tpl.custom_def)))):
                    tpl.validate(self)
                    nodetemplates.append(tpl)
        return nodetemplates

    def _relationship_templates(self):
        rel_templates = []
        tpls = self._tpl_relationship_templates()
        for name in tpls:
            tpl = RelationshipTemplate(tpls[name], name, self.custom_defs)
            rel_templates.append(tpl)
        return rel_templates

    def _outputs(self):
        outputs = []
        for name, attrs in self._tpl_outputs().items():
            output = Output(name, attrs)
            output.validate()
            outputs.append(output)
        return outputs

    def _substitution_mappings(self):
        tpl_substitution_mapping = self._tpl_substitution_mappings()
        # if tpl_substitution_mapping and self.sub_mapped_node_template:
        if tpl_substitution_mapping:
            return SubstitutionMappings(tpl_substitution_mapping,
                                        self.nodetemplates,
                                        self.inputs,
                                        self.outputs,
                                        self.sub_mapped_node_template,
                                        self.custom_defs)

    def _policies(self):
        policies = []
        for policy in self._tpl_policies():
            for policy_name, policy_tpl in policy.items():
                target_list = policy_tpl.get('targets')
                target_objects = []
                targets_type = "groups"
                if target_list and len(target_list) >= 1:
                    target_objects = self._get_policy_groups(target_list)
                    if not target_objects:
                        targets_type = "node_templates"
                        target_objects = self._get_group_members(target_list)
                policyObj = Policy(policy_name, policy_tpl,
                                   target_objects, targets_type,
                                   self.custom_defs)
                policies.append(policyObj)
        return policies

    def _groups(self):
        groups = []
        member_nodes = None
        for group_name, group_tpl in self._tpl_groups().items():
            member_names = group_tpl.get('members')
            if member_names is not None:
                DataEntity.validate_datatype('list', member_names)
                if len(member_names) < 1 or \
                        len(member_names) != len(set(member_names)):
                    exception.ExceptionCollector.appendException(
                        exception.InvalidGroupTargetException(
                            message=_('Member nodes "%s" should be >= 1 '
                                      'and not repeated') % member_names))
                else:
                    member_nodes = self._get_group_members(member_names)
            group = Group(group_name, group_tpl,
                          member_nodes,
                          self.custom_defs)
            groups.append(group)
        return groups

    def _get_group_members(self, member_names):
        member_nodes = []
        self._validate_group_members(member_names)
        for member in member_names:
            for node in self.nodetemplates:
                if node.name == member:
                    member_nodes.append(node)
        return member_nodes

    def _get_policy_groups(self, member_names):
        member_groups = []
        for member in member_names:
            for group in self.groups:
                if group.name == member:
                    member_groups.append(group)
        return member_groups

    def _validate_group_members(self, members):
        node_names = []
        for node in self.nodetemplates:
            node_names.append(node.name)
        for member in members:
            if member not in node_names:
                exception.ExceptionCollector.appendException(
                    exception.InvalidGroupTargetException(
                        message=_('Target member "%s" is not found in '
                                  'node_templates') % member))

    # topology template can act like node template
    # it is exposed by substitution_mappings.
    def nodetype(self):
        return self.substitution_mappings.node_type \
            if self.substitution_mappings else None

    def capabilities(self):
        return self.substitution_mappings.capabilities \
            if self.substitution_mappings else None

    def requirements(self):
        return self.substitution_mappings.requirements \
            if self.substitution_mappings else None

    def _tpl_description(self):
        description = self.tpl.get(DESCRIPTION)
        if description:
            return description.rstrip()

    def _tpl_inputs(self):
        return self.tpl.get(INPUTS) or {}

    def _tpl_nodetemplates(self):
        return self.tpl.get(NODE_TEMPLATES)

    def _tpl_relationship_templates(self):
        return self.tpl.get(RELATIONSHIP_TEMPLATES) or {}

    def _tpl_outputs(self):
        return self.tpl.get(OUTPUTS) or {}

    def _tpl_substitution_mappings(self):
        return self.tpl.get(SUBSTITUION_MAPPINGS) or {}

    def _tpl_groups(self):
        return self.tpl.get(GROUPS) or {}

    def _tpl_policies(self):
        return self.tpl.get(POLICIES) or {}

    def _validate_field(self):
        for name in self.tpl:
            if name not in SECTIONS:
                exception.ExceptionCollector.appendException(
                    exception.UnknownFieldError(what='Template', field=name))

    def _process_intrinsic_functions(self):
        """Process intrinsic functions

        Current implementation processes functions within node template
        properties, requirements, interfaces inputs and template outputs.
        """
        if hasattr(self, 'nodetemplates'):
            for node_template in self.nodetemplates:
                for prop in node_template.get_properties_objects():
                    prop.value = functions.get_function(self,
                                                        node_template,
                                                        prop.value)
                for interface in node_template.interfaces:
                    if interface.inputs:
                        for name, value in interface.inputs.items():
                            interface.inputs[name] = functions.get_function(
                                self,
                                node_template,
                                value)
                if node_template.requirements and \
                   isinstance(node_template.requirements, list):
                    for req in node_template.requirements:
                        rel = req
                        for req_name, req_item in req.items():
                            if isinstance(req_item, dict):
                                rel = req_item.get('relationship')
                                break
                        if rel and 'properties' in rel:
                            for key, value in rel['properties'].items():
                                rel['properties'][key] = \
                                    functions.get_function(self,
                                                           req,
                                                           value)
                if node_template.get_capabilities_objects():
                    for cap in node_template.get_capabilities_objects():
                        if cap.get_properties_objects():
                            for prop in cap.get_properties_objects():
                                propvalue = functions.get_function(
                                    self,
                                    node_template,
                                    prop.value)
                                if isinstance(propvalue, functions.GetInput):
                                    propvalue = propvalue.result()
                                    for p, v in cap._properties.items():
                                        if p == prop.name:
                                            cap._properties[p] = propvalue
                for rel, node in node_template.relationships.items():
                    rel_tpls = node.relationship_tpl
                    if rel_tpls:
                        for rel_tpl in rel_tpls:
                            for interface in rel_tpl.interfaces:
                                if interface.inputs:
                                    for name, value in \
                                            interface.inputs.items():
                                        interface.inputs[name] = \
                                            functions.get_function(self,
                                                                   rel_tpl,
                                                                   value)
        for output in self.outputs:
            func = functions.get_function(self, self.outputs, output.value)
            if isinstance(func, functions.GetAttribute):
                output.attrs[output.VALUE] = func

    @classmethod
    def get_sub_mapping_node_type(cls, topology_tpl):
        if topology_tpl and isinstance(topology_tpl, dict):
            submap_tpl = topology_tpl.get(SUBSTITUION_MAPPINGS)
            return SubstitutionMappings.get_node_type(submap_tpl)
