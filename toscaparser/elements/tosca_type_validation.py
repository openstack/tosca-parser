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

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTemplateVersion
from toscaparser.common.exception import UnknownFieldError
from toscaparser.extensions.exttools import ExtTools


class TypeValidation(object):

    ALLOWED_TYPE_SECTIONS = (DEFINITION_VERSION, DESCRIPTION, IMPORTS,
                             DSL_DEFINITIONS, NODE_TYPES, REPOSITORIES,
                             DATA_TYPES, ARTIFACT_TYPES, GROUP_TYPES,
                             RELATIONSHIP_TYPES, CAPABILITY_TYPES,
                             INTERFACE_TYPES, POLICY_TYPES,
                             TOPOLOGY_TEMPLATE) = \
        ('tosca_definitions_version', 'description', 'imports',
         'dsl_definitions', 'node_types', 'repositories',
         'data_types', 'artifact_types', 'group_types',
         'relationship_types', 'capability_types',
         'interface_types', 'policy_types', 'topology_template')
    VALID_TEMPLATE_VERSIONS = ['tosca_simple_yaml_1_0']
    exttools = ExtTools()
    VALID_TEMPLATE_VERSIONS.extend(exttools.get_versions())

    def __init__(self, custom_types, import_def):
        self.import_def = import_def
        self._validate_type_keys(custom_types)

    def _validate_type_keys(self, custom_type):
        version = custom_type[self.DEFINITION_VERSION] \
            if self.DEFINITION_VERSION in custom_type \
            else None
        if version:
            self._validate_type_version(version)
            self.version = version

        for name in custom_type:
            if name not in self.ALLOWED_TYPE_SECTIONS:
                ExceptionCollector.appendException(
                    UnknownFieldError(what='Template ' + str(self.import_def),
                                      field=name))

    def _validate_type_version(self, version):
        if version not in self.VALID_TEMPLATE_VERSIONS:
            ExceptionCollector.appendException(
                InvalidTemplateVersion(
                    what=version + ' in ' + str(self.import_def),
                    valid_versions=', '. join(self.VALID_TEMPLATE_VERSIONS)))
