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

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import URLException
from toscaparser.utils.gettextutils import _
import toscaparser.utils.urlutils

SECTIONS = (DESCRIPTION, URL, CREDENTIAL) = \
           ('description', 'url', 'credential')


class Repository(object):
    def __init__(self, repositories, values):
        self.name = repositories
        self.reposit = values
        if isinstance(self.reposit, dict):
            if 'url' not in self.reposit.keys():
                ExceptionCollector.appendException(
                    MissingRequiredFieldError(what=_('Repository "%s"')
                                              % self.name, required='url'))
            self.url = self.reposit['url']
        self.load_and_validate(self.name, self.reposit)

    def load_and_validate(self, val, reposit_def):
        self.keyname = val
        if isinstance(reposit_def, dict):
            for key in reposit_def.keys():
                if key not in SECTIONS:
                    ExceptionCollector.appendException(
                        UnknownFieldError(what=_('repositories "%s"')
                                          % self.keyname, field=key))

            if URL in reposit_def.keys():
                reposit_url = reposit_def.get(URL)
                url_val = toscaparser.utils.urlutils.UrlUtils.\
                    validate_url(reposit_url)
                if url_val is not True:
                    ExceptionCollector.appendException(
                        URLException(what=_('repsositories "%s" Invalid Url')
                                     % self.keyname))
