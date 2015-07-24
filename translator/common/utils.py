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


import logging
import math
import numbers
import os
import re
from translator.toscalib.tosca_template import ToscaTemplate
from translator.toscalib.utils.gettextutils import _
import translator.toscalib.utils.yamlparser
import yaml

YAML_ORDER_PARSER = translator.toscalib.utils.yamlparser.simple_ordered_parse
log = logging.getLogger('tosca')


class MemoryUnit(object):

    UNIT_SIZE_DEFAULT = 'B'
    UNIT_SIZE_DICT = {'B': 1, 'KB': 1000, 'KIB': 1024, 'MB': 1000000,
                      'MIB': 1048576, 'GB': 1000000000,
                      'GIB': 1073741824, 'TB': 1000000000000,
                      'TIB': 1099511627776}

    @staticmethod
    def convert_unit_size_to_num(size, unit=None):
        """Convert given size to a number representing given unit.

        If unit is None, convert to a number representing UNIT_SIZE_DEFAULT
        :param size: unit size e.g. 1 TB
        :param unit: unit to be converted to e.g GB
        :return: converted number e.g. 1000 for 1 TB size and unit GB
        """

        if unit:
            MemoryUnit.validate_unit(unit)
        else:
            unit = MemoryUnit.UNIT_SIZE_DEFAULT

        regex = re.compile('(\d*)\s*(\w*)')
        result = regex.match(str(size)).groups()
        if result[1]:
            MemoryUnit.validate_unit(result[1])
            converted = int(str_to_num(result[0])
                            * MemoryUnit.UNIT_SIZE_DICT[result[1].upper()]
                            * math.pow(MemoryUnit.UNIT_SIZE_DICT
                                       [unit.upper()], -1))
        else:
            converted = (str_to_num(result[0]))
        return converted

    @staticmethod
    def validate_unit(unit):
        if unit.upper() not in MemoryUnit.UNIT_SIZE_DICT.keys():
            msg = _('Provided unit "{0}" is not valid. The valid units are '
                    '{1}').format(unit, MemoryUnit.UNIT_SIZE_DICT.keys())
            raise ValueError(msg)


class CompareUtils(object):

    MISMATCH_VALUE1_LABEL = "<Expected>"
    MISMATCH_VALUE2_LABEL = "<Provided>"
    ORDERLESS_LIST_KEYS = ['allowed_values', 'depends_on']

    @staticmethod
    def compare_dicts(dict1, dict2):
        """Return False if not equal, True if both are equal."""

        if dict1 is None and dict2 is None:
            return True
        if dict1 is None or dict2 is None:
            return False

        both_equal = True
        for dict1_item, dict2_item in zip(dict1.items(), dict2.items()):
            if dict1_item != dict2_item:
                log.warning(CompareUtils.MISMATCH_VALUE2_LABEL,
                            ": %s \n is not equal to \n",
                            CompareUtils.MISMATCH_VALUE1_LABEL,
                            ": %s", dict1_item, dict2_item)
                both_equal = False
                break
        return both_equal

    @staticmethod
    def compare_hot_yamls(generated_yaml, expected_yaml):
        hot_translated_dict = YAML_ORDER_PARSER(generated_yaml)
        hot_expected_dict = YAML_ORDER_PARSER(expected_yaml)
        return CompareUtils.compare_dicts(hot_translated_dict,
                                          hot_expected_dict)

    @staticmethod
    def reorder(dic):
        '''Canonicalize list items in the dictionary for ease of comparison.

        For properties whose value is a list in which the order does not
        matter, some pre-processing is required to bring those lists into a
        canonical format. We use sorting just to make sure such differences
        in ordering would not cause to a mismatch.
        '''

        if type(dic) is not dict:
            return None

        reordered = {}
        for key in dic.keys():
            value = dic[key]
            if type(value) is dict:
                reordered[key] = CompareUtils.reorder(value)
            elif type(value) is list \
                and key in CompareUtils.ORDERLESS_LIST_KEYS:
                reordered[key] = sorted(value)
            else:
                reordered[key] = value
        return reordered

    @staticmethod
    def diff_dicts(dict1, dict2, reorder=True):
        '''Compares two dictionaries and returns their differences.

        Returns a dictionary of mismatches between the two dictionaries.
        An empty dictionary is returned if two dictionaries are equivalent.
        The reorder parameter indicates whether reordering is required
        before comparison or not.
        '''

        if reorder:
            dict1 = CompareUtils.reorder(dict1)
            dict2 = CompareUtils.reorder(dict2)

        if dict1 is None and dict2 is None:
            return {}
        if dict1 is None or dict2 is None:
            return {CompareUtils.MISMATCH_VALUE1_LABEL: dict1,
                    CompareUtils.MISMATCH_VALUE2_LABEL: dict2}

        diff = {}
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        for key in keys1.union(keys2):
            if key in keys1 and key not in keys2:
                diff[key] = {CompareUtils.MISMATCH_VALUE1_LABEL: dict1[key],
                             CompareUtils.MISMATCH_VALUE2_LABEL: None}
            elif key not in keys1 and key in keys2:
                diff[key] = {CompareUtils.MISMATCH_VALUE1_LABEL: None,
                             CompareUtils.MISMATCH_VALUE2_LABEL: dict2[key]}
            else:
                val1 = dict1[key]
                val2 = dict2[key]
                if val1 != val2:
                    if type(val1) is dict and type(val2) is dict:
                        diff[key] = CompareUtils.diff_dicts(val1, val2, False)
                    else:
                        diff[key] = {CompareUtils.MISMATCH_VALUE1_LABEL: val1,
                                     CompareUtils.MISMATCH_VALUE2_LABEL: val2}
        return diff


class YamlUtils(object):

    @staticmethod
    def get_dict(yaml_file):
        '''Returns the dictionary representation of the given YAML spec.'''
        try:
            return yaml.load(open(yaml_file))
        except IOError:
            return None

    @staticmethod
    def compare_yamls(yaml1_file, yaml2_file):
        '''Returns true if two dictionaries are equivalent, false otherwise.'''
        dict1 = YamlUtils.get_dict(yaml1_file)
        dict2 = YamlUtils.get_dict(yaml2_file)
        return CompareUtils.compare_dicts(dict1, dict2)

    @staticmethod
    def compare_yaml_dict(yaml_file, dic):
        '''Returns true if yaml matches the dictionary, false otherwise.'''
        return CompareUtils.compare_dicts(YamlUtils.get_dict(yaml_file), dic)


class TranslationUtils(object):

    @staticmethod
    def compare_tosca_translation_with_hot(tosca_file, hot_file, params):
        '''Verify tosca translation against the given hot specification.

        inputs:
        tosca_file: relative path to tosca input
        hot_file: relative path to expected hot output
        params: dictionary of parameter name value pairs

        Returns as a dictionary the difference between the HOT translation
        of the given tosca_file and the given hot_file.
        '''

        tosca_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), tosca_file)
        expected_hot_tpl = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), hot_file)

        tosca = ToscaTemplate(tosca_tpl, params)
        translate = translator.hot.tosca_translator.TOSCATranslator(tosca,
                                                                    params)
        output = translate.translate()
        output_dict = translator.toscalib.utils.yamlparser.simple_parse(output)
        expected_output_dict = YamlUtils.get_dict(expected_hot_tpl)
        return CompareUtils.diff_dicts(output_dict, expected_output_dict)


def str_to_num(value):
    """Convert a string representation of a number into a numeric type."""
    if isinstance(value, numbers.Number):
        return value
    try:
        return int(value)
    except ValueError:
        return float(value)
