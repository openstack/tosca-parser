from rootnodetype import RootRelationshipType

class RelatonshipType(RootRelationshipType):
    def __init__(self, relatointype): 
        super(RelatonshipType, self).__init__()
        self.nodetype = relatointype