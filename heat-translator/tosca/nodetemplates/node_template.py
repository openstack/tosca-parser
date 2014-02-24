from properties import Property
from tosca.nodetemplates.schema import Schema
from tosca.inputs import InputParameters
from tosca.inputs import Input
from tosca.nodetemplates.node_templates import NodeTemplates

class NodeTemplate(object):
    def __init__(self, name, nodetemplate, tosca):
        self.name = name
        self.nodetemplate = nodetemplate
        self.tosca = tosca
    
    def get_node(self):
        return self.nodetemplate
    
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.nodetemplate['type']
    
    def get_properties(self):
        return self.nodetemplate['properties']
    
    def validate(self):
        self.validate_prpoerties()
        self.validate_type()
        
    #TODO
    def validate_type(self):
        pass
    
    #TODO
    def validate_relationship(self):
        pass
    
    def validate_prpoerties(self):
        '''validate that required properties for a particular nodetype is provided and matches constraints'''
        nodetype = self.get_type()
        required_props = Schema(nodetype).required()
        for req in required_props:
            if req not in self.get_properties():
                raise ValueError('Missing required property %s' %req)
        for prop, val in self.get_properties().iteritems():
            if isinstance(val, dict):
                for key, value in val.iteritems():           
                    if key == "get_input":
                        val = self.get_input_ref(value)
                        break
                    if key == "get_property":
                        val = self.get_property_ref(value, self.tosca)
            if val is not None:
                Property(prop, self.get_type(), val).validate()
            
    def get_input_ref(self, ref):
        ''' get input reference, for example, get_input: db_user '''
        input_val = self.tosca.get_inputs()[ref]
        if Input(ref, input_val).has_default():
            return Input(ref, input_val).get_default()
    
    @classmethod
    def get_property_ref(cls, ref, t):
        ''' get property reference, for example, get_property: [ mysql, db_user ] '''
        item = ref[0]
        n = t.get_nodetemplates()[item]
        c = cls(item, n, t)
        for val in c.get_properties().itervalues():
            if isinstance(val, dict):
                for key, value in val.iteritems():           
                    if key == "get_input":
                        return c.get_input_ref(value)
        
    def get_relationship(self):
        return self.nodetemplate['requirements']
    
    def get_hostedOn_relationship(self):
        hosted = []
        r = self.get_relationship()
        for key, value in r.iteritems():
            if key == "host":
                hosted.append(value)
        return hosted
    
    def get_dependsOn_relationship(self):
        depends = []
        r = self.get_relationship()
        for key, value in r.iteritems():
            if key == "dependency":
                depends.append(value)
        return depends
    
    def get_connectedTo_relationship(self):
        connected = []
        r = self.get_relationship()
        for key, value in r.iteritems():
            if key == "database":
                connected.append(value)
        return connected
    
    def is_hostedOn(self):
        pass
    
    def is_dependsOn(self):
        pass
    
    def is_connectedTo(self):
        pass
    
    def get_interfaces(self):
        return self.nodetemplate['interfaces']

    def get_interface_inputs(self, interface):
        i = self.get_interfaces()
        for key, value in i.iteritems():
            if key == interface:
                return value
            