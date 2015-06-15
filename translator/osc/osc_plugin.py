#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from translator.osc import utils

DEFAULT_TRANSLATOR_API_VERSION = '1'
API_VERSION_OPTION = 'os_translator_api_version'
API_NAME = 'translator'
API_VERSIONS = {
    '1': 'translator.v1.client.Client',
}


def make_client(instance):
    # NOTE(stevemar): We don't need a client because
    # heat-translator itself is a command line tool
    pass


def build_option_parser(parser):
    """Hook to add global options."""

    parser.add_argument(
        '--os-translator-api-version',
        metavar='<translator-api-version>',
        default=utils.env(
            'OS_TRANSLATOR_API_VERSION',
            default=DEFAULT_TRANSLATOR_API_VERSION),
        help='Translator API version, default=' +
             DEFAULT_TRANSLATOR_API_VERSION +
             ' (Env: OS_TRANSLATOR_API_VERSION)')
    return parser
