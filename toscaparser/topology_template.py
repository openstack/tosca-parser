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
        """
        Initialize the graph

        Args:
            self: (todo): write your description
            template: (str): write your description
            custom_defs: (todo): write your description
            rel_types: (todo): write your description
            parsed_params: (dict): write your description
            sub_mapped_node_template: (todo): write your description
        """
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
        """
        Return a list of input inputs.

        Args:
            self: (todo): write your description
        """
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
        """
        Return a list of template definitions that name definitions.

        Args:
            self: (todo): write your description
        """
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
        """
        Return a list of relationship objects.

        Args:
            self: (todo): write your description
        """
        rel_templates = []
        tpls = self._tpl_relationship_templates()
        for name in tpls:
            tpl = RelationshipTemplate(tpls[name], name, self.custom_defs)
            rel_templates.append(tpl)
        return rel_templates

    def _outputs(self):
        """
        Return a list of outputs.

        Args:
            self: (todo): write your description
        """
        outputs = []
        for name, attrs in self._tpl_outputs().items():
            output = Output(name, attrs)
            output.validate()
            outputs.append(output)
        return outputs

    def _substitution_mappings(self):
        """
        Substitution substitution.

        Args:
            self: (todo): write your description
        """
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
        """
        Return the policies list of policies.

        Args:
            self: (todo): write your description
        """
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
        """
        Return a list of group names.

        Args:
            self: (todo): write your description
        """
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
        """
        Return a list of member members.

        Args:
            self: (todo): write your description
            member_names: (str): write your description
        """
        member_nodes = []
        self._validate_group_members(member_names)
        for member in member_names:
            for node in self.nodetemplates:
                if node.name == member:
                    member_nodes.append(node)
        return member_nodes

    def _get_policy_groups(self, member_names):
        """
        Returns a list of member groups.

        Args:
            self: (todo): write your description
            member_names: (str): write your description
        """
        member_groups = []
        for member in member_names:
            for group in self.groups:
                if group.name == member:
                    member_groups.append(group)
        return member_groups

    def _validate_group_members(self, members):
        """
        Validate the group members.

        Args:
            self: (todo): write your description
            members: (todo): write your description
        """
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
        """
        Nodetyetype of this node.

        Args:
            self: (todo): write your description
        """
        return self.substitution_mappings.node_type \
            if self.substitution_mappings else None

    def capabilities(self):
        """
        : class : class.

        Args:
            self: (todo): write your description
        """
        return self.substitution_mappings.capabilities \
            if self.substitution_mappings else None

    def requirements(self):
        """
        : class : class.

        Args:
            self: (todo): write your description
        """
        return self.substitution_mappings.requirements \
            if self.substitution_mappings else None

    def _tpl_description(self):
        """
        Get the description of the description.

        Args:
            self: (todo): write your description
        """
        description = self.tpl.get(DESCRIPTION)
        if description:
            return description.rstrip()

    def _tpl_inputs(self):
        """
        Returns a list of input inputs.

        Args:
            self: (todo): write your description
        """
        inputs = self.tpl.get(INPUTS) or {}
        if not isinstance(inputs, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=INPUTS, type="dict"))
        return inputs

    def _tpl_nodetemplates(self):
        """
        Returns a list of all available templates.

        Args:
            self: (todo): write your description
        """
        nodetemplates = self.tpl.get(NODE_TEMPLATES)
        if nodetemplates and not isinstance(nodetemplates, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=NODE_TEMPLATES, type="dict"))
        return nodetemplates

    def _tpl_relationship_templates(self):
        """
        Return a relationship between all relationship

        Args:
            self: (todo): write your description
        """
        relationship_templates = self.tpl.get(RELATIONSHIP_TEMPLATES) or {}
        if not isinstance(relationship_templates, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=RELATIONSHIP_TEMPLATES,
                                            type="dict"))
        return relationship_templates

    def _tpl_outputs(self):
        """
        Returns a list of outputs.

        Args:
            self: (todo): write your description
        """
        outputs = self.tpl.get(OUTPUTS) or {}
        if not isinstance(outputs, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=OUTPUTS, type="dict"))
        return outputs

    def _tpl_substitution_mappings(self):
        """
        Return a list of substitutions.

        Args:
            self: (todo): write your description
        """
        substitution_mappings = self.tpl.get(SUBSTITUION_MAPPINGS) or {}
        if not isinstance(substitution_mappings, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=SUBSTITUION_MAPPINGS,
                                            type="dict"))
        return substitution_mappings

    def _tpl_groups(self):
        """
        Returns a list.

        Args:
            self: (todo): write your description
        """
        groups = self.tpl.get(GROUPS) or {}
        if not isinstance(groups, dict):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=GROUPS, type="dict"))
        return groups

    def _tpl_policies(self):
        """
        Return a list of policies.

        Args:
            self: (todo): write your description
        """
        policies = self.tpl.get(POLICIES) or []
        if not isinstance(policies, list):
            exception.ExceptionCollector.appendException(
                exception.TypeMismatchError(what=POLICIES, type="list"))
        return policies

    def _validate_field(self):
        """
        { type : attr : field.

        Args:
            self: (todo): write your description
        """
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
        """
        Returns a mapping between the submap_tplitution.

        Args:
            cls: (todo): write your description
            topology_tpl: (dict): write your description
        """
        if topology_tpl and isinstance(topology_tpl, dict):
            submap_tpl = topology_tpl.get(SUBSTITUION_MAPPINGS)
            return SubstitutionMappings.get_node_type(submap_tpl)
