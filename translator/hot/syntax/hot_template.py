#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import OrderedDict
import textwrap
import yaml


class HotTemplate(object):
    '''Container for full Heat Orchestration template.'''

    SECTIONS = (VERSION, DESCRIPTION, PARAMETER_GROUPS, PARAMETERS,
                RESOURCES, OUTPUTS, MAPPINGS) = \
               ('heat_template_version', 'description', 'parameter_groups',
                'parameters', 'resources', 'outputs', '__undefined__')

    VERSIONS = (LATEST,) = ('2013-05-23',)

    def __init__(self):
        self.resources = []
        self.outputs = []
        self.parameters = []
        self.description = ""

    def represent_ordereddict(self, dumper, data):
        nodes = []
        for key, value in data.items():
            node_key = dumper.represent_data(key)
            node_value = dumper.represent_data(value)
            nodes.append((node_key, node_value))
        return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', nodes)

    def output_to_yaml(self):
        dict_output = OrderedDict()
        # Version
        version_string = self.VERSION + ": " + self.LATEST + "\n\n"

        # Description
        desc_str = ""
        if self.description:
            # Wrap the text to a new line if the line exceeds 80 characters.
            wrapped_txt = "\n  ".join(textwrap.wrap(self.description, 80))
            desc_str = self.DESCRIPTION + ": >\n  " + wrapped_txt + "\n\n"

        # Parameters
        all_params = OrderedDict()
        for parameter in self.parameters:
            all_params.update(parameter.get_dict_output())
        dict_output.update({self.PARAMETERS: all_params})

        # Resources
        all_resources = OrderedDict()
        for resource in self.resources:
            if not resource.hide_resource:
                all_resources.update(resource.get_dict_output())
        dict_output.update({self.RESOURCES: all_resources})

        # Outputs
        all_outputs = OrderedDict()
        for output in self.outputs:
            all_outputs.update(output.get_dict_output())
        dict_output.update({self.OUTPUTS: all_outputs})

        yaml.add_representer(OrderedDict, self.represent_ordereddict)
        yaml_string = yaml.dump(dict_output, default_flow_style=False)
        # get rid of the '' from yaml.dump around numbers
        yaml_string = yaml_string.replace('\'', '')
        return version_string + desc_str + yaml_string
