.. tosca-parser documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tosca-parser's documentation!
========================================

The TOSCA Parser is developed to parse TOSCA Simple Profile in YAML. It reads
the TOSCA templates and creates an in-memory graph of TOSCA nodes and their
relationship.

The TOSCA Parser can also be used for parsing TOSCA Simple Profile for Network
Functions Virtualization (NFV). The work to provide such a support was started
with the release of TOSCA Parser 0.4.0 PyPI release and it is ongoing.
The TOSCA Simple Profile for NFV can be accessed by using TOSCA version
"tosca_simple_profile_for_nfv_1_0_0" in the template.

The TOSCA Parser now supports profile definition extensions that can be
accessed via a custom tosca_definitions_version.  Extensions can be added by
creating a module in the "toscaparser/extensions" directory.  See the "nfv"
module for an example.

Contents:
---------

.. toctree::
   :maxdepth: 2

   installation
   usage
   contributing

For Contributors
================

* If you are a new contributor to tosca-parser please refer: :doc:`contributor/contributing`

  .. toctree::
     :hidden:

     contributor/contributing

Indices and tables
------------------

* :ref:`genindex`
* :ref:`search`
