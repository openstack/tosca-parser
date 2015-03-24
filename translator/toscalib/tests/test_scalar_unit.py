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

from translator.toscalib.common import exception
from translator.toscalib.elements.constraints import Constraint
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.tests.base import TestCase
from translator.toscalib.utils import yamlparser


class ScalarUnitPositiveTest(TestCase):

    scenarios = [
        (
            # tpl_snippet with mem_size given as number
            'mem_size_is_number',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1024
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with mem_size given as number+space+MB
            'mem_size_is_number_Space_MB',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1024 MB
                 ''',
                 expected='1024 MB')
        ),
        (
            # tpl_snippet with mem_size given as number+spaces+GB
            'mem_size_is_number_Space_GB',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1     GB
                 ''',
                 expected='1     GB')
        ),
        (
            # tpl_snippet with mem_size given as number+tiB
            'mem_size_is_number_NoSpace_GB',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1tiB
                 ''',
                 expected='1tiB')
        ),
        (
            # tpl_snippet with mem_size given as number+Spaces+GIB
            'mem_size_is_number_Spaces_GB',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1     GIB
                 ''',
                 expected='1     GIB')
        ),
        (
            # tpl_snippet with mem_size given as number+Space+tib
            'mem_size_is_number_Spaces_GB',
            dict(tpl_snippet='''
                 server:
                   type: tosca.nodes.Compute
                   properties:
                     mem_size: 1 tib
                 ''',
                 expected='1 tib')
        ),
    ]

    def test_scenario_scalar_unit_positive(self):
        tpl = self.tpl_snippet
        nodetemplates = yamlparser.simple_parse(tpl)
        nodetemplate = NodeTemplate('server', nodetemplates)
        props = nodetemplate.get_properties()
        if props and 'mem_size' in props.keys():
            prop = props['mem_size']
            self.assertIsNone(prop.validate())
            resolved = prop.value
        self.assertEqual(resolved, self.expected)


class GetNumFromScalarUnitSizePositive(TestCase):

    scenarios = [
        (   # Note that (1 TB) / (1 GB) = 1000
            'Input is TB, user input is GB',
            dict(InputMemSize='1   TB',
                 UserInputUnit='gB',
                 expected=1000)
        ),
        (   # Note that (1 Tib)/ (1 GB) = 1099
            'Input is TiB, user input is GB',
            dict(InputMemSize='1   TiB',
                 UserInputUnit='gB',
                 expected=1099)
        ),
    ]

    def test_scenario_get_num_from_scalar_unit_size(self):
        resolved = Constraint.get_num_from_scalar_unit_size(self.InputMemSize,
                                                            self.UserInputUnit)
        self.assertEqual(resolved, self.expected)


class GetNumFromScalarUnitSizeNegative(TestCase):

    InputMemSize = '1 GB'
    UserInputUnit = 'qB'

    def test_get_num_from_scalar_unit_size_negative(self):
        try:
            Constraint.get_num_from_scalar_unit_size(self.InputMemSize,
                                                     self.UserInputUnit)
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))
            self.assertEqual('input unit "qB" is not a valid unit',
                             error.__str__())


class ScalarUnitNegativeTest(TestCase):

    custom_def_snippet = '''
    tosca.my.nodes.Compute:
      derived_from: tosca.nodes.Root
      properties:
        disk_size:
          required: no
          type: scalar-unit.size
          constraints:
            - greater_or_equal: 1 GB
        mem_size:
          required: no
          type: scalar-unit.size
          constraints:
            - in_range: [1 MiB, 1 GiB]
    '''
    custom_def = yamlparser.simple_parse(custom_def_snippet)

    # disk_size doesn't provide a value, mem_size uses an invalid unit.
    def test_invalid_scalar_unit(self):
        tpl_snippet = '''
        server:
          type: tosca.my.nodes.Compute
          properties:
            disk_size: MB
            mem_size: 1 QB
        '''
        nodetemplates = yamlparser.simple_parse(tpl_snippet)
        nodetemplate = NodeTemplate('server', nodetemplates, self.custom_def)
        for p in nodetemplate.get_properties_objects():
            self.assertRaises(ValueError, p.validate)

    # disk_size is less than 1 GB, mem_size is not in the required range.
    # Note: in the spec, the minimum value of mem_size is 1 MiB (> 1 MB)
    def test_constraint_for_scalar_unit(self):
        tpl_snippet = '''
        server:
          type: tosca.my.nodes.Compute
          properties:
            disk_size: 500 MB
            mem_size: 1 MB
        '''
        nodetemplates = yamlparser.simple_parse(tpl_snippet)
        nodetemplate = NodeTemplate('server', nodetemplates, self.custom_def)
        props = nodetemplate.get_properties()
        if 'disk_size' in props.keys():
            error = self.assertRaises(exception.ValidationError,
                                      props['disk_size'].validate)
            self.assertEqual('disk_size: 500 MB must be greater or '
                             'equal to "1 GB".', error.__str__())

        if 'mem_size' in props.keys():
            error = self.assertRaises(exception.ValidationError,
                                      props['mem_size'].validate)
            self.assertEqual('mem_size: 1 MB is out of range '
                             '(min:1 MiB, '
                             'max:1 GiB).', error.__str__())
