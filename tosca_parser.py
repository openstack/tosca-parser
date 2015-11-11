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


from toscaparser import shell as parser_shell

"""
Test utility to show how TOSCA Parser can be used programmatically

It can be used as,
#python tosca_parser.py --template-file=<path to the YAML template>
#python tosca_parser.py --template-file=<path to the CSAR zip file>
#python tosca_parser.py --template-file=<URL to the template or CSAR>

e.g.
#python tosca_parser.py
--template-file=toscaparser/tests/data/tosca_helloworld.yaml
#python tosca_parser.py
--template-file=toscaparser/tests/data/CSAR/csar_hello_world.zip
"""

if __name__ == '__main__':
    parser_shell.main()
