===============
Heat-Translator
===============

Tool to translate non-heat templates to Heat Orchestration Template (HOT).

Overview
--------

Heat-Translator is an Openstack project and licensed under Apache 2. It is a
command line tool which takes non-Heat templates as an input and produces a
Heat Orchestration Template (HOT) which can be deployed by Heat. Currently the
development and testing is done with an aim to translate OASIS Topology and
Orchestration Specification for Cloud Applications (TOSCA) templates to
HOT. However, the tool is designed to be easily extended to use with any
format other than TOSCA.

Architecture
------------

Heat-Translator project is mainly built of two components:

1. **Parser** - parser for a particular template format e.g. TOSCA parser

2. **Generator** - takes an in-memory graph from **Parser**, maps it to Heat resources and software configuration and then produces a HOT.

How To Use
**********
Please refer to `doc/source/usage.rst <https://github.com/openstack/heat-translator/blob/master/doc/source/usage.rst>`_

Directory Structure
*******************

Three main directories related to the heat-translator are:

1. toscalib: It is TOSCA parser for TOSCA Simple Profile YAML. It validates tosca input file and creates an in memory graphs.
2. hot: It is the generator, that has logic of converting TOSCA in memory graph to HOT yaml files.
3. common: It has all the file that can support the execution of parser and generator.

Project Info
------------

* License: Apache License, Version 2.0
* Documentation: http://docs.openstack.org/developer/heat-translator/
* Launchpad: https://launchpad.net/heat-translator
* Blueprints: https://blueprints.launchpad.net/heat-translator
* Bugs: https://bugs.launchpad.net/heat-translator
* Source: http://git.openstack.org/cgit/openstack/heat-translator/
* IRC Channel: #openstack-heat-translator
