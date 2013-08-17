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

"""
A driver for Redhat-derived operating systems.
"""

import os
import shutil
import subprocess

from cloudagent.drivers import linux
from cloudagent import templates


class RedhatDriver(linux.LinuxDriver):
    """Redhat-based operating system driver"""

    def install(self):
        """Install scripts to ensure running on boot"""
        path = os.path.dirname(os.path.realpath(__file__))
        install_path = '/etc/init.d/cloudagent'
        shutil.copyfile('%s/../../init-scripts/redhat' % path, install_path)
        os.chmod(install_path, 0755)
        subprocess.call(('chkconfig', 'cloudagent', 'on'))

    def reset_hostname(self, network_info):
        """Reset the hostname of this instance"""
        super(RedhatDriver, self).reset_hostname(network_info)

        # Apply Redhat-specific changes
        hostname = network_info['hostname']
        sysconf_file = templates.REDHAT_SYSCONFIG.render({'hostname': hostname})
        self.inject_file('/etc/sysconfig/network', sysconf_file)

    def reset_nics(self, network_info):
        """Reset the NICs of this instance"""
        pass

    def reload_network(self):
        subprocess.call(('service', 'network', 'restart'))
