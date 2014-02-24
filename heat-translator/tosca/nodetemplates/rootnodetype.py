from yaml_loader import Loader
import os

nodetype_def_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + "nodetypesdef.yaml"
nodetype_def = Loader(nodetype_def_file).load()

class RootNodeType(object):
    def __init__(self):
        self.nodetypes = self._set_nodetypes()

        '''set a list of node names from the nodetype definition'''
    def _set_nodetypes(self):
        nodetypes = []
        if isinstance(nodetype_def, dict):
            for key in nodetype_def.iterkeys():
                nodetypes.append(key)
        return nodetypes
    
    def get_nodetype(self, nodetype=None):
        rtype = {}
        if nodetype == None:
            nodetype = self.nodetype
        ntype = nodetype
        ntype = ntype.replace(".", "_")
        if ntype in self.nodetypes:
            rtype = nodetype_def[ntype]
        return rtype

class RootRelationshipType(object):
    def __init__(self):
        pass  