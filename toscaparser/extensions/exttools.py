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

import importlib
import logging
import os

from toscaparser.common.exception import ToscaExtAttributeError
from toscaparser.common.exception import ToscaExtImportError

log = logging.getLogger("tosca.model")

REQUIRED_ATTRIBUTES = ['VERSION', 'DEFS_FILE']


class ExtTools(object):
    def __init__(self):
        self.EXTENSION_INFO = self._load_extensions()

    def _load_extensions(self):
        '''Dynamically load all the extensions .'''
        extensions = {}

        # Use the absolute path of the class path
        abs_path = os.path.dirname(os.path.abspath(__file__))

        extdirs = [e for e in os.listdir(abs_path) if
                   not e.startswith('tests') and
                   os.path.isdir(os.path.join(abs_path, e))]

        for e in extdirs:
            log.info(e)
            extpath = abs_path + '/' + e
            # Grab all the extension files in the given path
            ext_files = [f for f in os.listdir(extpath) if f.endswith('.py')
                         and not f.startswith('__init__')]

            # For each module, pick out the target translation class
            for f in ext_files:
                log.info(f)
                ext_name = 'toscaparser/extensions/' + e + '/' + f.strip('.py')
                ext_name = ext_name.replace('/', '.')
                try:
                    extinfo = importlib.import_module(ext_name)
                    version = getattr(extinfo, 'VERSION')
                    defs_file = extpath + '/' + getattr(extinfo, 'DEFS_FILE')

                    # Sections is an optional attribute
                    sections = getattr(extinfo, 'SECTIONS', ())

                    extensions[version] = {'sections': sections,
                                           'defs_file': defs_file}
                except ImportError:
                    raise ToscaExtImportError(ext_name=ext_name)
                except AttributeError:
                    attrs = ', '.join(REQUIRED_ATTRIBUTES)
                    raise ToscaExtAttributeError(ext_name=ext_name,
                                                 attrs=attrs)

        return extensions

    def get_versions(self):
        return self.EXTENSION_INFO.keys()

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
