README:

This CSAR contains all definitions that are required for deploying WordPress
and MySQL on a single compute instance.

Entry information for processing through an orchestrator is contained in file
TOSCA-Metadata/TOSCA.meta. This file provides high-level information such as
CSAR version or creator of the CSAR. Furthermore, it provides pointers to the
various TOSCA definitions files that contain the real details.
The entry 'Entry-Definitions' points to the definitions file which holds the
service template for the workload.
'Entry-Definitions' is optional. An orchestrator can also process the contents
like this:
1) Read in and process each definitions file.
2) For each definitions file:
  2.1) Read in all * type definitions (node types, capability types, etc.) and
       store them in an internal map
3) Verify and build dependencies (e.g. inheritance) between all type definitions
   previously read in. Orchestrator built-in types (e.g. TOSCA base types) are
   also considered in this step.
4) Process the actual service template (the file with a node_templates section).
   Validate using previously obtained type information.
