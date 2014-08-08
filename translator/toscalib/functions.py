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


import abc


GET_PROPERTY = 'get_property'
GET_REF_PROPERTY = 'get_ref_property'


class Function(object):
    """An abstract type for representing a Tosca template function."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, node_template, func_name, args):
        self.node_template = node_template
        self.name = func_name
        self.args = args
        self.validate()

    @abc.abstractmethod
    def result(self):
        """Invokes the function and returns its result

        Some methods invocation may only be relevant on runtime (for example,
        getting runtime properties) and therefore its the responsibility of
        the orchestrator/translator to take care of such functions invocation.

        :return: Function invocation result.
        """
        return {self.name: self.args}

    def validate(self):
        """Validates function arguments."""


class GetRefProperty(Function):
    """Get a property via a reference expressed in the requirements section.

    Arguments:
        - Requirement name.
        - Capability name.
        - Property to get.

    Example:
        get_ref_property: [ database_endpoint, database_endpoint, port ]
    """

    def validate(self):
        if len(self.args) != 3:
            raise ValueError(
                'Expected arguments: requirement, capability, property')

    def result(self):
        requires = self.node_template.requirements
        name = None
        if requires:
            requirement = self.args[0]
            for r in requires:
                for cap, node in r.items():
                    if cap == requirement:
                        name = node
                        break
            if name:
                from translator.toscalib.nodetemplate import NodeTemplate
                tpl = NodeTemplate(
                    name, self.node_template.templates)
                caps = tpl.capabilities
                required_cap = self.args[1]
                required_property = self.args[2]
                for c in caps:
                    if c.name == required_cap:
                        return c.properties.get(required_property)


function_mappings = {
    GET_REF_PROPERTY: GetRefProperty
}


def get_function(node_template, raw_function):
    """Gets a Function instance representing the provided template function.

    If the format provided raw_function format is not relevant for template
    functions or if the function name doesn't exist in function mapping the
    method returns the provided raw_function.

    :param node_template: The node template the function is specified for.
    :param raw_function: The raw function as dict.
    :return: Template function as Function instance or the raw_function if
     parsing was unsuccessful.
    """
    if isinstance(raw_function, dict) and len(raw_function) == 1:
        func_name = list(raw_function.keys())[0]
        if func_name in function_mappings:
            func = function_mappings[func_name]
            func_args = list(raw_function.values())[0]
            return func(node_template, func_name, func_args)
    return raw_function
