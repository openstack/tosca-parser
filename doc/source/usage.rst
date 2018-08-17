=====
Usage
=====

The TOSCA Parser can be used as a library by any client program, for example,
OpenStack heat-translator uses it to translate TOSCA to Heat Orchestration
Template (HOT).

For an easy reference on how TOSCA Parser can be used programmatically or to
test that the a TOSCA template passes validation, refer to the tosca_parser.py
test program which is located at the root level of the project. Alternatively,
you can install 0.3.0 or higher PyPI release of TOSCA-Parser as available at the
https://pypi.python.org/project/tosca-parser and test use the parser via CLI
entry point as::

    tosca-parser --template-file=toscaparser/tests/data/tosca_helloworld.yaml

The value to the --template-file is required to be a relative or an absolute path.

Custom template versions can be created and supported outside of TOSCA Parser
using the toscaparser.extensions namespace.  See the NFV and MEC extensions
for examples of how to define custom template definitions and versions.
