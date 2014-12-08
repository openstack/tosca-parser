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


from translator.toscalib.common.exception import MissingRequiredFieldError
from translator.toscalib.common.exception import UnknownFieldError
from translator.toscalib.elements.capabilitytype import CapabilityTypeDef
from translator.toscalib.elements.interfaces import InterfacesDef
from translator.toscalib.elements.nodetype import NodeType
from translator.toscalib.elements.relationshiptype import RelationshipType
from translator.toscalib.properties import Property


class EntityTemplate(object):
    '''Base class for TOSCA templates.'''

    SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
                INTERFACES, CAPABILITIES, TYPE) = \
               ('derived_from', 'properties', 'requirements', 'interfaces',
                'capabilities', 'type')

    def __init__(self, name, template, entity_name, custom_def=None):
        self.name = name
        self.entity_tpl = template
        self.custom_def = custom_def
        self._validate_field(self.entity_tpl)
        if entity_name == 'node_type':
            self.type_definition = NodeType(self.entity_tpl['type'],
                                            custom_def)
        if entity_name == 'relationship_type':
            self.type_definition = RelationshipType(self.entity_tpl['type'],
                                                    custom_def)
        self._properties = None
        self._interfaces = None
        self._requirements = None
        self._capabilities = None

    @property
    def type(self):
        return self.type_definition.type

    @property
    def requirements(self):
        if self._requirements is None:
            self._requirements = self.type_definition.get_value(
                self.REQUIREMENTS,
                self.entity_tpl) or []
        return self._requirements

    @property
    def properties(self):
        if self._properties is None:
            self._properties = self._create_properties()
        return self._properties

    @property
    def interfaces(self):
        if self._interfaces is None:
            self._interfaces = self._create_interfaces()
        return self._interfaces

    @property
    def capabilities(self):
        if not self._capabilities:
            self._capabilities = self._create_capabilities()
        return self._capabilities

    def _create_capabilities(self):
        capability = []
        properties = {}
        cap_type = None
        caps = self.type_definition.get_value(self.CAPABILITIES,
                                              self.entity_tpl)
        if caps:
            for name, value in caps.items():
                for val in value.values():
                    properties = val
                for c in self.type_definition.capabilities:
                    if c.name == name:
                        cap_type = c.type
                cap = CapabilityTypeDef(name, cap_type,
                                        self.name, properties)
                capability.append(cap)
        return capability

    def _validate_properties(self, template, entitytype):
        properties = entitytype.get_value(self.PROPERTIES, template)
        allowed_props = []
        required_props = []
        for p in entitytype.properties_def:
            allowed_props.append(p.name)
            if p.required:
                required_props.append(p.name)
        if properties:
            self._common_validate_field(properties, allowed_props,
                                        'Properties')
            # make sure it's not missing any property required by a tosca type
            missingprop = []
            for r in required_props:
                if r not in properties.keys():
                    missingprop.append(r)
            if missingprop:
                raise MissingRequiredFieldError(
                    what='Properties of template %s' % self.name,
                    required=missingprop)
        else:
            if required_props:
                raise MissingRequiredFieldError(
                    what='Properties of template %s' % self.name,
                    required=missingprop)

    def _validate_capabilities(self):
        type_capabilities = self.type_definition.capabilities
        allowed_caps = []
        if type_capabilities:
            for tcap in type_capabilities:
                allowed_caps.append(tcap.name)
        capabilities = self.type_definition.get_value(self.CAPABILITIES,
                                                      self.entity_tpl)
        if capabilities:
            self._common_validate_field(capabilities, allowed_caps,
                                        'Capabilities')

    def _validate_field(self, template):
        if not isinstance(template, dict):
            raise MissingRequiredFieldError(
                what='Template %s' % self.name, required=self.TYPE)
        try:
            template[self.TYPE]
        except KeyError:
            raise MissingRequiredFieldError(
                what='Template %s' % self.name, required=self.TYPE)

    def _common_validate_field(self, schema, allowedlist, section):
        for name in schema:
            if name not in allowedlist:
                raise UnknownFieldError(
                    what='%(section)s of template %(nodename)s'
                    % {'section': section, 'nodename': self.name},
                    field=name)

    def _create_properties(self):
        props = []
        properties = self.type_definition.get_value(self.PROPERTIES,
                                                    self.entity_tpl) or {}
        for name, value in properties.items():
            for p in self.type_definition.properties_def:
                if p.name == name:
                    prop = Property(name, value, p.schema)
                    props.append(prop)
        for p in self.type_definition.properties_def:
            if p.default is not None and p.name not in properties.keys():
                prop = Property(p.name, p.default, p.schema)
                props.append(prop)
        return props

    def _create_interfaces(self):
        interfaces = []
        type_interfaces = self.type_definition.get_value(self.INTERFACES,
                                                         self.entity_tpl)
        if type_interfaces:
            for interface_type, value in type_interfaces.items():
                for op, op_def in value.items():
                    iface = InterfacesDef(self.type_definition,
                                          interfacetype=interface_type,
                                          node_template=self,
                                          name=op,
                                          value=op_def)
                    interfaces.append(iface)
        return interfaces
