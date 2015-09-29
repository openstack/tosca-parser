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


import os
import sys

from toscaparser.tosca_template import ToscaTemplate
from toscaparser.utils.gettextutils import _
import toscaparser.utils.urlutils

"""
CLI test utility to show how TOSCA Parser can be used programmatically

This is a basic command line test utility showing the entry point in the
TOSCA Parser and how to iterate over parsed template. It can be extended
or modified to fit an individual need.

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


def main():
    if len(sys.argv) < 2:
        msg = _("The program requires template or CSAR file as an argument. "
                "Please refer to the usage documentation.")
        raise ValueError(msg)
    if "--template-file=" not in sys.argv[1]:
        msg = _("The program expects --template-file as first argument. "
                "Please refer to the usage documentation.")
    path = sys.argv[1].split('--template-file=')[1]
    if os.path.isfile(path):
        parse(path)
    elif toscaparser.utils.urlutils.UrlUtils.validate_url(path):
        parse(path, False)
    else:
        raise ValueError(_("%(path)s is not a valid file.") % {'path': path})


def parse(path, a_file=True):
    output = None
    tosca = ToscaTemplate(path, None, a_file)
    version = tosca.version
    if tosca.version:
        print ("\nversion:\n" + version)
    description = tosca.description
    if description:
        print ("\ndescription:\n" + description)
    inputs = tosca.inputs
    if inputs:
        print ("\ninputs:")
        for input in inputs:
            print (input.name)
    nodetemplates = tosca.nodetemplates
    if nodetemplates:
        print ("\nnodetemplates:")
        for node in nodetemplates:
            print (node.name)
    outputs = tosca.outputs
    if outputs:
        print ("\noutputs:")
        for output in outputs:
            print (output.name)


if __name__ == '__main__':
    main()
