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

import numbers
from translator.toscalib.utils.gettextutils import _


class Constraint(object):
    CONSTRAINTS = (EQUAL, GREATER_THAN,
                   GREATER_OR_EQUAL, LESS_THAN, LESS_OR_EQUAL, IN_RANGE,
                   VALID_VALUES, LENGTH, MIN_LENGHT, MAX_LENGTH, PATTERN) = \
                  ('equal', 'greater_than', 'greater_or_equal', 'less_than',
                   'less_or_equal', 'in_range', 'valid_values', 'length',
                   'min_length', 'max_length', 'pattern')

    def __init__(self, propertyname, value, constraint):
        self.propertyname = propertyname
        self.value = value
        self.constraint = constraint

    def validate(self):
        for key, value in self.constraint.items():
            if key == self.GREATER_OR_EQUAL:
                self.validate_greater_than(value)

    def validate_equal(self):
        pass

    def validate_greater_than(self, value):
        if self.value < value:
            raise ValueError(_("%(prop)s value requires to be "
                               "greater than %(val)s")
                             % {'prop': self.propertyname, 'val': value})

    def validate_greater_or_equal(self):
        pass

    def validate_less_than(self):
        pass

    def validate_less_or_equal(self):
        pass

    def validate_in_range(self):
        pass

    def validate_valid_values(self):
        pass

    def validate_length(self):
        pass

    def validate_min_length(self):
        pass

    def validate_max_length(self):
        pass

    def validate_pattern(self):
        pass

    @staticmethod
    def validate_integer(value):
        if not isinstance(value, (int, long)):
            raise TypeError(_('Value is not an integer for %s') % value)
        return Constraint.validate_number(value)

    @staticmethod
    def validate_number(value):
        return Constraint.str_to_num(value)

    @staticmethod
    def validate_string(value):
        if not isinstance(value, basestring):
            raise ValueError(_('Value must be a string %s') % value)
        return value

    @staticmethod
    def validate_list(self, value):
        pass

    @staticmethod
    def str_to_num(value):
        '''Convert a string representation of a number into a numeric type.'''
        if isinstance(value, numbers.Number):
            return value
        try:
            return int(value)
        except ValueError:
            return float(value)
