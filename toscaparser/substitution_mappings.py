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

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidNodeTypeError
from toscaparser.common.exception import MissingDefaultValueError
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import MissingRequiredInputError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import UnknownOutputError
from toscaparser.elements.nodetype import NodeType
from toscaparser.utils.gettextutils import _

log = logging.getLogger('tosca')


class SubstitutionMappings(object):
    '''SubstitutionMappings class declaration

    SubstitutionMappings exports the topology template as an
    implementation of a Node type.
    '''

    SECTIONS = (NODE_TYPE, REQUIREMENTS, CAPABILITIES) = \
               ('node_type', 'requirements', 'capabilities')

    OPTIONAL_OUTPUTS = ['tosca_id', 'tosca_name', 'state']

    def __init__(self, sub_mapping_def, nodetemplates, inputs, outputs,
                 sub_mapped_node_template, custom_defs):
        self.nodetemplates = nodetemplates
        self.sub_mapping_def = sub_mapping_def
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.sub_mapped_node_template = sub_mapped_node_template
        self.custom_defs = custom_defs or {}
        self._validate()

        self._capabilities = None
        self._requirements = None

    @property
    def type(self):
        if self.sub_mapping_def:
            return self.sub_mapping_def.get(self.NODE_TYPE)

    @classmethod
    def get_node_type(cls, sub_mapping_def):
        if isinstance(sub_mapping_def, dict):
            return sub_mapping_def.get(cls.NODE_TYPE)

    @property
    def node_type(self):
        return self.sub_mapping_def.get(self.NODE_TYPE)

    @property
    def capabilities(self):
        return self.sub_mapping_def.get(self.CAPABILITIES)

    @property
    def requirements(self):
        return self.sub_mapping_def.get(self.REQUIREMENTS)

    @property
    def node_definition(self):
        return NodeType(self.node_type, self.custom_defs)

    def _validate(self):
        # Basic validation
        self._validate_keys()
        self._validate_type()

        # SubstitutionMapping class syntax validation
        self._validate_inputs()
        self._validate_capabilities()
        self._validate_requirements()
        self._validate_outputs()

    def _validate_keys(self):
        """validate the keys of substitution mappings."""
        for key in self.sub_mapping_def.keys():
            if key not in self.SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what=_('SubstitutionMappings'),
                                      field=key))

    def _validate_type(self):
        """validate the node_type of substitution mappings."""
        node_type = self.sub_mapping_def.get(self.NODE_TYPE)
        if not node_type:
            ExceptionCollector.appendException(
                MissingRequiredFieldError(
                    what=_('SubstitutionMappings used in topology_template'),
                    required=self.NODE_TYPE))

        node_type_def = self.custom_defs.get(node_type)
        if not node_type_def:
            ExceptionCollector.appendException(
                InvalidNodeTypeError(what=node_type))

    def _validate_inputs(self):
        """validate the inputs of substitution mappings.

        The inputs defined by the topology template have to match the
        properties of the node type or the substituted node. If there are
        more inputs than the substituted node has properties, default values
        must be defined for those inputs.
        """

        all_inputs = set([input.name for input in self.inputs])
        required_properties = set([p.name for p in
                                   self.node_definition.
                                   get_properties_def_objects()
                                   if p.required and p.default is None])
        # Must provide inputs for required properties of node type.
        for property in required_properties:
            # Check property which is 'required' and has no 'default' value
            if property not in all_inputs:
                ExceptionCollector.appendException(
                    MissingRequiredInputError(
                        what=_('SubstitutionMappings with node_type ')
                        + self.node_type,
                        input_name=property))

        # If the optional properties of node type need to be customized by
        # substituted node, it also is necessary to define inputs for them,
        # otherwise they are not mandatory to be defined.
        customized_parameters = set(self.sub_mapped_node_template
                                    .get_properties().keys()
                                    if self.sub_mapped_node_template else [])
        all_properties = set(self.node_definition.get_properties_def())
        for parameter in customized_parameters - all_inputs:
            if parameter in all_properties:
                ExceptionCollector.appendException(
                    MissingRequiredInputError(
                        what=_('SubstitutionMappings with node_type ')
                        + self.node_type,
                        input_name=parameter))

        # Additional inputs are not in the properties of node type must
        # provide default values. Currently the scenario may not happen
        # because of parameters validation in nodetemplate, here is a
        # guarantee.
        for input in self.inputs:
            if input.name in all_inputs - all_properties \
               and input.default is None:
                ExceptionCollector.appendException(
                    MissingDefaultValueError(
                        what=_('SubstitutionMappings with node_type ')
                        + self.node_type,
                        input_name=input.name))

    def _validate_capabilities(self):
        """validate the capabilities of substitution mappings."""

        # The capabilites must be in node template wchich be mapped.
        tpls_capabilities = self.sub_mapping_def.get(self.CAPABILITIES)
        node_capabiliteys = self.sub_mapped_node_template.get_capabilities() \
            if self.sub_mapped_node_template else None
        for cap in node_capabiliteys.keys() if node_capabiliteys else []:
            if (tpls_capabilities and
                    cap not in list(tpls_capabilities.keys())):
                pass
                # ExceptionCollector.appendException(
                #    UnknownFieldError(what='SubstitutionMappings',
                #                      field=cap))

    def _validate_requirements(self):
        """validate the requirements of substitution mappings."""

        # The requirements must be in node template wchich be mapped.
        tpls_requirements = self.sub_mapping_def.get(self.REQUIREMENTS)
        node_requirements = self.sub_mapped_node_template.requirements \
            if self.sub_mapped_node_template else None
        for req in node_requirements if node_requirements else []:
            if (tpls_requirements and
                    req not in list(tpls_requirements.keys())):
                pass
                # ExceptionCollector.appendException(
                #    UnknownFieldError(what='SubstitutionMappings',
                #                      field=req))

    def _validate_outputs(self):
        """validate the outputs of substitution mappings.

        The outputs defined by the topology template have to match the
        attributes of the node type or the substituted node template,
        and the observable attributes of the substituted node template
        have to be defined as attributes of the node type or outputs in
        the topology template.
        """

        # The outputs defined by the topology template have to match the
        # attributes of the node type according to the specification, but
        # it's reasonable that there are more inputs than the node type
        # has properties, the specification will be amended?
        for output in self.outputs:
            if output.name not in self.node_definition.get_attributes_def():
                ExceptionCollector.appendException(
                    UnknownOutputError(
                        where=_('SubstitutionMappings with node_type ')
                        + self.node_type,
                        output_name=output.name))
