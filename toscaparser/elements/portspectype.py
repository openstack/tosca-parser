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

import logging

from toscaparser.common.exception import ExceptionCollector
from toscaparser.common.exception import InvalidTypeAdditionalRequirementsError
from toscaparser.utils.gettextutils import _
import toscaparser.utils.validateutils as validateutils

log = logging.getLogger('tosca')


class PortSpec(object):
    '''Parent class for tosca.datatypes.network.PortSpec type.'''

    SHORTNAME = 'PortSpec'
    TYPE_URI = 'tosca.datatypes.network.' + SHORTNAME

    PROPERTY_NAMES = (
        PROTOCOL, SOURCE, SOURCE_RANGE,
        TARGET, TARGET_RANGE
    ) = (
        'protocol', 'source', 'source_range',
        'target', 'target_range'
    )

    # TODO(TBD) May want to make this a subclass of DataType
    # and change init method to set PortSpec's properties
    def __init__(self):
        pass

    # The following additional requirements MUST be tested:
    # 1) A valid PortSpec MUST have at least one of the following properties:
    #   target, target_range, source or source_range.
    # 2) A valid PortSpec MUST have a value for the source property that
    #    is within the numeric range specified by the property source_range
    #    when source_range is specified.
    # 3) A valid PortSpec MUST have a value for the target property that is
    #    within the numeric range specified by the property target_range
    #    when target_range is specified.
    @staticmethod
    def validate_additional_req(properties, prop_name, custom_def=None, ):
        try:
            source = properties.get(PortSpec.SOURCE)
            source_range = properties.get(PortSpec.SOURCE_RANGE)
            target = properties.get(PortSpec.TARGET)
            target_range = properties.get(PortSpec.TARGET_RANGE)

            # verify one of the specified values is set
            if source is None and source_range is None and \
                    target is None and target_range is None:
                ExceptionCollector.appendException(
                    InvalidTypeAdditionalRequirementsError(
                        type=PortSpec.TYPE_URI))
            # Validate source value is in specified range
            if source and source_range:
                validateutils.validate_value_in_range(source, source_range,
                                                      PortSpec.SOURCE)
            else:
                from toscaparser.dataentity import DataEntity
                portdef = DataEntity('PortDef', source, None, PortSpec.SOURCE)
                portdef.validate()
            # Validate target value is in specified range
            if target and target_range:
                validateutils.validate_value_in_range(target, target_range,
                                                      PortSpec.TARGET)
            else:
                from toscaparser.dataentity import DataEntity
                portdef = DataEntity('PortDef', source, None, PortSpec.TARGET)
                portdef.validate()
        except Exception:
            msg = _('"%(value)s" do not meet requirements '
                    'for type "%(type)s".') \
                % {'value': properties, 'type': PortSpec.SHORTNAME}
            ExceptionCollector.appendException(
                ValueError(msg))
