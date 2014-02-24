from yaml_loader import Loader

class Source(object):
    def __init__(self, path):
        self.profile = Loader(path).load()
            
    def __contains__(self, key):
        return key in self.profile

    def __iter__(self):
        return iter(self.profile)

    def __len__(self):
        return len(self.profile)

    def __getitem__(self, key):
        '''Get a section.'''
        return self.profile[key]
