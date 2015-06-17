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

import distutils.command.install
import platform
import setuptools

import cloudagent

if platform.system() == 'Windows':
    import py2exe
    # ModuleFinder can't handle runtime changes to __path__, but win32com uses them
    try:
        # py2exe 0.6.4 introduced a replacement modulefinder.
        # This means we have to add package paths there, not to the built-in
        # one.  If this new modulefinder gets integrated into Python, then
        # we might be able to revert this some day.
        # if this doesn't work, try import modulefinder
        try:
            import py2exe.mf as modulefinder
        except ImportError:
            import modulefinder
        import win32com, sys
        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath("win32com", p)
        for extra in ["win32com.adsi"]: #,"win32com.mapi"
            __import__(extra)
            m = sys.modules[extra]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(extra, p)
    except ImportError:
        # no build path setup, no worries.
        pass

win_service = dict(
    description="OpenStack Cloud Server Agent",
    modules=["AgentService"],
)

requirements = [
    "Jinja2==2.6",
    "pyserial",
    "pycrypto"
]

if platform.system() == 'Windows':
    requirements += ["pywin32", "win32com", "wmi"]
        
setuptools.setup(
    name='CloudAgent',
    version=cloudagent.__version__,
    author='VEXXHOST, Inc.',
    author_email='support@vexxhost.com',
    packages=['cloudagent', 'cloudagent.drivers'],
    scripts=['bin/cloudagent'],
    console=['bin/cloudagent'],
    service=[win_service],
    url='http://pypi.python.org/pypi/CloudAgent/',
    license='LICENSE',
    description='OpenStack Cloud Server Agent',
    data_files=[('/usr/share/cloudagent/init-scripts', ['init-scripts/upstart', 'init-scripts/debian', 'init-scripts/redhat'])],
    install_requires = requirements,
    dependency_links = ['http://pypi.python.org/packages/source/J/Jinja2/Jinja2-2.6.tar.gz#egg=Jinja2-2.6',
                        'https://pypi.python.org/packages/source/s/simplejson/simplejson-2.1.0.tar.gz#egg=simplejson-2.1.0'],
)
