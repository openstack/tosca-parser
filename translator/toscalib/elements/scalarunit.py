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

import re

from translator.toscalib.utils.gettextutils import _
from translator.toscalib.utils import validateutils


class ScalarUnit(object):
    '''Parent class for scalar-unit type.'''

    SCALAR_UNIT_TYPES = (
        SCALAR_UNIT_SIZE, SCALAR_UNIT_FREQUENCY, SCALAR_UNIT_TIME
    ) = (
        'scalar-unit.size', 'scalar-unit.frequency', 'scalar-unit.time'
    )

    def __init__(self, value):
        self.value = value

    def validate_scalar_unit(self):
        regex = re.compile('([0-9.]+)\s*(\w+)')
        try:
            result = regex.match(str(self.value)).groups()
            validateutils.str_to_num(result[0])
        except Exception:
            raise ValueError(_('"%s" is not a valid scalar-unit')
                             % self.value)
        if result[1].upper() in self.SCALAR_UNIT_DICT.keys():
            return self.value
        raise ValueError(_('"%s" is not a valid scalar-unit') % self.value)

    def get_num_from_scalar_unit(self, unit=None):
        if unit:
            if unit.upper() not in self.SCALAR_UNIT_DICT.keys():
                raise ValueError(_('input unit "%s" is not a valid unit')
                                 % unit)
        else:
            unit = self.SCALAR_UNIT_DEFAULT
        self.validate_scalar_unit()

        regex = re.compile('([0-9.]+)\s*(\w+)')
        result = regex.match(str(self.value)).groups()
        converted = (float(validateutils.str_to_num(result[0]))
                     * self.SCALAR_UNIT_DICT[result[1].upper()]
                     / self.SCALAR_UNIT_DICT[unit.upper()])
        if converted - int(converted) < 0.0000000000001:
            converted = int(converted)
        return converted


class ScalarUnit_Size(ScalarUnit):

    SCALAR_UNIT_DEFAULT = 'B'
    SCALAR_UNIT_DICT = {'B': 1, 'KB': 1000, 'KIB': 1024, 'MB': 1000000,
                        'MIB': 1048576, 'GB': 1000000000,
                        'GIB': 1073741824, 'TB': 1000000000000,
                        'TIB': 1099511627776}


class ScalarUnit_Time(ScalarUnit):

    SCALAR_UNIT_DEFAULT = 'MS'
    SCALAR_UNIT_DICT = {'D': 86400, 'H': 3600, 'M': 60, 'S': 1,
                        'MS': 0.001, 'US': 0.000001, 'NS': 0.000000001}


class ScalarUnit_Frequency(ScalarUnit):

    SCALAR_UNIT_DEFAULT = 'GHZ'
    SCALAR_UNIT_DICT = {'HZ': 1, 'KHZ': 1000,
                        'MHZ': 1000000, 'GHZ': 1000000000}


scalarunit_mapping = {
    ScalarUnit.SCALAR_UNIT_FREQUENCY: ScalarUnit_Frequency,
    ScalarUnit.SCALAR_UNIT_SIZE: ScalarUnit_Size,
    ScalarUnit.SCALAR_UNIT_TIME: ScalarUnit_Time,
    }


def get_scalarunit_class(type):
    return scalarunit_mapping.get(type)


def get_scalarunit_value(type, value, unit=None):
    if type in ScalarUnit.SCALAR_UNIT_TYPES:
        ScalarUnit_Class = get_scalarunit_class(type)
        return (ScalarUnit_Class(value).
                get_num_from_scalar_unit(unit))
    else:
        raise TypeError(_('"%s" is not a valid scalar-unit type') % type)
