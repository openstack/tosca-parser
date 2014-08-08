# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
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

from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.elements.statefulentitytype import StatefulEntityType
from translator.toscalib.functions import get_function

SECTIONS = (LIFECYCLE, CONFIGURE) = \
           ('tosca.interfaces.node.Lifecycle',
            'tosca.interfaces.relationship.Configure')

INTERFACEVALUE = (IMPLEMENTATION, INPUT) = ('implementation', 'input')


class InterfacesDef(StatefulEntityType):
    '''TOSCA built-in interfaces type.'''

    def __init__(self, node_type, interfacetype,
                 node_template=None, name=None, value=None):
        self.ntype = node_type
        self.node_template = node_template
        if self.INTERFACE_PREFIX not in interfacetype:
            interfacetype = self.INTERFACE_PREFIX + interfacetype
        self.type = interfacetype
        self.name = name
        self.value = value
        self.implementation = None
        self.input = None
        self.defs = {}
        if node_type:
            self.defs = self.TOSCA_DEF[interfacetype]
        if value:
            if isinstance(self.value, dict):
                for i, j in self.value.items():
                    if i == 'implementation':
                        self.implementation = j
                    elif i == 'input':
                        self.input = self._create_input_functions(j)
                    else:
                        what = ('Interfaces of template %s' %
                                self.node_template.name)
                        raise UnknownFieldError(what=what, field=i)
            else:
                self.implementation = value

    def _create_input_functions(self, raw_input):
        """Creates input functions if necessary.
        :param raw_input: Raw input as dict.
        :return: Modified input dict containing template functions.
        :rtype: dict
        """
        return dict((k, get_function(self.node_template, v))
                    for (k, v) in raw_input.items())

    @property
    def lifecycle_ops(self):
        if self.defs:
            if self.type == LIFECYCLE:
                return self._ops()

    @property
    def configure_ops(self):
        if self.defs:
            if self.type == CONFIGURE:
                return self._ops()

    def _ops(self):
        ops = []
        for name in list(self.defs.keys()):
            ops.append(name)
        return ops
