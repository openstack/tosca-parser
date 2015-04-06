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
2. **Generator** - takes an in-memory graph from **Parser**, maps it to Heat
resources and software configuration and then produces a HOT.

Project Info
------------

* Free software: Apache license
* Documentation: http://heat-translator.readthedocs.org/
* Launchpad: https://launchpad.net/heat-translator
* Blueprints: https://blueprints.launchpad.net/heat-translator
* Bugs: https://bugs.launchpad.net/heat-translator
* Source Code: https://github.com/openstack/heat-translator/
