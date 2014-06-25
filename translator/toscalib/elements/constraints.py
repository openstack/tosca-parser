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

import collections
import datetime
import numbers
import re

from translator.toscalib.utils.gettextutils import _


class ValidationError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class Constraint(object):
    '''Parent class for constraints for a Property or Input.'''

    CONSTRAINTS = (EQUAL, GREATER_THAN,
                   GREATER_OR_EQUAL, LESS_THAN, LESS_OR_EQUAL, IN_RANGE,
                   VALID_VALUES, LENGTH, MIN_LENGTH, MAX_LENGTH, PATTERN) = \
                  ('equal', 'greater_than', 'greater_or_equal', 'less_than',
                   'less_or_equal', 'in_range', 'valid_values', 'length',
                   'min_length', 'max_length', 'pattern')

    PROPERTY_TYPES = (
        INTEGER, STRING, BOOLEAN,
        FLOAT, TIMESTAMP
    ) = (
        'integer', 'string', 'boolean',
        'float', 'timestamp'
    )

    def __new__(cls, property_name, property_type, constraint):
        if cls is not Constraint:
            return super(Constraint, cls).__new__(cls)

        if(not isinstance(constraint, collections.Mapping) or
           len(constraint) != 1):
            raise ValidationError(_('Invalid constraint schema.'))

        for type in constraint.keys():
            ConstraintClass = get_constraint_class(type)
            if not ConstraintClass:
                raise ValidationError(_('Invalid constraint type "%s".') %
                                      type)

        return ConstraintClass(property_name, property_type, constraint)

    def __init__(self, property_name, property_type, constraint):
        self.property_name = property_name
        self.property_type = property_type
        self.constraint_value = constraint[self.constraint_key]
        # check if constraint is valid for property type
        if property_type not in self.valid_prop_types:
            raise ValidationError(_('Constraint type "%(ctype)s" is not valid '
                                    'for data type "%(dtype)s".') %
                                  {'ctype': self.constraint_key,
                                   'dtype': property_type})

    def _err_msg(self, value):
        return _('Property %s could not be validated.') % self.property_name

    def validate(self, value):
        if not self._is_valid(value):
            err_msg = self._err_msg(value)
            raise ValidationError(err_msg)

    @staticmethod
    def validate_integer(value):
        if not isinstance(value, int):
            raise ValueError(_('Value is not an integer for %s.') % value)
        return Constraint.validate_number(value)

    @staticmethod
    def validate_number(value):
        return Constraint.str_to_num(value)

    @staticmethod
    def validate_string(value):
        if not isinstance(value, str):
            raise ValueError(_('Value must be a string %s.') % value)
        return value

    @staticmethod
    def validate_list(self, value):
        if not isinstance(value, collections.Sequence):
            raise ValueError(_('Value must be a list %s.') % value)
        return value

    @staticmethod
    def str_to_num(value):
        '''Convert a string representation of a number into a numeric type.'''
        if isinstance(value, numbers.Number):
            return value
        try:
            return int(value)
        except ValueError:
            return float(value)


