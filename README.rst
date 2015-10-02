===============
TOSCA Parser
===============

Overview
--------

The TOSCA Parser is an OpenStack project and licensed under Apache 2. It is
developed to parse TOSCA Simple Profile in YAML. It reads the TOSCA templates
and creates an in-memory graph of TOSCA nodes and their relationship.

Architecture
------------

The TOSCA Parser takes TOSCA YAML template as an input, with optional input of
dictionary of needed parameters with their values, and produces in-memory
objects of different TOSCA elements with their relationship to each other. It
also creates a graph of TOSCA node templates and their relationship. The support
for parsing template within TOSCA CSAR is under development.

The ToscaTemplate class located in the toscaparser/tosca_template.py is an entry
class of the parser and various functionality of parser can be used by initiating
this class. In order to see an example usage, refer to the heat-translator
class TranslateTemplate located in the translator/osc/v1/translate.py module.

The toscaparser/elements sub-directory contains various modules to handle
various TOSCA type elements like node type, relationship type etc. The
entity_type.py module is a parent of all type elements. The toscaparser
directory contains various python module to handle service template including
topology template, node templates, relationship templates etc. The
entity_template.py is a parent of all template elements.


How To Use
----------
Please refer to `doc/source/usage.rst <https://github.com/openstack/tosca-parser/blob/master/doc/source/usage.rst>`_

Project Info
------------

* License: Apache License, Version 2.0
* Source: http://git.openstack.org/cgit/openstack/tosca-parser/

