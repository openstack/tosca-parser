#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import collections
import importlib
import logging
import os

from stevedore import extension

from toscaparser.common.exception import ToscaExtAttributeError
from toscaparser.common.exception import ToscaExtImportError

log = logging.getLogger("tosca.model")

REQUIRED_ATTRIBUTES = ['VERSION', 'DEFS_FILE']


class ExtTools(object):
    def __init__(self):
        self.EXTENSION_INFO = self._load_extensions()

    def _load_extensions(self):
        '''Dynamically load all the extensions .'''
        extensions = collections.OrderedDict()

        extns = extension.ExtensionManager(namespace='toscaparser.extensions',
                                           invoke_on_load=True).extensions

        for e in extns:
            try:
                extinfo = importlib.import_module(e.plugin.__module__)
                base_path = os.path.dirname(extinfo.__file__)
                version = e.plugin().VERSION
                defs_file = base_path + '/' + e.plugin().DEFS_FILE

                # Sections is an optional attribute
                sections = getattr(e.plugin(), 'SECTIONS', ())

                extensions[version] = {'sections': sections,
                                       'defs_file': defs_file}
            except ImportError:
                raise ToscaExtImportError(ext_name=e.name)
            except AttributeError:
                attrs = ', '.join(REQUIRED_ATTRIBUTES)
                raise ToscaExtAttributeError(ext_name=e.name, attrs=attrs)

        return extensions

    def get_versions(self):
        return sorted(self.EXTENSION_INFO.keys())

    def get_sections(self):
        sections = {}
        for version in self.EXTENSION_INFO.keys():
            sections[version] = self.EXTENSION_INFO[version]['sections']

        return sections

    def get_defs_file(self, version):
        versiondata = self.EXTENSION_INFO.get(version)

        if versiondata:
            return versiondata.get('defs_file')
        else:
            return None
