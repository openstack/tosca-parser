import yaml

if hasattr(yaml, 'CSafeLoader'):
    yaml_loader = yaml.CSafeLoader
else:
    yaml_loader = yaml.SafeLoader
    

class Loader(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def load(self):
        f = open(self.file_name, 'r')
        profile = f.read() # string
        try:
            doc = yaml.load(profile, Loader=yaml_loader)
        except yaml.YAMLError as error:
            raise ValueError(error)
        return doc