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
import dateutil.parser
import logging
import numbers
import re
import six

# from toscaparser.elements import constraints
from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTOSCAVersionPropertyException
from toscaparser.common.exception import RangeValueError
from toscaparser.utils.gettextutils import _

log = logging.getLogger('tosca')

RANGE_UNBOUNDED = 'UNBOUNDED'


def str_to_num(value):
    '''Convert a string representation of a number into a numeric type.'''
    # TODO(TBD) we should not allow numeric values in, input should be str
    if isinstance(value, numbers.Number):
        return value
    try:
        return int(value)
    except ValueError:
        return float(value)


def validate_numeric(value):
    if not isinstance(value, numbers.Number):
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a numeric.') % value))
    return value


def validate_integer(value):
    if not isinstance(value, int):
        try:
            value = int(value)
        except Exception:
            ExceptionCollector.appendException(
                ValueError(_('"%s" is not an integer.') % value))
    return value


def validate_float(value):
    if not isinstance(value, float):
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a float.') % value))
    return value


def validate_string(value):
    if not isinstance(value, six.string_types):
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a string.') % value))
    return value


def validate_list(value):
    if not isinstance(value, list):
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a list.') % value))
    return value


def validate_range(range):
    # list class check
    validate_list(range)
    # validate range list has a min and max
    if len(range) != 2:
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a valid range.') % range))
    # validate min and max are numerics or the keyword UNBOUNDED
    min_test = max_test = False
    if not range[0] == RANGE_UNBOUNDED:
        min = validate_numeric(range[0])
    else:
        min_test = True
    if not range[1] == RANGE_UNBOUNDED:
        max = validate_numeric(range[1])
    else:
        max_test = True
    # validate the max > min (account for UNBOUNDED)
    if not min_test and not max_test:
        # Note: min == max is allowed
        if min > max:
            ExceptionCollector.appendException(
                ValueError(_('"%s" is not a valid range.') % range))

    return range


def validate_value_in_range(value, range, prop_name):
    validate_numeric(value)
    validate_range(range)

    # Note: value is valid if equal to min
    if range[0] != RANGE_UNBOUNDED:
        if value < range[0]:
            ExceptionCollector.appendException(
                RangeValueError(pname=prop_name,
                                pvalue=value,
                                vmin=range[0],
                                vmax=range[1]))
    # Note: value is valid if equal to max
    if range[1] != RANGE_UNBOUNDED:
        if value > range[1]:
            ExceptionCollector.appendException(
                RangeValueError(pname=prop_name,
                                pvalue=value,
                                vmin=range[0],
                                vmax=range[1]))
    return value


def validate_map(value):
    if not isinstance(value, collections.Mapping):
        ExceptionCollector.appendException(
            ValueError(_('"%s" is not a map.') % value))
    return value


def validate_boolean(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalised = value.lower()
        if normalised in ['true', 'false']:
            return normalised == 'true'

    ExceptionCollector.appendException(
        ValueError(_('"%s" is not a boolean.') % value))


def validate_timestamp(value):
    try:
        # Note: we must return our own exception message
        # as dateutil's parser returns different types / values on
        # different systems. OSX, for example, returns a tuple
        # containing a different error message than Linux
        dateutil.parser.parse(value)
    except Exception as e:
        original_err_msg = str(e)
        log.error(original_err_msg)
        ExceptionCollector.appendException(
            ValueError(_('"%(val)s" is not a valid timestamp. "%(msg)s"') %
                       {'val': value, 'msg': original_err_msg}))
    return


class TOSCAVersionProperty(object):

    VERSION_RE = re.compile('^(?P<major_version>([0-9][0-9]*))'
                            '(\.(?P<minor_version>([0-9][0-9]*)))?'
                            '(\.(?P<fix_version>([0-9][0-9]*)))?'
                            '(\.(?P<qualifier>([0-9A-Za-z]+)))?'
                            '(\-(?P<build_version>[0-9])*)?$')

    def __init__(self, version):
        self.version = str(version)
        match = self.VERSION_RE.match(self.version)
        if not match:
            ExceptionCollector.appendException(
                InvalidTOSCAVersionPropertyException(what=(self.version)))
            return
        ver = match.groupdict()
        if self.version in ['0', '0.0', '0.0.0']:
            log.warning(_('Version assumed as not provided'))
            self.version = None
        self.minor_version = ver['minor_version']
        self.major_version = ver['major_version']
        self.fix_version = ver['fix_version']
        self.qualifier = self._validate_qualifier(ver['qualifier'])
        self.build_version = self._validate_build(ver['build_version'])
        self._validate_major_version(self.major_version)

    def _validate_major_version(self, value):
        """Validate major version

        Checks if only major version is provided and assumes
        minor version as 0.
        Eg: If version = 18, then it returns version = '18.0'
        """

        if self.minor_version is None and self.build_version is None and \
                value != '0':
            log.warning(_('Minor version assumed "0".'))
            self.version = '.'.join([value, '0'])
        return value

    def _validate_qualifier(self, value):
        """Validate qualifier

           TOSCA version is invalid if a qualifier is present without the
           fix version or with all of major, minor and fix version 0s.

           For example, the following versions are invalid
              18.0.abc
              0.0.0.abc
        """
        if (self.fix_version is None and value) or \
            (self.minor_version == self.major_version ==
             self.fix_version == '0' and value):
            ExceptionCollector.appendException(
                InvalidTOSCAVersionPropertyException(what=(self.version)))
        return value

    def _validate_build(self, value):
        """Validate build version

           TOSCA version is invalid if build version is present without the
           qualifier.
           Eg: version = 18.0.0-1 is invalid.
        """
        if not self.qualifier and value:
            ExceptionCollector.appendException(
                InvalidTOSCAVersionPropertyException(what=(self.version)))
        return value

    def get_version(self):
        return self.version
