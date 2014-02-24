import yaml

HEAT_VERSIONS = '2013-05-23'

if hasattr(yaml, 'CSafeDumper'):
    yaml_dumper = yaml.CSafeDumper
else:
    yaml_dumper = yaml.SafeDumper

yaml_tpl = {}

class TOSCATranslator(object):
    def __init__(self, tosca):
        super(TOSCATranslator, self).__init__()
        self.tosca = tosca
 
    def translate(self):
        self._translate_version()
        self._translate_inputs()
        self._translate_node_templates()
        self._translate_outputs()

    def _translate_version(self):
        pass
    
    def _translate_inputs(self):
        pass
    
    def _translate_node_templates(self):
        pass
            
    def _translate_outputs(self):
        pass
    