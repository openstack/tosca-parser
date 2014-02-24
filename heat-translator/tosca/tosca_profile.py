SECTIONS = (VERSION, DESCRIPTION, INPUTS,
            NODE_TEMPLATES, OUTPUTS) = \
           ('tosca_definitions_version', 'description', 'inputs',
            'node_templates', 'outputs')

class Tosca(object):
    
    def __init__(self, sourcedata):
        self.sourcedata = sourcedata

    def get_version(self):
        return self.sourcedata[VERSION]

    def get_description(self):
        return self.sourcedata[DESCRIPTION]
    
    def get_inputs(self):
        return self.sourcedata[INPUTS]

    def get_nodetemplates(self):
        return self.sourcedata[NODE_TEMPLATES]

    def get_outputs(self):
        return self.sourcedata[OUTPUTS]