class Equal(Constraint):
    """Constraint class for "equal"

    Constrains a property or parameter to a value equal to ('=')
    the value declared.
    """

    constraint_key = Constraint.EQUAL

    valid_prop_types = Constraint.PROPERTY_TYPES

    def _is_valid(self, value):
        if value == self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s is not equal to "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class GreaterThan(Constraint):
    """Constraint class for "greater_than"

    Constrains a property or parameter to a value greater than ('>')
    the value declared.
    """

    constraint_key = Constraint.GREATER_THAN

    valid_types = (int, float, datetime.date,
                   datetime.time, datetime.datetime)

    valid_prop_types = (Constraint.INTEGER, Constraint.FLOAT,
                        Constraint.TIMESTAMP)

    def __init__(self, property_name, property_type, constraint):
        super(GreaterThan, self).__init__(property_name, property_type,
                                          constraint)
        if not isinstance(constraint[self.GREATER_THAN], self.valid_types):
            raise ValidationError(_('greater_than must be comparable.'))

    def _is_valid(self, value):
        if value > self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s must be greater than "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class GreaterOrEqual(Constraint):
    """Constraint class for "greater_or_equal"

    Constrains a property or parameter to a value greater than or equal
    to ('>=') the value declared.
    """

    constraint_key = Constraint.GREATER_OR_EQUAL

    valid_types = (int, float, datetime.date,
                   datetime.time, datetime.datetime)

    valid_prop_types = (Constraint.INTEGER, Constraint.FLOAT,
                        Constraint.TIMESTAMP)

    def __init__(self, property_name, property_type, constraint):
        super(GreaterOrEqual, self).__init__(property_name, property_type,
                                             constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('greater_or_equal must be comparable.'))

    def _is_valid(self, value):
        if value >= self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s must be greater or equal '
                  'to "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class LessThan(Constraint):
    """Constraint class for "less_than"

    Constrains a property or parameter to a value less than ('<')
    the value declared.
    """

    constraint_key = Constraint.LESS_THAN

    valid_types = (int, float, datetime.date,
                   datetime.time, datetime.datetime)

    valid_prop_types = (Constraint.INTEGER, Constraint.FLOAT,
                        Constraint.TIMESTAMP)

    def __init__(self, property_name, property_type, constraint):
        super(LessThan, self).__init__(property_name, property_type,
                                       constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('less_than must be comparable.'))

    def _is_valid(self, value):
        if value < self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s must be less than "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class LessOrEqual(Constraint):
    """Constraint class for "less_or_equal"

    Constrains a property or parameter to a value less than or equal
    to ('<=') the value declared.
    """

    constraint_key = Constraint.LESS_OR_EQUAL

    valid_types = (int, float, datetime.date,
                   datetime.time, datetime.datetime)

    valid_prop_types = (Constraint.INTEGER, Constraint.FLOAT,
                        Constraint.TIMESTAMP)

    def __init__(self, property_name, property_type, constraint):
        super(LessOrEqual, self).__init__(property_name, property_type,
                                          constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('less_or_equal must be comparable.'))

    def _is_valid(self, value):
        if value <= self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s must be less or '
                  'equal to "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class InRange(Constraint):
    """Constraint class for "in_range"

    Constrains a property or parameter to a value in range of (inclusive)
    the two values declared.
    """

    constraint_key = Constraint.IN_RANGE

    valid_types = (int, float, datetime.date,
                   datetime.time, datetime.datetime)

    valid_prop_types = (Constraint.INTEGER, Constraint.FLOAT,
                        Constraint.TIMESTAMP)

    def __init__(self, property_name, property_type, constraint):
        super(InRange, self).__init__(property_name, property_type, constraint)
        if(not isinstance(self.constraint_value, collections.Sequence) or
           (len(constraint[self.IN_RANGE]) != 2)):
            raise ValidationError(_('in_range must be a list.'))

        for value in self.constraint_value:
            if not isinstance(value, self.valid_types):
                raise ValidationError(_('in_range value must be comparable.'))

        self.min = self.constraint_value[0]
        self.max = self.constraint_value[1]

    def _is_valid(self, value):
        if value < self.min:
            return False
        if value > self.max:
            return False

        return True

    def _err_msg(self, value):
        return (_('%(pname)s: %(pvalue)s is out of range '
                  '(min:%(vmin)s, max:%(vmax)s).') %
                dict(pname=self.property_name,
                     pvalue=value,
                     vmin=self.min,
                     vmax=self.max))


