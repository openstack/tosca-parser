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

from translator.toscalib.common.exception import UnknownInputError
from translator.toscalib.utils.gettextutils import _


GET_PROPERTY = 'get_property'
GET_ATTRIBUTE = 'get_attribute'
GET_INPUT = 'get_input'

SELF = 'SELF'


class Function(object):
    """An abstract type for representing a Tosca template function."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, tosca_tpl, context, name, args):
        self.tosca_tpl = tosca_tpl
        self.context = context
        self.name = name
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

    @abc.abstractmethod
    def validate(self):
        """Validates function arguments."""
        pass


class GetInput(Function):
    """Get a property value declared within the inputs section of the service
    template.

    Arguments:

    * Input name.

    Example:

    * get_input: port
    """

    def validate(self):
        if len(self.args) != 1:
            raise ValueError(_(
                'Expected one argument for get_input function but received: '
                '{0}.').format(self.args))
        inputs = [input.name for input in self.tosca_tpl.inputs]
        if self.args[0] not in inputs:
            raise UnknownInputError(input_name=self.args[0])

    def result(self):
        return self

    @property
    def input_name(self):
        return self.args[0]


class GetAttribute(Function):

    def validate(self):
        pass

    def result(self):
        pass


class GetProperty(Function):
    """Get a property value of an entity defined in the same service template.

    Arguments:

    * Node template name.
    * Requirement or capability name (optional).
    * Property name.

    If requirement or capability name is specified, the behavior is as follows:
    The req or cap name is first looked up in the specified node template's
    requirements.
    If found, it would search for a matching capability
    of an other node template and get its property as specified in function
    arguments.
    Otherwise, the req or cap name would be looked up in the specified
    node template's capabilities and if found, it would return  the property of
    the capability as specified in function arguments.

    Examples:

    * { get_property: [ mysql_server, port ] }
    * { get_property: [ SELF, db_port ] }
    * { get_property: [ SELF, database_endpoint, port ] }
    """

    def validate(self):
        if len(self.args) < 2 or len(self.args) > 3:
            raise ValueError(_(
                'Expected arguments: [node-template-name, req-or-cap '
                '(optional), property name.'))
        if len(self.args) == 2:
            prop = self._find_property(self.args[1]).value
            if not isinstance(prop, Function):
                get_function(self.tosca_tpl, self.context, prop)
        elif len(self.args) == 3:
            get_function(self.tosca_tpl,
                         self.context,
                         self._find_req_or_cap_property(self.args[1],
                                                        self.args[2]))
        else:
            raise NotImplementedError(_(
                'Nested properties are not supported.'))

    def _find_req_or_cap_property(self, req_or_cap, property_name):
        node_tpl = self._find_node_template(self.args[0])
        # Find property in node template's requirements
        for r in node_tpl.requirements:
            for req, node_name in r.items():
                if req == req_or_cap:
                    node_template = self._find_node_template(node_name)
                    return self._get_capability_property(
                        node_template,
                        req,
                        property_name)
        # If requirement was not found, look in node template's capabilities
        return self._get_capability_property(node_tpl,
                                             req_or_cap,
                                             property_name)

    def _get_capability_property(self,
                                 node_template,
                                 capability_name,
                                 property_name):
        """Gets a node template capability property."""
        for cap in node_template.capabilities:
            if cap.name == capability_name:
                if property_name not in cap.properties:
                    raise KeyError(_(
                        "Property '{0}' not found in capability '{1}' of node "
                        "template '{2}' referenced from node template "
                        "'{3}'.").format(property_name,
                                         capability_name,
                                         node_template.name,
                                         self.context.name))
                return cap.properties[property_name]
        msg = _("Requirement/Capability '{0}' referenced from '{1}' node "
                "template not found in '{2}' node template.").format(
                    capability_name,
                    self.context.name,
                    node_template.name)
        raise KeyError(msg)

    def _find_property(self, property_name):
        node_tpl = self._find_node_template(self.args[0])
        found = [
            prop for prop in node_tpl.properties
            if prop.name == property_name]
        if len(found) == 0:
            raise KeyError(_(
                "Property: '{0}' not found in node template: {1}.").format(
                    property_name, node_tpl.name))
        return found[0]

    def _find_node_template(self, node_template_name):
        if node_template_name == SELF:
            return self.context
        for node_template in self.tosca_tpl.nodetemplates:
            if node_template.name == node_template_name:
                return node_template
        raise KeyError(_(
            'No such node template: {0}.').format(node_template_name))

    def result(self):
        if len(self.args) == 3:
            property_value = self._find_req_or_cap_property(self.args[1],
                                                            self.args[2])
        else:
            property_value = self._find_property(self.args[1]).value
        if isinstance(property_value, Function):
            return property_value
        return get_function(self.tosca_tpl,
                            self.context,
                            property_value)


function_mappings = {
    GET_PROPERTY: GetProperty,
    GET_INPUT: GetInput,
    GET_ATTRIBUTE: GetAttribute
}


def is_function(function):
    """Returns True if the provided function is a Tosca intrinsic function.

    Examples:

    * "{ get_property: { SELF, port } }"
    * "{ get_input: db_name }"
    * Function instance

    :param function: Function as string or a Function instance.
    :return: True if function is a Tosca intrinsic function, otherwise False.
    """
    if isinstance(function, dict) and len(function) == 1:
        func_name = list(function.keys())[0]
        return func_name in function_mappings
    return isinstance(function, Function)


def get_function(tosca_tpl, node_template, raw_function):
    """Gets a Function instance representing the provided template function.

    If the format provided raw_function format is not relevant for template
    functions or if the function name doesn't exist in function mapping the
    method returns the provided raw_function.

    :param tosca_tpl: The tosca template.
    :param node_template: The node template the function is specified for.
    :param raw_function: The raw function as dict.
    :return: Template function as Function instance or the raw_function if
     parsing was unsuccessful.
    """
    if is_function(raw_function):
        func_name = list(raw_function.keys())[0]
        if func_name in function_mappings:
            func = function_mappings[func_name]
            func_args = list(raw_function.values())[0]
            if not isinstance(func_args, list):
                func_args = [func_args]
            return func(tosca_tpl, node_template, func_name, func_args)
    return raw_function
