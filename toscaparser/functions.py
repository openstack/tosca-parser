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
import six

from toscaparser.common.exception import UnknownInputError
from toscaparser.dataentity import DataEntity
from toscaparser.utils.gettextutils import _


GET_PROPERTY = 'get_property'
GET_ATTRIBUTE = 'get_attribute'
GET_INPUT = 'get_input'

SELF = 'SELF'
HOST = 'HOST'

HOSTED_ON = 'tosca.relationships.HostedOn'


@six.add_metaclass(abc.ABCMeta)
class Function(object):
    """An abstract type for representing a Tosca template function."""

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
    """Get a property value declared within the input of the service template.

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
        if self.tosca_tpl.parsed_params and \
           self.input_name in self.tosca_tpl.parsed_params:
            return DataEntity.validate_datatype(
                self.tosca_tpl.tpl['inputs'][self.input_name]['type'],
                self.tosca_tpl.parsed_params[self.input_name])

        input = [input_def for input_def in self.tosca_tpl.inputs
                 if self.input_name == input_def.name][0]
        return input.default

    @property
    def input_name(self):
        return self.args[0]


class GetAttribute(Function):
    """Get an attribute value of an entity defined in the service template

    Node template attributes values are set in runtime and therefore its the
    responsibility of the Tosca engine to implement the evaluation of
    get_attribute functions.

    Arguments:

    * Node template name | HOST.
    * Attribute name.

    If the HOST keyword is passed as the node template name argument the
    function will search each node template along the HostedOn relationship
    chain until a node which contains the attribute is found.

    Examples:

    * { get_attribute: [ server, private_address ] }
    * { get_attribute: [ HOST, private_address ] }
    """

    def validate(self):
        if len(self.args) != 2:
            raise ValueError(_(
                'Illegal arguments for {0} function. Expected arguments: '
                'node-template-name, attribute-name').format(GET_ATTRIBUTE))
        self._find_node_template_containing_attribute()

    def result(self):
        return self.args

    def get_referenced_node_template(self):
        """Gets the NodeTemplate instance the get_attribute function refers to.

        If HOST keyword was used as the node template argument, the node
        template which contains the attribute along the HostedOn relationship
        chain will be returned.
        """
        return self._find_node_template_containing_attribute()

    def _find_node_template_containing_attribute(self):
        if self.node_template_name == HOST:
            # Currently this is the only way to tell whether the function
            # is used within the outputs section of the TOSCA template.
            if isinstance(self.context, list):
                raise ValueError(_(
                    "get_attribute HOST keyword is not allowed within the "
                    "outputs section of the TOSCA template"))
            node_tpl = self._find_host_containing_attribute()
            if not node_tpl:
                raise ValueError(_(
                    "get_attribute HOST keyword is used in '{0}' node "
                    "template but {1} was not found "
                    "in relationship chain").format(self.context.name,
                                                    HOSTED_ON))
        else:
            node_tpl = self._find_node_template(self.args[0])
        if not self._attribute_exists_in_type(node_tpl.type_definition):
            raise KeyError(_(
                "Attribute '{0}' not found in node template: {1}.").format(
                    self.attribute_name, node_tpl.name))
        return node_tpl

    def _attribute_exists_in_type(self, type_definition):
        attrs_def = type_definition.get_attributes_def()
        found = [attrs_def[self.attribute_name]] \
            if self.attribute_name in attrs_def else []
        return len(found) == 1

    def _find_host_containing_attribute(self, node_template_name=SELF):
        node_template = self._find_node_template(node_template_name)
        from toscaparser.elements.entity_type import EntityType
        hosted_on_rel = EntityType.TOSCA_DEF[HOSTED_ON]
        for r in node_template.requirements:
            for requirement, target_name in r.items():
                target_node = self._find_node_template(target_name)
                target_type = target_node.type_definition
                for capability in target_type.get_capabilities_objects():
                    if capability.type in hosted_on_rel['valid_target_types']:
                        if self._attribute_exists_in_type(target_type):
                            return target_node
                        return self._find_host_containing_attribute(
                            target_name)
        return None

    def _find_node_template(self, node_template_name):
        name = self.context.name if node_template_name == SELF else \
            node_template_name
        for node_template in self.tosca_tpl.nodetemplates:
            if node_template.name == name:
                return node_template
        raise KeyError(_(
            'No such node template: {0}.').format(node_template_name))

    @property
    def node_template_name(self):
        return self.args[0]

    @property
    def attribute_name(self):
        return self.args[1]


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
        caps = node_template.get_capabilities()
        if caps and capability_name in caps.keys():
            cap = caps[capability_name]
            property = None
            props = cap.get_properties()
            if props and property_name in props.keys():
                property = props[property_name].value
            if not property:
                raise KeyError(_(
                    "Property '{0}' not found in capability '{1}' of node"
                    " template '{2}' referenced from node template"
                    " '{3}'.").format(property_name,
                                      capability_name,
                                      node_template.name,
                                      self.context.name))
            return property
        msg = _("Requirement/Capability '{0}' referenced from '{1}' node "
                "template not found in '{2}' node template.").format(
                    capability_name,
                    self.context.name,
                    node_template.name)
        raise KeyError(msg)

    def _find_property(self, property_name):
        node_tpl = self._find_node_template(self.args[0])
        props = node_tpl.get_properties()
        found = [props[property_name]] if property_name in props else []
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
            return property_value.result()
        return get_function(self.tosca_tpl,
                            self.context,
                            property_value)

    @property
    def node_template_name(self):
        return self.args[0]

    @property
    def property_name(self):
        if len(self.args) > 2:
            return self.args[2]
        return self.args[1]

    @property
    def req_or_cap(self):
        if len(self.args) > 2:
            return self.args[1]
        return None


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
