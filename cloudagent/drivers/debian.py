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
A driver for Debian-derived operating systems.
"""

import os
import shutil
import subprocess

from cloudagent.drivers import linux
from cloudagent import templates


class DebianDriver(linux.LinuxDriver):
    """Debian-based operating system driver"""

    def install(self):
        """Install scripts to ensure running on boot"""
        path = os.path.dirname(os.path.realpath(__file__))
        install_path = '/etc/init.d/cloudagent'
        shutil.copyfile('%s/../../init-scripts/debian' % path, install_path)
        os.chmod(install_path, 0755)
        subprocess.call(('update-rc.d', 'cloudagent', 'defaults'))

    def reset_hostname(self, network_info):
        """Reset the hostname of this instance"""
        super(DebianDriver, self).reset_hostname(network_info)

        # Apply Debian-specific changes
        hostname_file = network_info['hostname'] + "\n"
        self.inject_file('/etc/hostname', hostname_file)

    def reset_nics(self, network_info):
        """Reset the NICs of this instance"""
        context = {'devices': self._get_devices(network_info)}
        interfaces_file = templates.DEBIAN_INTERFACES.render(context)

        # Write the interfaces file
        self.inject_file("/etc/network/interfaces", interfaces_file)

    def reload_network(self):
        subprocess.call(('invoke-rc.d', 'hostname.sh', 'start'))
        subprocess.call(('invoke-rc.d', 'networking', 'restart'))
