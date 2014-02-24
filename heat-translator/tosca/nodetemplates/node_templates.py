from tosca.tosca_profile import Tosca

class NodeTemplates(object):
    
    def __init__(self, nodetemplates):
        self.nodetemplates = nodetemplates
    
    def __contains__(self, key):
        return key in self.nodetemplates

    def __iter__(self):
        return iter(self.nodetemplates)

    def __len__(self):
        return len(self.nodetemplates)

    def __getitem__(self, key):
        '''Get a node template value.'''
        return self.nodetemplates[key]