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

import glob
import os
import shutil
import sys
import subprocess

from cloudagent.drivers import linux
from cloudagent import templates


class RedhatDriver(linux.LinuxDriver):
    """Redhat-based operating system driver"""

    def install(self):
        """Install scripts to ensure running on boot"""
        path = "/usr/share/cloudagent/init-scripts/redhat"
        install_path = '/etc/init.d/cloudagent'
        shutil.copyfile(path, install_path)
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
        devices = self._get_devices(network_info)
        files_to_create = {}

        for device in devices:
            # Generate primary interface config
            config_path = "/etc/sysconfig/network-scripts/ifcfg-%s"
            config = templates.REDHAT_IFCFG.render({'dev': device})
            files_to_create[config_path % device['name']] = config

            # Generate config for secondary interfaces
            for index, alias_dev in enumerate(device['ips']):
                alias_dev['name'] = "%s:%s" % (device['name'], index)
                config = templates.REDHAT_IFCFG.render({'dev': alias_dev})
                files_to_create[config_path % alias_dev['name']] = config

        # Remove all existing configuration files
        existing_files = glob.glob("/etc/sysconfig/network-scripts/ifcfg-eth*")
        for f in existing_files:
            os.remove(f)

        # Write out all new configuration files
        for path, contents in files_to_create.iteritems():
            self.inject_file(path, contents)

    def reload_network(self):
        subprocess.call(('service', 'network', 'restart'))
