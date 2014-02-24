from yaml_loader import Loader
import os

schema_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + "nodetypeschema.yaml"
schema = Loader(schema_file).load()

class Schema(object):
    
    TYPES = (
        INTEGER,
        STRING, NUMBER, BOOLEAN,
        LIST
    ) = (
        'integer',
        'string', 'number', 'boolean',
        'list'
    )
    
    KEYS = (
        TYPE, DESCRIPTION, DEFAULT, CONSTRAINTS,
    ) = (
        'type', 'description', 'default', 'constraints'
    )
                    
    def __init__(self, nodetype): 
        self.nodetype = nodetype
        self.nodes = self._set_nodes()
    
        '''set a list of node names from the schema'''
    def _set_nodes(self):
        sections = []
        if isinstance(schema, dict):
            for key in schema.iterkeys():
                sections.append(key)
        return sections
    
    def _get_section(self, section_name):
        section = {}
        if section_name in self.nodes:
            return schema[section_name]
        return section
    
    ''' return true if property is a required for a given node '''
    def is_required(self, property_name):
        return property_name in self.required()
    
    ''' get schemata for a given node type'''
    def get_schemata(self):
        ntype = self.nodetype
        ntype = ntype.replace(".", "_")
        return self._get_section(ntype)
    
    ''' get schema for a given property'''
    def get_schema(self, property_name):
        schema = {}
        schemata = self.get_schemata()
        for prop_key, prop_vale in schemata.iteritems():
            if prop_key == property_name:
                for attr, value in prop_vale.iteritems():
                    schema[attr] = value
        return schema
    
    def get_type(self, property_name):
        return self.get_schema(property_name)['type']
    
    def get_constraints(self, property_name):
        s = self.get_schema(property_name)
        if 'constraints' in s:
            s['constraints']
    
    def get_description(self, property_name):
        return self.get_schema(property_name)['description']   
    
    def get_greater_or_equal(self, property_name):
        pass
    
    def get_equal(self, property_name):
        pass
                
    ''' list all the required properties for a given nodetype '''
    def required(self):
        required = []
        schemata = self.get_schemata()
        for prop_key, prop_vale in schemata.iteritems():
            for attr, value in prop_vale.iteritems():
                if attr == 'required' and value:
                    required.append(prop_key)
        return required