class ValidValues(Constraint):
    """Constraint class for "valid_values"

    Constrains a property or parameter to a value that is in the list of
    declared values.
    """
    constraint_key = Constraint.VALID_VALUES

    valid_prop_types = Constraint.PROPERTY_TYPES

    def __init__(self, property_name, property_type, constraint):
        super(ValidValues, self).__init__(property_name, property_type,
                                          constraint)
        if not isinstance(self.constraint_value, collections.Sequence):
            raise ValidationError(_('valid_values must be a list.'))

    def _is_valid(self, value):
        if isinstance(value, collections.Sequence):
            return all(v in self.constraint_value for v in value)
        return value in self.constraint_value

    def _err_msg(self, value):
        allowed = '[%s]' % ', '.join(str(a) for a in self.constraint_value)
        return (_('%(pname)s: %(pvalue)s is not an valid '
                  'value "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=allowed))


class Length(Constraint):
    """Constraint class for "length"

    Constrains the property or parameter to a value of a given length.
    """

    constraint_key = Constraint.LENGTH

    valid_types = (int, )

    valid_prop_types = (Constraint.STRING, )

    def __init__(self, property_name, property_type, constraint):
        super(Length, self).__init__(property_name, property_type, constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('length must be integer.'))

    def _is_valid(self, value):
        if isinstance(value, str) and len(value) == self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('length of %(pname)s: %(pvalue)s must be equal '
                  'to "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class MinLength(Constraint):
    """Constraint class for "min_length"

    Constrains the property or parameter to a value to a minimum length.
    """

    constraint_key = Constraint.MIN_LENGTH

    valid_types = (int, )

    valid_prop_types = (Constraint.STRING, )

    def __init__(self, property_name, property_type, constraint):
        super(MinLength, self).__init__(property_name, property_type,
                                        constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('min_length must be integer.'))

    def _is_valid(self, value):
        if isinstance(value, str) and len(value) >= self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('length of %(pname)s: %(pvalue)s must be '
                  'at least "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class MaxLength(Constraint):
    """Constraint class for "max_length"

    Constrains the property or parameter to a value to a maximum length.
    """

    constraint_key = Constraint.MAX_LENGTH

    valid_types = (int, )

    valid_prop_types = (Constraint.STRING, )

    def __init__(self, property_name, property_type, constraint):
        super(MaxLength, self).__init__(property_name, property_type,
                                        constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('max_length must be integer.'))

    def _is_valid(self, value):
        if isinstance(value, str) and len(value) <= self.constraint_value:
            return True

        return False

    def _err_msg(self, value):
        return (_('length of %(pname)s: %(pvalue)s must be no greater '
                  'than "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


class Pattern(Constraint):
    """Constraint class for "pattern"

    Constrains the property or parameter to a value that is allowed by
    the provided regular expression.
    """

    constraint_key = Constraint.PATTERN

    valid_types = (str, )

    valid_prop_types = (Constraint.STRING, )

    def __init__(self, property_name, property_type, constraint):
        super(Pattern, self).__init__(property_name, property_type, constraint)
        if not isinstance(self.constraint_value, self.valid_types):
            raise ValidationError(_('pattern must be string.'))
        self.match = re.compile(self.constraint_value).match

    def _is_valid(self, value):
        match = self.match(value)
        return match is not None and match.end() == len(value)

    def _err_msg(self, value):
        return (_('%(pname)s: "%(pvalue)s" does not match '
                  'pattern "%(cvalue)s".') %
                dict(pname=self.property_name,
                     pvalue=value,
                     cvalue=self.constraint_value))


constraint_mapping = {
    Constraint.EQUAL: Equal,
    Constraint.GREATER_THAN: GreaterThan,
    Constraint.GREATER_OR_EQUAL: GreaterOrEqual,
    Constraint.LESS_THAN: LessThan,
    Constraint.LESS_OR_EQUAL: LessOrEqual,
    Constraint.IN_RANGE: InRange,
    Constraint.VALID_VALUES: ValidValues,
    Constraint.LENGTH: Length,
    Constraint.MIN_LENGTH: MinLength,
    Constraint.MAX_LENGTH: MaxLength,
    Constraint.PATTERN: Pattern
    }


def get_constraint_class(type):
    return constraint_mapping.get(type)
