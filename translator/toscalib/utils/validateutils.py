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
import numbers
import six

from translator.toscalib.utils.gettextutils import _


def str_to_num(value):
    '''Convert a string representation of a number into a numeric type.'''
    if isinstance(value, numbers.Number):
        return value
    try:
        return int(value)
    except ValueError:
        return float(value)


def validate_number(value):
    return str_to_num(value)


def validate_integer(value):
    if not isinstance(value, int):
        raise ValueError(_('"%s" is not an integer') % value)
    return validate_number(value)


def validate_float(value):
    if not isinstance(value, float):
        raise ValueError(_('"%s" is not a float') % value)
    return validate_number(value)


def validate_string(value):
    if not isinstance(value, six.string_types):
        raise ValueError(_('"%s" is not a string') % value)
    return value


def validate_list(value):
    if not isinstance(value, list):
        raise ValueError(_('"%s" is not a list') % value)
    return value


def validate_map(value):
    if not isinstance(value, collections.Mapping):
        raise ValueError(_('"%s" is not a map') % value)
    return value


def validate_boolean(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalised = value.lower()
        if normalised in ['true', 'false']:
            return normalised == 'true'
    raise ValueError(_('"%s" is not a boolean') % value)


def validate_timestamp(value):
    return dateutil.parser.parse(value)
