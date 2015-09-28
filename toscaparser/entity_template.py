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

from toscaparser.capabilities import Capability
from toscaparser.common.exception import MissingRequiredFieldError
from toscaparser.common.exception import UnknownFieldError
from toscaparser.common.exception import ValidationError
from toscaparser.elements.interfaces import InterfacesDef
from toscaparser.elements.nodetype import NodeType
from toscaparser.elements.relationshiptype import RelationshipType
from toscaparser.properties import Property


class EntityTemplate(object):
    '''Base class for TOSCA templates.'''

    SECTIONS = (DERIVED_FROM, PROPERTIES, REQUIREMENTS,
                INTERFACES, CAPABILITIES, TYPE, DESCRIPTION, DIRECTIVES,
                ATTRIBUTES, ARTIFACTS, NODE_FILTER, COPY) = \
               ('derived_from', 'properties', 'requirements', 'interfaces',
                'capabilities', 'type', 'description', 'directives',
                'attributes', 'artifacts', 'node_filter', 'copy')
    REQUIREMENTS_SECTION = (NODE, CAPABILITY, RELATIONSHIP, OCCURRENCES) = \
                           ('node', 'capability', 'relationship',
                            'occurrences')
    # Special key names
    SPECIAL_SECTIONS = (METADATA) = ('metadata')

    def __init__(self, name, template, entity_name, custom_def=None):
        self.name = name
        self.entity_tpl = template
        self.custom_def = custom_def
        self._validate_field(self.entity_tpl)
        if entity_name == 'node_type':
            self.type_definition = NodeType(self.entity_tpl['type'],
                                            custom_def)
        if entity_name == 'relationship_type':
            relationship = template.get('relationship')
            type = None
            if relationship and isinstance(relationship, dict):
                type = relationship.get('type')
            elif isinstance(relationship, str):
                type = self.entity_tpl['relationship']
            else:
                type = self.entity_tpl['type']
            self.type_definition = RelationshipType(type,
                                                    None, custom_def)
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

    def get_properties_objects(self):
        '''Return properties objects for this template.'''
        if self._properties is None:
            self._properties = self._create_properties()
        return self._properties

    def get_properties(self):
        '''Return a dictionary of property name-object pairs.'''
        return {prop.name: prop
                for prop in self.get_properties_objects()}

    def get_property_value(self, name):
        '''Return the value of a given property name.'''
        props = self.get_properties()
        if props and name in props.keys():
            return props[name].value

    @property
    def interfaces(self):
        if self._interfaces is None:
            self._interfaces = self._create_interfaces()
        return self._interfaces

    def get_capabilities_objects(self):
        '''Return capabilities objects for this template.'''
        if not self._capabilities:
            self._capabilities = self._create_capabilities()
        return self._capabilities

    def get_capabilities(self):
        '''Return a dictionary of capability name-object pairs.'''
        return {cap.name: cap
                for cap in self.get_capabilities_objects()}

    def is_derived_from(self, type_str):
        '''Check if object inherits from the given type.

        Returns true if this object is derived from 'type_str'.
        False otherwise.
        '''
        if not self.type:
            return False
        elif self.type == type_str:
            return True
        elif self.parent_type:
            return self.parent_type.is_derived_from(type_str)
        else:
            return False

    def _create_capabilities(self):
        capability = []
        caps = self.type_definition.get_value(self.CAPABILITIES,
                                              self.entity_tpl)
        if caps:
            for name, props in caps.items():
                capabilities = self.type_definition.get_capabilities()
                if name in capabilities.keys():
                    c = capabilities[name]
                    cap = Capability(name, props['properties'], c)
                    capability.append(cap)
        return capability

    def _validate_properties(self, template, entitytype):
        properties = entitytype.get_value(self.PROPERTIES, template)
        self._common_validate_properties(entitytype, properties)

    def _validate_capabilities(self):
        type_capabilities = self.type_definition.get_capabilities()
        allowed_caps = \
            type_capabilities.keys() if type_capabilities else []
        capabilities = self.type_definition.get_value(self.CAPABILITIES,
                                                      self.entity_tpl)
        if capabilities:
            self._common_validate_field(capabilities, allowed_caps,
                                        'Capabilities')
            self._validate_capabilities_properties(capabilities)

    def _validate_capabilities_properties(self, capabilities):
        for cap, props in capabilities.items():
            capabilitydef = self.get_capability(cap).definition
            self._common_validate_properties(capabilitydef,
                                             props[self.PROPERTIES])

            # validating capability properties values
            for prop in self.get_capability(cap).get_properties_objects():
                prop.validate()

                # TODO(srinivas_tadepalli): temporary work around to validate
                # default_instances until standardized in specification
                if cap == "scalable" and prop.name == "default_instances":
                    prop_dict = props[self.PROPERTIES]
                    min_instances = prop_dict.get("min_instances")
                    max_instances = prop_dict.get("max_instances")
                    default_instances = prop_dict.get("default_instances")
                    if not (min_instances <= default_instances
                            <= max_instances):
                        err_msg = ("Properties of template %s : "
                                   "default_instances value is not"
                                   " between min_instances and "
                                   "max_instances" % self.name)
                        raise ValidationError(message=err_msg)

    def _common_validate_properties(self, entitytype, properties):
        allowed_props = []
        required_props = []
        for p in entitytype.get_properties_def_objects():
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

    def _validate_field(self, template):
        if not isinstance(template, dict):
            raise MissingRequiredFieldError(
                what='Template %s' % self.name, required=self.TYPE)
        try:
            relationship = template.get('relationship')
            if relationship and not isinstance(relationship, str):
                relationship[self.TYPE]
            elif isinstance(relationship, str):
                template['relationship']
            else:
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
            props_def = self.type_definition.get_properties_def()
            if props_def and name in props_def:
                prop = Property(name, value,
                                props_def[name].schema, self.custom_def)
                props.append(prop)
        for p in self.type_definition.get_properties_def_objects():
            if p.default is not None and p.name not in properties.keys():
                prop = Property(p.name, p.default, p.schema, self.custom_def)
                props.append(prop)
        return props

    def _create_interfaces(self):
        interfaces = []
        type_interfaces = None
        if isinstance(self.type_definition, RelationshipType):
            if isinstance(self.entity_tpl, dict):
                for rel_def, value in self.entity_tpl.items():
                    if rel_def != 'type':
                        rel_def = self.entity_tpl.get(rel_def)
                        rel = None
                        if isinstance(rel_def, dict):
                            rel = rel_def.get('relationship')
                        if rel:
                            if self.INTERFACES in rel:
                                type_interfaces = rel[self.INTERFACES]
                                break
        else:
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

    def get_capability(self, name):
        """Provide named capability

        :param name: name of capability
        :return: capability object if found, None otherwise
        """
        caps = self.get_capabilities()
        if caps and name in caps.keys():
            return caps[name]
