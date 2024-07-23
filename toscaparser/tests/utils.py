# Copyright (C) 2024 Fujitsu
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import os


def get_sample_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '../../samples'))


def get_sample_test_dir():
    # {tosca-parser}/samples/tests
    return os.path.join(get_sample_dir(), 'tests')


def get_sample_test_path(*p):
    return os.path.join(get_sample_test_dir(), *p)
