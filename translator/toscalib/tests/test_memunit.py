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

from translator.toscalib.common.exception import InvalidPropertyValueError
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.tests.base import TestCase
import translator.toscalib.utils.yamlparser


class ToscaTemplateMemorySizeOutputTest(TestCase):

    scenarios = [
        (
            # tpl_snippet with mem_size given as number
            'mem_size_is_number',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1024
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with mem_size given as number+space+MB
            'mem_size_is_number_Space_MB',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1024 MB
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with mem_size given as number+space+GB
            'mem_size_is_number_Space_GB',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1 GB
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with mem_size given as number+GB
            'mem_size_is_number_NoSpace_GB',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1GB
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with mem_size given as number+Spaces+GB
            'mem_size_is_number_Spaces_GB',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1     GB
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
        (
            # tpl_snippet with no mem_size given
            'mem_size_is_absent',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       # host image properties
                       os_type: Linux
                 ''',
                 expected=1024)
        ),
    ]

    def test_scenario_mem_size(self):
        tpl = self.tpl_snippet
        nodetemplates = (translator.toscalib.utils.yamlparser.
                         simple_parse(tpl))['node_templates']
        name = list(nodetemplates.keys())[0]
        nodetemplate = NodeTemplate(name, nodetemplates)
        for p in nodetemplate.properties:
            if p.name == 'mem_size':
                resolved = p.value
        self.assertEqual(resolved, self.expected)


class ToscaTemplateMemorySizeErrorTest(TestCase):

    scenarios = [
        (
            # tpl_snippet with mem_size given as empty (error)
            'mem_size_is_empty',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size:
                       # host image properties
                       os_type: Linux
                 ''',
                 err=InvalidPropertyValueError)
        ),
        (
            # tpl_snippet with mem_size given as number+InvalidUnit (error)
            'mem_size_unit_is_invalid',
            dict(tpl_snippet='''
                 node_templates:
                   server:
                     type: tosca.nodes.Compute
                     properties:
                       # compute properties (flavor)
                       mem_size: 1    QB
                       # host image properties
                       os_type: Linux
                 ''',
                 err=InvalidPropertyValueError)
        ),
    ]

    def test_scenario_mem_size_error(self):
        tpl = self.tpl_snippet
        nodetemplates = (translator.toscalib.utils.yamlparser.
                         simple_parse(tpl))['node_templates']
        name = list(nodetemplates.keys())[0]
        nodetemplate = NodeTemplate(name, nodetemplates)
        self.assertRaises(self.err,
                          nodetemplate._create_properties)
