from rootnodetype import RootNodeType

class NodeType(RootNodeType):
    def __init__(self, nodetype): 
        super(NodeType, self).__init__()
        self.nodetype = nodetype
    
    ''' get properties for a given node type'''
    def get_properties(self):
        properties = []
        nodetype = self.get_nodetype()
        for prop_key, prop_vale in nodetype.iteritems():
            if prop_key == 'properties':
                properties = prop_vale
        return properties
    
    ''' get capabilities for a given node type'''
    def get_capabilities(self):
        pass
    
    def derived_from(self):
        pass
    
    def set_requirements(self):
        pass
    
    def get_requirements(self):
        return self.requirements()
    