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

import copy
import logging
import os
from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import ValidationError
from toscaparser.extensions.exttools import ExtTools
import toscaparser.utils.yamlparser

log = logging.getLogger('tosca')


class EntityType(object):
    '''Base class for TOSCA elements.'''

    SECTIONS = (DERIVED_FROM, PROPERTIES, ATTRIBUTES, REQUIREMENTS,
                INTERFACES, CAPABILITIES, TYPE, ARTIFACTS) = \
               ('derived_from', 'properties', 'attributes', 'requirements',
                'interfaces', 'capabilities', 'type', 'artifacts')

    '''TOSCA definition file.'''
    TOSCA_DEF_FILE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "TOSCA_definition_1_0.yaml")

    loader = toscaparser.utils.yamlparser.load_yaml

    TOSCA_DEF = loader(TOSCA_DEF_FILE)

    RELATIONSHIP_TYPE = (DEPENDSON, HOSTEDON, CONNECTSTO, ATTACHESTO,
                         LINKSTO, BINDSTO) = \
                        ('tosca.relationships.DependsOn',
                         'tosca.relationships.HostedOn',
                         'tosca.relationships.ConnectsTo',
                         'tosca.relationships.AttachesTo',
                         'tosca.relationships.network.LinksTo',
                         'tosca.relationships.network.BindsTo')

    NODE_PREFIX = 'tosca.nodes.'
    RELATIONSHIP_PREFIX = 'tosca.relationships.'
    CAPABILITY_PREFIX = 'tosca.capabilities.'
    INTERFACE_PREFIX = 'tosca.interfaces.'
    ARTIFACT_PREFIX = 'tosca.artifacts.'
    POLICY_PREFIX = 'tosca.policies.'
    GROUP_PREFIX = 'tosca.groups.'
    # currently the data types are defined only for network
    # but may have changes in the future.
    DATATYPE_PREFIX = 'tosca.datatypes.network.'
    TOSCA = 'tosca'

    def derived_from(self, defs):
        '''Return a type this type is derived from.'''
        return self.entity_value(defs, 'derived_from')

    def is_derived_from(self, type_str):
        '''Check if object inherits from the given type.

        Returns true if this object is derived from 'type_str'.
        False otherwise.
        '''
        if not self.type:
            return False
        elif self.type == type_str:
            return True
        elif self.parent_type:
            return self.parent_type.is_derived_from(type_str)
        else:
            return False

    def entity_value(self, defs, key):
        if key in defs:
            return defs[key]

    def get_value(self, ndtype, defs=None, parent=None):
        value = None
        if defs is None:
            if not hasattr(self, 'defs'):
                return None
            defs = self.defs
        if ndtype in defs:
            # copy the value to avoid that next operations add items in the
            # item definitions
            value = copy.copy(defs[ndtype])
        if parent:
            p = self
            if p:
                while p:
                    if ndtype in p.defs:
                        # get the parent value
                        parent_value = p.defs[ndtype]
                        if value:
                            if isinstance(value, dict):
                                for k, v in parent_value.items():
                                    if k not in value.keys():
                                        value[k] = v
                            if isinstance(value, list):
                                for p_value in parent_value:
                                    if p_value not in value:
                                        value.append(p_value)
                        else:
                            value = copy.copy(parent_value)
                    p = p.parent_type
        return value

    def get_definition(self, ndtype):
        value = None
        if not hasattr(self, 'defs'):
            defs = None
            ExceptionCollector.appendException(
                ValidationError(message="defs is " + str(defs)))
        else:
            defs = self.defs
        if defs is not None and ndtype in defs:
            value = defs[ndtype]
        p = self.parent_type
        if p:
            inherited = p.get_definition(ndtype)
            if inherited:
                inherited = dict(inherited)
                if not value:
                    value = inherited
                else:
                    inherited.update(value)
                    value.update(inherited)
        return value


def update_definitions(version):
    exttools = ExtTools()
    extension_defs_file = exttools.get_defs_file(version)

    loader = toscaparser.utils.yamlparser.load_yaml

    EntityType.TOSCA_DEF.update(loader(extension_defs_file))
