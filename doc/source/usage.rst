=====
Usage
=====

Heat-Translator project is planned to be made available via python-heatclient.

For now, it can be tested on the command line as below::

    git clone https://github.com/openstack/heat-translator
    python heat_translator.py --template-file==<path to the YAML template> --template-type=<type of template e.g. tosca> --parameters="purpose=test"

The heat_translator.py test program is at the root level of the project. The program has currently tested with TOSCA templates.
It requires two arguments::

1. Path to the file that needs to be translated
2. Type of translation (e.g. tosca)

An optional argument can be provided to handle user inputs parameters.

For example, a TOSCA hello world template can be translated by running the following command from the directory where you have cloned the project::

    python heat_translator.py --template-file=translator/toscalib/tests/data/tosca_helloworld.yaml --template-type=tosca

This should produce a translated Heat Orchestration Template on the command line. In the near future, new options will be added to save the output
to a file. When deploy the translated template with Heat, please keep in mind that you have image registered in the Glance. The Heat-Translator
project sets flavor and image from a pre-defined set of values (as listed in /home/openstack/heat-translator/translator/hot/tosca/tosca_compute.py)
with the best possible match to the constraints defined in the TOSCA template. If there is no possible match found, a null value is set for now.
Per the future plan, an image and flavor will be provided from an online repository.

Once the project is made available in python-heatclient, it will be enabled to deploy translated output template seamlessly via Heat.

