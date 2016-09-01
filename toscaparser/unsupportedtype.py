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
from toscaparser.common.exception import UnsupportedTypeError
from toscaparser.utils.gettextutils import _

log = logging.getLogger('tosca')


class UnsupportedType(object):

    """Note: TOSCA spec version related

    The tosca.nodes.Storage.ObjectStorage and tosca.nodes.Storage.BlockStorage
    used here as un_supported_types are part of the name changes in TOSCA spec
    version 1.1. The original name as specified in version 1.0 are,
    tosca.nodes.BlockStorage and tosca.nodes.ObjectStorage which are supported
    by the tosca-parser. Since there are little overlapping in version support
    currently in the tosca-parser, the names tosca.nodes.Storage.ObjectStorage
    and tosca.nodes.Storage.BlockStorage are used here to demonstrate the usage
    of un_supported_types. As tosca-parser move to provide support for version
    1.1 and higher, they will be removed.
    """
    un_supported_types = ['tosca.test.invalidtype',
                          'tosca.nodes.Storage.ObjectStorage',
                          'tosca.nodes.Storage.BlockStorage']

    def __init__(self):
        pass

    @staticmethod
    def validate_type(entitytype):
        if entitytype in UnsupportedType.un_supported_types:
            ExceptionCollector.appendException(UnsupportedTypeError(
                                               what=_('%s')
                                               % entitytype))
            return True
        else:
            return False
