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

import gettext
import os

_localedir = os.environ.get('tosca-parser'.upper() + '_LOCALEDIR')
_t = gettext.translation('tosca-parser', localedir=_localedir,
                         fallback=True)


def _(msg):
    """
    Returns a message text

    Args:
        msg: (str): write your description
    """
    # type: (object) -> object
    return _t.gettext(msg)
