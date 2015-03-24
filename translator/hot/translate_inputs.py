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

from translator.hot.syntax.hot_parameter import HotParameter
from translator.toscalib.dataentity import DataEntity
from translator.toscalib.utils.gettextutils import _


INPUT_CONSTRAINTS = (CONSTRAINTS, DESCRIPTION, LENGTH, RANGE,
                     MIN, MAX, ALLOWED_VALUES, ALLOWED_PATTERN) = \
                    ('constraints', 'description', 'length', 'range',
                     'min', 'max', 'allowed_values', 'allowed_pattern')

TOSCA_CONSTRAINT_OPERATORS = (EQUAL, GREATER_THAN, GREATER_OR_EQUAL, LESS_THAN,
                              LESS_OR_EQUAL, IN_RANGE, VALID_VALUES, LENGTH,
                              MIN_LENGTH, MAX_LENGTH, PATTERN) = \
                             ('equal', 'greater_than', 'greater_or_equal',
                              'less_than', 'less_or_equal', 'in_range',
                              'valid_values', 'length', 'min_length',
                              'max_length', 'pattern')

TOSCA_TO_HOT_CONSTRAINTS_ATTRS = {'equal': 'allowed_values',
                                  'greater_than': 'range',
                                  'greater_or_equal': 'range',
                                  'less_than': 'range',
                                  'less_or_equal': 'range',
                                  'in_range': 'range',
                                  'valid_values': 'allowed_values',
                                  'length': 'length',
                                  'min_length': 'length',
                                  'max_length': 'length',
                                  'pattern': 'allowed_pattern'}

TOSCA_TO_HOT_INPUT_TYPES = {'string': 'string',
                            'integer': 'number',
                            'float': 'number',
                            'boolean': 'boolean',
                            'timestamp': 'string',
                            'null': 'string'}


class TranslateInputs():
    '''Translate TOSCA Inputs to Heat Parameters.'''

    def __init__(self, inputs, parsed_params):
        self.inputs = inputs
        self.parsed_params = parsed_params

    def translate(self):
        return self._translate_inputs()

    def _translate_inputs(self):
        hot_inputs = []
        hot_default = None
        for input in self.inputs:
            hot_input_type = TOSCA_TO_HOT_INPUT_TYPES[input.type]

            if input.name in self.parsed_params:
                DataEntity.validate_datatype(hot_input_type,
                                             self.parsed_params[input.name])
                hot_default = self.parsed_params[input.name]
            elif input.default is not None:
                hot_default = input.default
            else:
                raise Exception(_("Need to specify a value "
                                  "for input {0}").format(input.name))
            hot_constraints = []
            if input.constraints:
                for constraint in input.constraints:
                    constraint.validate(
                        int(hot_default) if hot_input_type == "number"
                        else hot_default)
                    hc, hvalue = self._translate_constraints(
                        constraint.constraint_key, constraint.constraint_value)
                    hot_constraints.append({hc: hvalue})

            hot_inputs.append(HotParameter(name=input.name,
                                           type=hot_input_type,
                                           description=input.description,
                                           default=hot_default,
                                           constraints=hot_constraints))
        return hot_inputs

    def _translate_constraints(self, name, value):
        hot_constraint = TOSCA_TO_HOT_CONSTRAINTS_ATTRS[name]

        # Offset used to support less_than and greater_than.
        # TODO(anyone):  when parser supports float, verify this works
        offset = 1

        if name == EQUAL:
            hot_value = [value]
        elif name == GREATER_THAN:
            hot_value = {"min": value + offset}
        elif name == GREATER_OR_EQUAL:
            hot_value = {"min": value}
        elif name == LESS_THAN:
            hot_value = {"max": value - offset}
        elif name == LESS_OR_EQUAL:
            hot_value = {"max": value}
        elif name == IN_RANGE:
            # value is list type here
            min_value = min(value)
            max_value = max(value)
            hot_value = {"min": min_value, "max": max_value}
        elif name == LENGTH:
            hot_value = {"min": value, "max": value}
        elif name == MIN_LENGTH:
            hot_value = {"min": value}
        elif name == MAX_LENGTH:
            hot_value = {"max": value}
        else:
            hot_value = value
        return hot_constraint, hot_value
