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
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import TypeMismatchError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.elements.constraints import Schema
from toscaparser.elements.datatype import DataType
from toscaparser.elements.portspectype import PortSpec
from toscaparser.elements.scalarunit import ScalarUnit_Frequency
from toscaparser.elements.scalarunit import ScalarUnit_Size
from toscaparser.elements.scalarunit import ScalarUnit_Time
from toscaparser.utils.gettextutils import _
from toscaparser.utils import validateutils


class DataEntity(object):
    '''A complex data value entity.'''

    def __init__(self, datatypename, value_dict, custom_def=None,
                 prop_name=None):
        """
        Initialize the data structure.

        Args:
            self: (todo): write your description
            datatypename: (str): write your description
            value_dict: (dict): write your description
            custom_def: (todo): write your description
            prop_name: (str): write your description
        """
        self.custom_def = custom_def
        self.datatype = DataType(datatypename, custom_def)
        self.schema = self.datatype.get_all_properties()
        self.value = value_dict
        self.property_name = prop_name

    def validate(self):
        '''Validate the value by the definition of the datatype.'''

        # A datatype can not have both 'type' and 'properties' definitions.
        # If the datatype has 'type' definition
        if self.datatype.value_type:
            self.value = DataEntity.validate_datatype(self.datatype.value_type,
                                                      self.value,
                                                      None,
                                                      self.custom_def)
            schema = Schema(self.property_name, self.datatype.defs)
            for constraint in schema.constraints:
                constraint.validate(self.value)
        # If the datatype has 'properties' definition
        else:
            if not isinstance(self.value, dict):
                ExceptionCollector.appendException(
                    TypeMismatchError(what=self.value,
                                      type=self.datatype.type))
            allowed_props = []
            required_props = []
            default_props = {}
            if self.schema:
                allowed_props = self.schema.keys()
                for name, prop_def in self.schema.items():
                    if prop_def.required:
                        required_props.append(name)
                    if prop_def.default:
                        default_props[name] = prop_def.default

            # check allowed field
            for value_key in list(self.value.keys()):
                if value_key not in allowed_props:
                    ExceptionCollector.appendException(
                        UnknownFieldError(what=(_('Data value of type "%s"')
                                                % self.datatype.type),
                                          field=value_key))

            # check default field
            for def_key, def_value in list(default_props.items()):
                if def_key not in list(self.value.keys()):
                    self.value[def_key] = def_value

            # check missing field
            missingprop = []
            for req_key in required_props:
                if req_key not in list(self.value.keys()):
                    missingprop.append(req_key)
            if missingprop:
                ExceptionCollector.appendException(
                    MissingRequiredFieldError(
                        what=(_('Data value of type "%s"')
                              % self.datatype.type), required=missingprop))

            # check every field
            for name, value in list(self.value.items()):
                schema_name = self._find_schema(name)
                if not schema_name:
                    continue
                prop_schema = Schema(name, schema_name)
                # check if field value meets type defined
                DataEntity.validate_datatype(prop_schema.type, value,
                                             prop_schema.entry_schema,
                                             self.custom_def)
                # check if field value meets constraints defined
                if prop_schema.constraints:
                    for constraint in prop_schema.constraints:
                        if isinstance(value, list):
                            for val in value:
                                constraint.validate(val)
                        else:
                            constraint.validate(value)

        return self.value

    def _find_schema(self, name):
        """
        Return the schema with the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        if self.schema and name in self.schema.keys():
            return self.schema[name].schema

    @staticmethod
    def validate_datatype(type, value, entry_schema=None, custom_def=None,
                          prop_name=None):
        '''Validate value with given type.

        If type is list or map, validate its entry by entry_schema(if defined)
        If type is a user-defined complex datatype, custom_def is required.
        '''
        from toscaparser.functions import is_function
        if is_function(value):
            return value
        if type == Schema.STRING:
            return validateutils.validate_string(value)
        elif type == Schema.INTEGER:
            return validateutils.validate_integer(value)
        elif type == Schema.FLOAT:
            return validateutils.validate_float(value)
        elif type == Schema.NUMBER:
            return validateutils.validate_numeric(value)
        elif type == Schema.BOOLEAN:
            return validateutils.validate_boolean(value)
        elif type == Schema.RANGE:
            return validateutils.validate_range(value)
        elif type == Schema.TIMESTAMP:
            validateutils.validate_timestamp(value)
            return value
        elif type == Schema.LIST:
            validateutils.validate_list(value)
            if entry_schema:
                DataEntity.validate_entry(value, entry_schema, custom_def)
            return value
        elif type == Schema.SCALAR_UNIT_SIZE:
            return ScalarUnit_Size(value).validate_scalar_unit()
        elif type == Schema.SCALAR_UNIT_FREQUENCY:
            return ScalarUnit_Frequency(value).validate_scalar_unit()
        elif type == Schema.SCALAR_UNIT_TIME:
            return ScalarUnit_Time(value).validate_scalar_unit()
        elif type == Schema.VERSION:
            return validateutils.TOSCAVersionProperty(value).get_version()
        elif type == Schema.MAP:
            validateutils.validate_map(value)
            if entry_schema:
                DataEntity.validate_entry(value, entry_schema, custom_def)
            return value
        elif type == Schema.PORTSPEC:
            # TODO(TBD) bug 1567063, validate source & target as PortDef type
            # as complex types not just as integers
            PortSpec.validate_additional_req(value, prop_name, custom_def)
        else:
            data = DataEntity(type, value, custom_def)
            return data.validate()

    @staticmethod
    def validate_entry(value, entry_schema, custom_def=None):
        '''Validate entries for map and list.'''
        schema = Schema(None, entry_schema)
        valuelist = value
        if isinstance(value, dict):
            valuelist = list(value.values())
        for v in valuelist:
            DataEntity.validate_datatype(schema.type, v, schema.entry_schema,
                                         custom_def)
            if schema.constraints:
                for constraint in schema.constraints:
                    constraint.validate(v)
        return value
