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

from translator.hot.tosca.tosca_block_storage import ToscaBlockStorage
from translator.toscalib.common.exception import InvalidPropertyValueError
from translator.toscalib.nodetemplate import NodeTemplate
from translator.toscalib.tests.base import TestCase
from translator.toscalib.utils.gettextutils import _
import translator.toscalib.utils.yamlparser


class ToscaBlockStoreTest(TestCase):

    def _tosca_blockstore_test(self, tpl_snippet, expectedprops):
        nodetemplates = (translator.toscalib.utils.yamlparser.
                         simple_parse(tpl_snippet)['node_templates'])
        name = list(nodetemplates.keys())[0]
        try:
            nodetemplate = NodeTemplate(name, nodetemplates)
            tosca_block_store = ToscaBlockStorage(nodetemplate)
            tosca_block_store.handle_properties()
            if not self._compare_properties(tosca_block_store.properties,
                                            expectedprops):
                raise Exception(_("Hot Properties are not"
                                  " same as expected properties"))
        except Exception:
            # for time being rethrowing. Will be handled future based
            # on new development
            raise

    def _compare_properties(self, hotprops, expectedprops):
        return all(item in hotprops.items() for item in expectedprops.items())

    def test_node_blockstorage_with_properties(self):
        tpl_snippet = '''
        node_templates:
          my_storage:
            type: tosca.nodes.BlockStorage
            properties:
              size: 1024 MiB
              snapshot_id: abc
        '''
        expectedprops = {'snapshot_id': 'abc',
                         'size': 1}
        self._tosca_blockstore_test(
            tpl_snippet,
            expectedprops)

        tpl_snippet = '''
        node_templates:
          my_storage:
            type: tosca.nodes.BlockStorage
            properties:
              size: 124 MB
              snapshot_id: abc
        '''
        expectedprops = {'snapshot_id': 'abc',
                         'size': 1}
        self._tosca_blockstore_test(
            tpl_snippet,
            expectedprops)

    def test_node_blockstorage_with_invalid_size_property(self):
        tpl_snippet = '''
        node_templates:
          my_storage:
            type: tosca.nodes.BlockStorage
            properties:
              size: 0 MB
              snapshot_id: abc
        '''
        expectedprops = {}
        self.assertRaises(InvalidPropertyValueError,
                          lambda: self._tosca_blockstore_test(tpl_snippet,
                                                              expectedprops))
