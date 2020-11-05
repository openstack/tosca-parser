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

import codecs
from collections import OrderedDict

from six.moves import urllib
import yaml

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import URLException
from toscaparser.utils.gettextutils import _


if hasattr(yaml, 'CSafeLoader'):
    yaml_loader = yaml.CSafeLoader
else:
    yaml_loader = yaml.SafeLoader


def load_yaml(path, a_file=True):
    """
    Load yaml file.

    Args:
        path: (str): write your description
        a_file: (str): write your description
    """
    f = None
    try:
        if a_file:
            f = codecs.open(path, encoding='utf-8', errors='strict')
        else:
            f = urllib.request.urlopen(path)
        contents = f.read()
        f.close()
        return yaml.load(contents, Loader=yaml_loader)
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            msg = (_('Failed to reach server "%(path)s". Reason is: '
                     '%(reason)s.')
                   % {'path': path, 'reason': e.reason})
            ExceptionCollector.appendException(URLException(what=msg))
            return
        elif hasattr(e, 'code'):
            msg = (_('The server "%(path)s" couldn\'t fulfill the request. '
                     'Error code: "%(code)s".')
                   % {'path': path, 'code': e.code})
            ExceptionCollector.appendException(URLException(what=msg))
            return
    except Exception:
        raise


def simple_parse(tmpl_str):
    """
    Parse a yaml file.

    Args:
        tmpl_str: (str): write your description
    """
    try:
        tpl = yaml.load(tmpl_str, Loader=yaml_loader)
    except yaml.YAMLError as yea:
        ExceptionCollector.appendException(ValueError(yea))
    else:
        if tpl is None:
            tpl = {}
    return tpl


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Deserialize a yaml stream.

    Args:
        stream: (str): write your description
        Loader: (todo): write your description
        yaml: (todo): write your description
        Loader: (todo): write your description
        object_pairs_hook: (str): write your description
        OrderedDict: (todo): write your description
    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        """
        Construct a mapping from a mapping.

        Args:
            loader: (todo): write your description
            node: (todo): write your description
        """
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def simple_ordered_parse(tmpl_str):
    """
    Parse a simple list of dictionaries.

    Args:
        tmpl_str: (str): write your description
    """
    try:
        tpl = ordered_load(tmpl_str)
    except yaml.YAMLError as yea:
        ExceptionCollector.appendException(ValueError(yea))
    else:
        if tpl is None:
            tpl = {}
    return tpl
