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
from toscaparser.common.exception import InvalidSchemaError
from toscaparser.common.exception import TOSCAException
from toscaparser.utils.gettextutils import _


class PropertyDef(object):
    '''TOSCA built-in Property type.'''

    VALID_PROPERTY_KEYNAMES = (PROPERTY_KEYNAME_DEFAULT,
                               PROPERTY_KEYNAME_REQUIRED,
                               PROPERTY_KEYNAME_STATUS) = \
        ('default', 'required', 'status')

    PROPERTY_REQUIRED_DEFAULT = True

    VALID_REQUIRED_VALUES = ['true', 'false']
    VALID_STATUS_VALUES = (PROPERTY_STATUS_SUPPORTED,
                           PROPERTY_STATUS_EXPERIMENTAL) = \
        ('supported', 'experimental')

    PROPERTY_STATUS_DEFAULT = PROPERTY_STATUS_SUPPORTED

    def __init__(self, name, value=None, schema=None):
        self.name = name
        self.value = value
        self.schema = schema
        self._status = self.PROPERTY_STATUS_DEFAULT
        self._required = self.PROPERTY_REQUIRED_DEFAULT

        # Validate required 'type' property exists
        try:
            self.schema['type']
        except KeyError:
            msg = (_('Schema definition of "%(pname)s" must have a "type" '
                     'attribute.') % dict(pname=self.name))
            ExceptionCollector.appendException(
                InvalidSchemaError(message=msg))

        if self.schema:
            self._load_required_attr_from_schema()
            self._load_status_attr_from_schema()

    @property
    def default(self):
        if self.schema:
            for prop_key, prop_value in self.schema.items():
                if prop_key == self.PROPERTY_KEYNAME_DEFAULT:
                    return prop_value
        return None

    @property
    def required(self):
        return self._required

    def _load_required_attr_from_schema(self):
        # IF 'required' keyname exists verify it's a boolean,
        # if so override default
        if self.PROPERTY_KEYNAME_REQUIRED in self.schema:
            value = self.schema[self.PROPERTY_KEYNAME_REQUIRED]
            if isinstance(value, bool):
                self._required = value
            else:
                valid_values = ', '.join(self.VALID_REQUIRED_VALUES)
                attr = self.PROPERTY_KEYNAME_REQUIRED
                TOSCAException.generate_inv_schema_property_error(self,
                                                                  attr,
                                                                  value,
                                                                  valid_values)

    @property
    def status(self):
        return self._status

    def _load_status_attr_from_schema(self):
        # IF 'status' keyname exists verify it's a valid value,
        # if so override default
        if self.PROPERTY_KEYNAME_STATUS in self.schema:
            value = self.schema[self.PROPERTY_KEYNAME_STATUS]
            if value in self.VALID_STATUS_VALUES:
                self._status = value
            else:
                valid_values = ', '.join(self.VALID_STATUS_VALUES)
                attr = self.PROPERTY_KEYNAME_STATUS
                TOSCAException.generate_inv_schema_property_error(self,
                                                                  attr,
                                                                  value,
                                                                  valid_values)
