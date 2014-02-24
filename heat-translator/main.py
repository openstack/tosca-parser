#!/usr/bin/env python

import exit
import os
import sys
from source import Source
from tosca.translate import TOSCATranslator
from tosca.tosca_profile import Tosca
from tosca.validate import ToscaValidator


def main():
    sourcetype = sys.argv[1]
    path = sys.argv[2]
    #sourcetype = "tosca"
    #path = "/heat-translator/tosca/tests/tosca.yaml"
    if not sourcetype:
        print("Translation type is needed. For example, 'tosca'")
    if not path.endswith(".yaml"):
        print "Only YAML file is supported at this time."
        
    if os.path.isdir(path):
        print('Translation of directory is not supported at this time : %s' % path)
    elif os.path.isfile(path):
        heat_tpl = translate(sourcetype, path)
        exit.write_output(heat_tpl)
    else:
        print('%s is not a valid file.' % path)

def translate(sourcetype, path):
    tpl = Source(path)
    if sourcetype == "tosca":
        tosca = Tosca(tpl)
        ToscaValidator(tosca).validate()
        return TOSCATranslator(tosca).translate()

if __name__ == '__main__':
    main()
