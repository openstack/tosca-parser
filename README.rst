========================
Team and repository tags
========================

.. image:: http://governance.openstack.org/badges/tosca-parser.svg
    :target: http://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

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

The TOSCA Parser takes TOSCA YAML template or TOSCA Cloud Service Archive (CSAR)
file as an input, with optional input of dictionary of needed parameters with their
values, and produces in-memory objects of different TOSCA elements with their
relationship to each other. It also creates a graph of TOSCA node templates and their
relationship.

The ToscaTemplate class located in the toscaparser/tosca_template.py is an entry
class of the parser and various functionality of parser can be used by initiating
this class. In order to see an example usage of TOSCA Parser from a separate tool,
refer to the OpenStack heat-translator class TranslateTemplate located in the
translator/osc/v1/translate.py module. The toscaparser/shell.py module of tosca-parser
also provides a good reference on how to invoke TOSCA Parser from Command Line Interface.

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
* Source: https://opendev.org/openstack/tosca-parser/

