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
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError


log = logging.getLogger('tosca')


class SubstitutionMappings(object):
    '''SubstitutionMappings class declaration

    SubstitutionMappings exports the topology template as an
    implementation of a Node type.
    '''

    SECTIONS = (NODE_TYPE, REQUIREMENTS, CAPABILITIES) = \
               ('node_type', 'requirements', 'capabilities')

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
            return self.sub_mapping_def['node_type']

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

    def _validate(self):
        self._validate_keys()
        self._validate_type()
        self._validate_inputs()
        self._validate_capabilities()
        self._validate_requirements()
        self._validate_outputs()

    def _validate_keys(self):
        """validate the keys of substitution mappings."""
        for key in self.sub_mapping_def.keys():
            if key not in self.SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='SubstitutionMappings',
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
                InvalidNodeTypeError(what=node_type_def))

    def _validate_inputs(self):
        """validate the inputs of substitution mappings."""

        # The inputs in service template which defines substutition mappings
        # must be in properties of node template which is mapped or provide
        # defualt value. Currently the input.name is not restrict to be the
        # same as properte's name in specification, but they should be equal
        # for current implementation.
        property_names = list(self.sub_mapped_node_template
                              .get_properties().keys()
                              if self.sub_mapped_node_template else [])
        for input in self.inputs:
            if input.name not in property_names and input.default is None:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='SubstitutionMappings',
                                      field=input.name))

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
        """validate the outputs of substitution mappings."""
        pass
        # The outputs in service template which defines substutition mappings
        # must be in atrributes of node template wchich be mapped.
        # outputs_names = self.sub_mapped_node_template.get_properties().
        #     keys() if self.sub_mapped_node_template else None
        # for name in outputs_names:
        #    if name not in [output.name for input in self.outputs]:
        #        ExceptionCollector.appendException(
        #            UnknownFieldError(what='SubstitutionMappings',
        #                              field=name))
