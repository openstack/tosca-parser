from tosca.nodetemplates.schema import Schema
from tosca.nodetemplates.constraints import Constraint

class InputParameters(object):
    def __init__(self, inputs):
        self.inputs = inputs

    def __contains__(self, key):
        return key in self.inputs

    def __iter__(self):
        return iter(self.inputs)

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, key):
        '''Get a input value.'''
        return self.inputs[key]

class Input(object):
                    
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
    
    def get_type(self):
        return self.schema['type']
    
    def get_description(self):
        if self.has_default():
            return self.schema['description']
        return ''
    
    def get_default(self):
        if self.has_default():
            return self.schema['default']
        return ''
    
    def get_constraints(self):
        return self.schema['constraints']
    
    def has_default(self):
        '''Return whether the parameter has a default value.'''
        return Schema.DEFAULT in self.schema

    def has_description(self):
        '''Return whether the parameter has a default value.'''
        return Schema.DESCRIPTION in self.schema
        
    def validate(self):
        self.validate_type(self.get_type())
        self.validate_constraints(self.get_constraints())
        
    def validate_type(self, input_type):
        if input_type not in Schema.TYPES:
            raise ValueError('Invalid type %s' % type)
    
    def validate_constraints(self, constraints):
        for constraint in constraints:
            for key in constraint.keys():
                if key not in Constraint.CONSTRAINTS:
                    raise ValueError('Invalid constraint %s' % constraint)
                if isinstance(key, dict): #and is_required to have a min or max or in certain range or equal to something etc.
                    pass
    