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
import toscaparser.elements.interfaces

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import UnknownInputError
from toscaparser.dataentity import DataEntity
from toscaparser.elements.constraints import Schema
from toscaparser.elements.datatype import DataType
from toscaparser.elements.entity_type import EntityType
from toscaparser.elements.relationshiptype import RelationshipType
from toscaparser.elements.statefulentitytype import StatefulEntityType
from toscaparser.utils.gettextutils import _


GET_PROPERTY = 'get_property'
GET_ATTRIBUTE = 'get_attribute'
GET_INPUT = 'get_input'
GET_OPERATION_OUTPUT = 'get_operation_output'
CONCAT = 'concat'
TOKEN = 'token'

SELF = 'SELF'
HOST = 'HOST'
TARGET = 'TARGET'
SOURCE = 'SOURCE'

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
            ExceptionCollector.appendException(
                ValueError(_(
                    'Expected one argument for function "get_input" but '
                    'received "%s".') % self.args))
        inputs = [input.name for input in self.tosca_tpl.inputs]
        if self.args[0] not in inputs:
            ExceptionCollector.appendException(
                UnknownInputError(input_name=self.args[0]))

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
    * { get_attribute: [ HOST, private_address, 0 ] }
    * { get_attribute: [ HOST, private_address, 0, some_prop] }
    """

    def validate(self):
        if len(self.args) < 2:
            ExceptionCollector.appendException(
                ValueError(_('Illegal arguments for function "{0}". Expected '
                             'arguments: "node-template-name", "req-or-cap"'
                             '(optional), "property name"'
                             ).format(GET_ATTRIBUTE)))
            return
        elif len(self.args) == 2:
            self._find_node_template_containing_attribute()
        else:
            node_tpl = self._find_node_template(self.args[0])
            if node_tpl is None:
                return
            index = 2
            attrs = node_tpl.type_definition.get_attributes_def()
            found = [attrs[self.args[1]]] if self.args[1] in attrs else []
            if found:
                attr = found[0]
            else:
                index = 3
                # then check the req or caps
                attr = self._find_req_or_cap_attribute(self.args[1],
                                                       self.args[2])
                if not attr:
                    return

            value_type = attr.schema['type']
            if len(self.args) > index:
                for elem in self.args[index:]:
                    if value_type == "list":
                        if not isinstance(elem, int):
                            ExceptionCollector.appendException(
                                ValueError(_('Illegal arguments for function'
                                             ' "{0}". "{1}" Expected positive'
                                             ' integer argument'
                                             ).format(GET_ATTRIBUTE, elem)))
                        value_type = attr.schema['entry_schema']['type']
                    elif value_type == "map":
                        value_type = attr.schema['entry_schema']['type']
                    elif value_type in Schema.PROPERTY_TYPES:
                        ExceptionCollector.appendException(
                            ValueError(_('Illegal arguments for function'
                                         ' "{0}". Unexpected attribute/'
                                         'index value "{1}"'
                                         ).format(GET_ATTRIBUTE, elem)))
                        return
                    else:  # It is a complex type
                        data_type = DataType(value_type)
                        props = data_type.get_all_properties()
                        found = [props[elem]] if elem in props else []
                        if found:
                            prop = found[0]
                            value_type = prop.schema['type']
                        else:
                            ExceptionCollector.appendException(
                                KeyError(_('Illegal arguments for function'
                                           ' "{0}". Attribute name "{1}" not'
                                           ' found in "{2}"'
                                           ).format(GET_ATTRIBUTE,
                                                    elem,
                                                    value_type)))

    def result(self):
        return self

    def get_referenced_node_template(self):
        """Gets the NodeTemplate instance the get_attribute function refers to.

        If HOST keyword was used as the node template argument, the node
        template which contains the attribute along the HostedOn relationship
        chain will be returned.
        """
        return self._find_node_template_containing_attribute()

    # Attributes can be explicitly created as part of the type definition
    # or a property name can be implicitly used as an attribute name
    def _find_node_template_containing_attribute(self):
        node_tpl = self._find_node_template(self.args[0])
        if node_tpl and \
                not self._attribute_exists_in_type(node_tpl.type_definition) \
                and self.attribute_name not in node_tpl.get_properties():
            ExceptionCollector.appendException(
                KeyError(_('Attribute "%(att)s" was not found in node '
                           'template "%(ntpl)s".') %
                         {'att': self.attribute_name,
                          'ntpl': node_tpl.name}))
        return node_tpl

    def _attribute_exists_in_type(self, type_definition):
        attrs_def = type_definition.get_attributes_def()
        found = [attrs_def[self.attribute_name]] \
            if self.attribute_name in attrs_def else []
        return len(found) == 1

    def _find_host_containing_attribute(self, node_template_name=SELF):
        node_template = self._find_node_template(node_template_name)
        if node_template:
            hosted_on_rel = EntityType.TOSCA_DEF[HOSTED_ON]
            for r in node_template.requirements:
                for requirement, target_name in r.items():
                    target_node = self._find_node_template(target_name)
                    target_type = target_node.type_definition
                    for capability in target_type.get_capabilities_objects():
                        if capability.inherits_from(
                                hosted_on_rel['valid_target_types']):
                            if self._attribute_exists_in_type(target_type):
                                return target_node
                            return self._find_host_containing_attribute(
                                target_name)

    def _find_node_template(self, node_template_name):
        if node_template_name == HOST:
            # Currently this is the only way to tell whether the function
            # is used within the outputs section of the TOSCA template.
            if isinstance(self.context, list):
                ExceptionCollector.appendException(
                    ValueError(_(
                        '"get_attribute: [ HOST, ... ]" is not allowed in '
                        '"outputs" section of the TOSCA template.')))
                return
            node_tpl = self._find_host_containing_attribute()
            if not node_tpl:
                ExceptionCollector.appendException(
                    ValueError(_(
                        '"get_attribute: [ HOST, ... ]" was used in node '
                        'template "{0}" but "{1}" was not found in '
                        'the relationship chain.').format(self.context.name,
                                                          HOSTED_ON)))
                return
            return node_tpl
        if node_template_name == TARGET:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"TARGET" keyword can only be used in context'
                               ' to "Relationships" target node')))
                return
            return self.context.target
        if node_template_name == SOURCE:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"SOURCE" keyword can only be used in context'
                               ' to "Relationships" source node')))
                return
            return self.context.source
        name = self.context.name \
            if node_template_name == SELF and \
            not isinstance(self.context, list) \
            else node_template_name
        for node_template in self.tosca_tpl.nodetemplates:
            if node_template.name == name:
                return node_template
        ExceptionCollector.appendException(
            KeyError(_(
                'Node template "{0}" was not found.'
                ).format(node_template_name)))

    def _find_req_or_cap_attribute(self, req_or_cap, attr_name):
        node_tpl = self._find_node_template(self.args[0])
        # Find attribute in node template's requirements
        for r in node_tpl.requirements:
            for req, node_name in r.items():
                if req == req_or_cap:
                    node_template = self._find_node_template(node_name)
                    return self._get_capability_attribute(
                        node_template,
                        req,
                        attr_name)
        # If requirement was not found, look in node template's capabilities
        return self._get_capability_attribute(node_tpl,
                                              req_or_cap,
                                              attr_name)

    def _get_capability_attribute(self,
                                  node_template,
                                  capability_name,
                                  attr_name):
        """Gets a node template capability attribute."""
        caps = node_template.get_capabilities()
        if caps and capability_name in caps.keys():
            cap = caps[capability_name]
            attribute = None
            attrs = cap.definition.get_attributes_def()
            if attrs and attr_name in attrs.keys():
                attribute = attrs[attr_name]
            if not attribute:
                ExceptionCollector.appendException(
                    KeyError(_('Attribute "%(attr)s" was not found in '
                               'capability "%(cap)s" of node template '
                               '"%(ntpl1)s" referenced from node template '
                               '"%(ntpl2)s".') % {'attr': attr_name,
                                                  'cap': capability_name,
                                                  'ntpl1': node_template.name,
                                                  'ntpl2': self.context.name}))
            return attribute
        msg = _('Requirement/Capability "{0}" referenced from node template '
                '"{1}" was not found in node template "{2}".').format(
                    capability_name,
                    self.context.name,
                    node_template.name)
        ExceptionCollector.appendException(KeyError(msg))

    @property
    def node_template_name(self):
        return self.args[0]

    @property
    def attribute_name(self):
        return self.args[1]


class GetProperty(Function):
    """Get a property value of an entity defined in the same service template.

    Arguments:

    * Node template name | SELF | HOST | SOURCE | TARGET.
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
    * { get_property: [ SELF, database_endpoint, port, 1 ] }
    """

    def validate(self):
        if len(self.args) < 2:
            ExceptionCollector.appendException(
                ValueError(_(
                    'Expected arguments: "node-template-name", "req-or-cap" '
                    '(optional), "property name".')))
            return
        if len(self.args) == 2:
            found_prop = self._find_property(self.args[1])
            if not found_prop:
                return
            prop = found_prop.value
            if not isinstance(prop, Function):
                get_function(self.tosca_tpl, self.context, prop)
        elif len(self.args) >= 3:
            # do not use _find_property to avoid raise KeyError
            # if the prop is not found
            # First check if there is property with this name
            node_tpl = self._find_node_template(self.args[0])
            props = node_tpl.get_properties() if node_tpl else []
            index = 2
            found = [props[self.args[1]]] if self.args[1] in props else []
            if found:
                property_value = found[0].value
            else:
                index = 3
                # then check the req or caps
                property_value = self._find_req_or_cap_property(self.args[1],
                                                                self.args[2])
            if len(self.args) > index:
                for elem in self.args[index:]:
                    if isinstance(property_value, list):
                        int_elem = int(elem)
                        property_value = self._get_index_value(property_value,
                                                               int_elem)
                    else:
                        property_value = self._get_attribute_value(
                            property_value,
                            elem)

    def _find_req_or_cap_property(self, req_or_cap, property_name):
        node_tpl = self._find_node_template(self.args[0])
        if node_tpl is None:
            return None
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
                                 property_name,
                                 throw_errors=True):
        """Gets a node template capability property."""
        caps = node_template.get_capabilities()
        if caps and capability_name in caps.keys():
            cap = caps[capability_name]
            property = None
            props = cap.get_properties()
            if props and property_name in props.keys():
                property = props[property_name].value
            if property is None and throw_errors:
                ExceptionCollector.appendException(
                    KeyError(_('Property "%(prop)s" was not found in '
                               'capability "%(cap)s" of node template '
                               '"%(ntpl1)s" referenced from node template '
                               '"%(ntpl2)s".') % {'prop': property_name,
                                                  'cap': capability_name,
                                                  'ntpl1': node_template.name,
                                                  'ntpl2': self.context.name}))
            return property
        if throw_errors:
            msg = _('Requirement/Capability "{0}" referenced from '
                    'node template "{1}" was not found in node template'
                    ' "{2}".').format(capability_name,
                                      self.context.name,
                                      node_template.name)
            ExceptionCollector.appendException(KeyError(msg))
        else:
            return None

    def _find_property(self, property_name):
        node_tpl = self._find_node_template(self.args[0])
        if not node_tpl:
            return
        props = node_tpl.get_properties()
        found = [props[property_name]] if property_name in props else []
        if len(found) == 0:
            ExceptionCollector.appendException(
                KeyError(_('Property "%(prop)s" was not found in node '
                           'template "%(ntpl)s".') %
                         {'prop': property_name,
                          'ntpl': node_tpl.name}))
            return None
        return found[0]

    def _find_node_template(self, node_template_name):
        if node_template_name == SELF:
            return self.context
        # enable the HOST value in the function
        if node_template_name == HOST:
            node = self._find_host_containing_property()
            if node is None:
                ExceptionCollector.appendException(
                    KeyError(_(
                        "Property '{0}' not found in capability/requirement"
                        " '{1}' referenced from node template {2}").
                        format(self.args[2],
                               self.args[1],
                               self.context.name)))
                return None
            else:
                return node
        if node_template_name == TARGET:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"TARGET" keyword can only be used in context'
                               ' to "Relationships" target node')))
                return
            return self.context.target
        if node_template_name == SOURCE:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"SOURCE" keyword can only be used in context'
                               ' to "Relationships" source node')))
                return
            return self.context.source
        if not hasattr(self.tosca_tpl, 'nodetemplates'):
            return
        for node_template in self.tosca_tpl.nodetemplates:
            if node_template.name == node_template_name:
                return node_template
        ExceptionCollector.appendException(
            KeyError(_(
                'Node template "{0}" was not found.'
                ' referenced from node template {1}'
                ).format(node_template_name,
                         self.context.name)))

    def _get_index_value(self, value, index):
        if isinstance(value, list):
            if index < len(value):
                return value[index]
            else:
                ExceptionCollector.appendException(
                    KeyError(_(
                        "Property '{0}' found in capability '{1}'"
                        " referenced from node template {2}"
                        " must have an element with index {3}.").
                        format(self.args[2],
                               self.args[1],
                               self.context.name,
                               index)))
        else:
            ExceptionCollector.appendException(
                KeyError(_(
                    "Property '{0}' found in capability '{1}'"
                    " referenced from node template {2}"
                    " must be a list.").format(self.args[2],
                                               self.args[1],
                                               self.context.name)))

    def _get_attribute_value(self, value, attibute):
        if isinstance(value, dict):
            if attibute in value:
                return value[attibute]
            else:
                ExceptionCollector.appendException(
                    KeyError(_(
                        "Property '{0}' found in capability '{1}'"
                        " referenced from node template {2}"
                        " must have an attribute named {3}.").
                        format(self.args[2],
                               self.args[1],
                               self.context.name,
                               attibute)))
        else:
            ExceptionCollector.appendException(
                KeyError(_(
                    "Property '{0}' found in capability '{1}'"
                    " referenced from node template {2}"
                    " must be a dict.").format(self.args[2],
                                               self.args[1],
                                               self.context.name)))

    # Add this functions similar to get_attribute case
    def _find_host_containing_property(self, node_template_name=SELF):
        node_template = self._find_node_template(node_template_name)
        hosted_on_rel = EntityType.TOSCA_DEF[HOSTED_ON]
        for r in node_template.requirements:
            for requirement, target_name in r.items():
                target_node = self._find_node_template(target_name)
                target_type = target_node.type_definition
                for capability in target_type.get_capabilities_objects():
                    if capability.inherits_from(
                            hosted_on_rel['valid_target_types']):
                        if self._property_exists_in_type(target_type):
                            return target_node
                        # If requirement was not found, look in node
                        # template's capabilities
                        if (len(self.args) > 2 and
                                self._get_capability_property(target_node,
                                                              self.args[1],
                                                              self.args[2],
                                                              False)
                                is not None):
                            return target_node
                        return self._find_host_containing_property(
                            target_name)
        return None

    def _property_exists_in_type(self, type_definition):
        props_def = type_definition.get_properties_def()
        found = [props_def[self.args[1]]] \
            if self.args[1] in props_def else []
        return len(found) == 1

    def result(self):
        if len(self.args) >= 3:
            # First check if there is property with this name
            node_tpl = self._find_node_template(self.args[0])
            props = node_tpl.get_properties() if node_tpl else []
            index = 2
            found = [props[self.args[1]]] if self.args[1] in props else []
            if found:
                property_value = found[0].value
            else:
                index = 3
                # then check the req or caps
                property_value = self._find_req_or_cap_property(self.args[1],
                                                                self.args[2])
            if len(self.args) > index:
                for elem in self.args[index:]:
                    if isinstance(property_value, list):
                        int_elem = int(elem)
                        property_value = self._get_index_value(property_value,
                                                               int_elem)
                    else:
                        property_value = self._get_attribute_value(
                            property_value,
                            elem)
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


class GetOperationOutput(Function):
    def validate(self):
        if len(self.args) == 4:
            self._find_node_template(self.args[0])
            interface_name = self._find_interface_name(self.args[1])
            self._find_operation_name(interface_name, self.args[2])
        else:
            ExceptionCollector.appendException(
                ValueError(_('Illegal arguments for function "{0}". Expected '
                             'arguments: "template_name","interface_name",'
                             '"operation_name","output_variable_name"'
                             ).format(GET_OPERATION_OUTPUT)))
            return

    def _find_interface_name(self, interface_name):
        if interface_name in toscaparser.elements.interfaces.SECTIONS:
            return interface_name
        else:
            ExceptionCollector.appendException(
                ValueError(_('Enter a valid interface name'
                             ).format(GET_OPERATION_OUTPUT)))
            return

    def _find_operation_name(self, interface_name, operation_name):
        if(interface_name == 'Configure' or
           interface_name == 'tosca.interfaces.node.relationship.Configure'):
            if(operation_name in
               StatefulEntityType.
               interfaces_relationship_configure_operations):
                return operation_name
            else:
                ExceptionCollector.appendException(
                    ValueError(_('Enter an operation of Configure interface'
                                 ).format(GET_OPERATION_OUTPUT)))
                return
        elif(interface_name == 'Standard' or
             interface_name == 'tosca.interfaces.node.lifecycle.Standard'):
            if(operation_name in
               StatefulEntityType.interfaces_node_lifecycle_operations):
                return operation_name
            else:
                ExceptionCollector.appendException(
                    ValueError(_('Enter an operation of Standard interface'
                                 ).format(GET_OPERATION_OUTPUT)))
                return
        else:
            ExceptionCollector.appendException(
                ValueError(_('Enter a valid operation name'
                             ).format(GET_OPERATION_OUTPUT)))
            return

    def _find_node_template(self, node_template_name):
        if node_template_name == TARGET:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"TARGET" keyword can only be used in context'
                               ' to "Relationships" target node')))
                return
            return self.context.target
        if node_template_name == SOURCE:
            if not isinstance(self.context.type_definition, RelationshipType):
                ExceptionCollector.appendException(
                    KeyError(_('"SOURCE" keyword can only be used in context'
                               ' to "Relationships" source node')))
                return
            return self.context.source
        name = self.context.name \
            if node_template_name == SELF and \
            not isinstance(self.context, list) \
            else node_template_name
        for node_template in self.tosca_tpl.nodetemplates:
            if node_template.name == name:
                return node_template
        ExceptionCollector.appendException(
            KeyError(_(
                'Node template "{0}" was not found.'
                ).format(node_template_name)))

    def result(self):
        return self


class Concat(Function):
    """Validate the function and provide an instance of the function

    Concatenation of values are supposed to be produced at runtime and
    therefore its the responsibility of the TOSCA engine to implement the
    evaluation of Concat functions.

    Arguments:

    * List of strings that needs to be concatenated

    Example:

      [ 'http://',
        get_attribute: [ server, public_address ],
        ':' ,
        get_attribute: [ server, port ] ]
    """

    def validate(self):
        if len(self.args) < 1:
            ExceptionCollector.appendException(
                ValueError(_('Invalid arguments for function "{0}". Expected '
                             'at least one arguments.').format(CONCAT)))

    def result(self):
        return self


class Token(Function):
    """Validate the function and provide an instance of the function

    The token function is used within a TOSCA service template on a string to
    parse out (tokenize) substrings separated by one or more token characters
    within a larger string.


    Arguments:

    * The composite string that contains one or more substrings separated by
      token characters.
    * The string that contains one or more token characters that separate
      substrings within the composite string.
    * The integer indicates the index of the substring to return from the
      composite string.  Note that the first substring is denoted by using
      the '0' (zero) integer value.

    Example:

     [ get_attribute: [ my_server, data_endpoint, ip_address ], ':', 1 ]

    """

    def validate(self):
        if len(self.args) < 3:
            ExceptionCollector.appendException(
                ValueError(_('Invalid arguments for function "{0}". Expected '
                             'at least three arguments.').format(TOKEN)))
        else:
            if not isinstance(self.args[1], str) or len(self.args[1]) != 1:
                ExceptionCollector.appendException(
                    ValueError(_('Invalid arguments for function "{0}". '
                                 'Expected single char value as second '
                                 'argument.').format(TOKEN)))

            if not isinstance(self.args[2], int):
                ExceptionCollector.appendException(
                    ValueError(_('Invalid arguments for function "{0}". '
                                 'Expected integer value as third '
                                 'argument.').format(TOKEN)))

    def result(self):
        return self

function_mappings = {
    GET_PROPERTY: GetProperty,
    GET_INPUT: GetInput,
    GET_ATTRIBUTE: GetAttribute,
    GET_OPERATION_OUTPUT: GetOperationOutput,
    CONCAT: Concat,
    TOKEN: Token
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
        if isinstance(raw_function, dict):
            func_name = list(raw_function.keys())[0]
            if func_name in function_mappings:
                func = function_mappings[func_name]
                func_args = list(raw_function.values())[0]
                if not isinstance(func_args, list):
                    func_args = [func_args]
                return func(tosca_tpl, node_template, func_name, func_args)
    return raw_function
