# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 VEXXHOST, Inc.
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

import setuptools
import distutils.command.install

import cloudagent

setuptools.setup(
    name='CloudAgent',
    version=cloudagent.__version__,
    author='VEXXHOST, Inc.',
    author_email='support@vexxhost.com',
    packages=['cloudagent', 'cloudagent.drivers'],
    scripts=['bin/cloudagent', 'bin/cloudagent-setup'],
    url='http://pypi.python.org/pypi/CloudAgent/',
    license='LICENSE',
    description='OpenStack Cloud Server Agent',
    data_files=[('init-scripts', ['init-scripts/debian'])],
    install_requires=[
        "https://github.com/mitsuhiko/jinja2/archive/2.6.tar.gz#egg=Jinja2-2.6",
        "pyserial",
    ],
)
