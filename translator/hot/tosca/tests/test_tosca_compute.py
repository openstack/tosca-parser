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

from translator.hot.tosca.tosca_compute import ToscaCompute
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.tests.base import TestCase
from translator.toscalib.utils.gettextutils import _
import translator.toscalib.utils.yamlparser


class ToscaComputeTest(TestCase):

    def _tosca_compute_test(self, tpl_snippet, expectedprops):
        nodetemplates = (translator.toscalib.utils.yamlparser.
                         simple_parse(tpl_snippet)['node_templates'])
        name = list(nodetemplates.keys())[0]
        try:
            nodetemplate = NodeTemplate(name, nodetemplates)
            toscacompute = ToscaCompute(nodetemplate)
            toscacompute.handle_properties()
            if not self._compare_properties(toscacompute.properties,
                                            expectedprops):
                raise Exception(_("Hot Properties are not"
                                  " same as expected properties"))
        except Exception:
            # for time being rethrowing. Will be handled future based
            # on new development in Glance and Graffiti
            raise

    def _compare_properties(self, hotprops, expectedprops):
        return all(item in hotprops.items() for item in expectedprops.items())

    def test_node_compute_with_properties_and_capabilities(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: 4
              mem_size: 4096
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
        '''
        expectedprops = {'flavor': 'm1.large',
                         'image': 'fedora-amd64-heat-config'}
        self._tosca_compute_test(
            tpl_snippet,
            expectedprops)

    def test_node_compute_without_os_capabilities(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              # compute properties (flavor)
              disk_size: 10
              num_cpus: 4
              mem_size: 4096
            capabilities:
              #left intentionally
        '''
        expectedprops = {'flavor': 'm1.large',
                         'image': None}
        self._tosca_compute_test(
            tpl_snippet,
            expectedprops)

    def test_node_compute_without_properties(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              #left intentionally
            capabilities:
              os:
                properties:
                  architecture: x86_64
                  type: Linux
                  distribution: Fedora
                  version: 18
        '''
        expectedprops = {'flavor': None,
                         'image': 'fedora-amd64-heat-config'}
        self._tosca_compute_test(
            tpl_snippet,
            expectedprops)

    def test_node_compute_without_properties_and_os_capabilities(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
            properties:
              #left intentionally
            capabilities:
              #left intentionally
        '''
        expectedprops = {'flavor': None,
                         'image': None}
        self._tosca_compute_test(
            tpl_snippet,
            expectedprops)

    def test_node_compute_with_only_type(self):
        tpl_snippet = '''
        node_templates:
          server:
            type: tosca.nodes.Compute
        '''
        expectedprops = {'flavor': None,
                         'image': None}
        self._tosca_compute_test(
            tpl_snippet,
            expectedprops)
