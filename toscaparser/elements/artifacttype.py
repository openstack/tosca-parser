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

from toscaparser.elements.statefulentitytype import StatefulEntityType


class ArtifactTypeDef(StatefulEntityType):
    '''TOSCA built-in artifacts type.'''

    def __init__(self, atype, custom_def=None):
        super(ArtifactTypeDef, self).__init__(atype, self.ARTIFACT_PREFIX,
                                              custom_def)
        self.type = atype
        self.properties = None
        if self.PROPERTIES in self.defs:
            self.properties = self.defs[self.PROPERTIES]
        self.parent_artifacts = self._get_parent_artifacts()

    def _get_parent_artifacts(self):
        artifacts = {}
        parent_artif = self.parent_type
        if parent_artif:
            while parent_artif != 'tosca.artifacts.Root':
                artifacts[parent_artif] = self.TOSCA_DEF[parent_artif]
                parent_artif = artifacts[parent_artif]['derived_from']
        return artifacts

    @property
    def parent_type(self):
        '''Return an artifact this artifact is derived from.'''
        return self.derived_from(self.defs)

    def get_artifact(self, name):
        '''Return the definition of an artifact field by name.'''
        if name in self.defs:
            return self.defs[name]
