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
from toscaparser import functions
from toscaparser.groups import NodeGroup
from toscaparser.nodetemplate import NodeTemplate
from toscaparser.parameters import Input
from toscaparser.parameters import Output
from toscaparser.relationship_template import RelationshipTemplate
from toscaparser.tpl_relationship_graph import ToscaGraph


# Topology template key names
SECTIONS = (DESCRIPTION, INPUTS, NODE_TEMPLATES,
            RELATIONSHIP_TEMPLATES, OUTPUTS, GROUPS,
            SUBSTITUION_MAPPINGS) = \
           ('description', 'inputs', 'node_templates',
            'relationship_templates', 'outputs', 'groups',
            'substitution_mappings')

log = logging.getLogger("tosca.model")


class TopologyTemplate(object):

    '''Load the template data.'''
    def __init__(self, template, custom_defs,
                 rel_types=None, parsed_params=None):
        self.tpl = template
        self.custom_defs = custom_defs
        self.rel_types = rel_types
        self.parsed_params = parsed_params
        self._validate_field()
        self.description = self._tpl_description()
        self.inputs = self._inputs()
        self.relationship_templates = self._relationship_templates()
        self.nodetemplates = self._nodetemplates()
        self.outputs = self._outputs()
        self.graph = ToscaGraph(self.nodetemplates)
        self.groups = self._groups()
        self._process_intrinsic_functions()

    def _inputs(self):
        inputs = []
        for name, attrs in self._tpl_inputs().items():
            input = Input(name, attrs)
            if self.parsed_params and name in self.parsed_params:
                input.validate(self.parsed_params[name])
            inputs.append(input)
        return inputs

    def _nodetemplates(self):
        nodetemplates = []
        tpls = self._tpl_nodetemplates()
        for name in tpls:
            tpl = NodeTemplate(name, tpls, self.custom_defs,
                               self.relationship_templates,
                               self.rel_types)
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
        pass

    def _groups(self):
        groups = []
        for group_name, group_tpl in self._tpl_groups().items():
            member_names = group_tpl.get('members')
            if member_names and len(member_names) > 1:
                group = NodeGroup(group_name, group_tpl,
                                  self._get_group_memerbs(member_names))
                groups.append(group)
            else:
                raise ValueError
        return groups

    def _get_group_memerbs(self, member_names):
        member_nodes = []
        for member in member_names:
            for node in self.nodetemplates:
                if node.name == member:
                    member_nodes.append(node)
        return member_nodes

    # topology template can act like node template
    # it is exposed by substitution_mappings.
    def nodetype(self):
        pass

    def capabilities(self):
        pass

    def requirements(self):
        pass

    def _tpl_description(self):
        description = self.tpl.get(DESCRIPTION)
        if description:
            description = description.rstrip()
        return description

    def _tpl_inputs(self):
        return self.tpl.get(INPUTS) or {}

    def _tpl_nodetemplates(self):
        return self.tpl[NODE_TEMPLATES]

    def _tpl_relationship_templates(self):
        return self.tpl.get(RELATIONSHIP_TEMPLATES) or {}

    def _tpl_outputs(self):
        return self.tpl.get(OUTPUTS) or {}

    def _tpl_substitution_mappings(self):
        return self.tpl.get(SUBSTITUION_MAPPINGS) or {}

    def _tpl_groups(self):
        return self.tpl.get(GROUPS) or {}

    def _validate_field(self):
        for name in self.tpl:
            if name not in SECTIONS:
                raise exception.UnknownFieldError(what='Template', field=name)

    def _process_intrinsic_functions(self):
        """Process intrinsic functions

        Current implementation processes functions within node template
        properties, requirements, interfaces inputs and template outputs.
        """
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
            if node_template.requirements:
                for req in node_template.requirements:
                    rel = req
                    for req_name, req_item in req.items():
                        if isinstance(req_item, dict):
                            rel = req_item.get('relationship')
                            break
                    if rel and 'properties' in rel:
                        for key, value in rel['properties'].items():
                            rel['properties'][key] = functions.get_function(
                                self,
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
                                for name, value in interface.inputs.items():
                                    interface.inputs[name] = \
                                        functions.get_function(self,
                                                               rel_tpl,
                                                               value)
        for output in self.outputs:
            func = functions.get_function(self, self.outputs, output.value)
            if isinstance(func, functions.GetAttribute):
                output.attrs[output.VALUE] = func
