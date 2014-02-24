from tosca.inputs import Input
from tosca.nodetemplates.node_template import NodeTemplate

class ToscaValidator():
    def __init__(self, Tosca):
        self.inputs = Tosca.get_inputs()
        self.nodetemplates = Tosca.get_nodetemplates()
        self.tosca = Tosca
        
    def validate(self):
        #validate inputs
        for name, attrs in self.inputs.iteritems():
            if not isinstance(attrs, dict):
                print ("The input %s has no attributes", name)
            Input(name, attrs).validate() 
        
        #validate node templates
        for nodetemplate, value in self.nodetemplates.iteritems():
            NodeTemplate(nodetemplate, value, self.tosca).validate()
    