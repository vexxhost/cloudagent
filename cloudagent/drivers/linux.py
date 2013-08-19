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
A driver for Linux based operating systems, implements common commands
throughout the Linux platform
"""

import crypt
import os
import shutil
import subprocess
import time

from cloudagent.drivers import base
from cloudagent import templates
from cloudagent import utils

class LinuxDriver(base.BaseDriver):
    """Base Linux driver"""

    def backup_file(self, path):
        """Create a backup copy of a file"""
        timestamp = int(time.time())
        new_name = "%s.%s" % (path, timestamp)
        shutil.copyfile(path, new_name)

    def set_admin_password(self, new_pass):
        """Update the password of the root/administrator account"""
        salt = os.urandom(16).encode('hex')
        password = crypt.crypt(new_pass,'$1$' + salt + '$')
        ret = subprocess.call(('usermod', '-p', password, 'root'))

        if ret != 0:
            raise RuntimeError('Failed to change password')

    def inject_file(self, path, contents):
        """Creates/update the content of file with specified contents"""
        if os.path.exists(path):
            self.backup_file(path)

        fd = open(path, 'w')
        fd.write(contents)
        fd.close()

    def get_nics(self):
        """Get all NICs and their MAC addreses on this instance"""
        nics = []
        for line in open('/proc/net/dev', 'r'):
            if 'eth' in line:
                nics += [line.split(':')[0].strip()]

        nic_map = {}
        for nic in nics:
            nic_map[nic] = utils.get_mac_addr(nic)

        return nic_map

    def reset_hostname(self, network_info):
        """Reset the hostname of this instance"""
        hostname = network_info['hostname']
        ret = subprocess.call(('hostname', hostname))

        context = {'ips': [], 'hostname': hostname}
        for key, value in network_info.iteritems():
            if 'vif-' not in key: continue
            context['ips'] += [addr['ip'] for addr in value['ips']]
        hosts_file = templates.HOSTS.render(context)

        # Write the hosts file
        self.inject_file('/etc/hosts', hosts_file)

    def _generate_host_records(self, ips, hostname):
        host_lines = []
        for ip in ips:
            host_lines += [templates.HOSTS_FILE_LINE % locals()]
        return host_lines

    def reset_resolvers(self, network_info):
        """Reset the resolvers of this instance"""
        # Generate resolver records
        resolv_records = []
        for key, value in network_info.iteritems():
            if 'vif-' not in key: continue
            resolv_records += self._generate_resolv_records(value['dns'])

        # Generate the resolvers file
        resolv_file = "\n".join(resolv_records) + "\n"

        # Write the resolvers file
        self.inject_file('/etc/resolv.conf', resolv_file)

    def _generate_resolv_records(self, dns_records):
        resolv_lines = []
        for dns in dns_records:
            resolv_lines += ['nameserver %s' % dns]
        return resolv_lines

    def _get_devices(self, network_info):
        """Get the device information"""
        nics = self.get_nics()
        mac_dev = dict([[v,k] for k,v in nics.items()])

        devices = []
        for key, value in network_info.iteritems():
            if 'vif-' not in key: continue
            if len(value['ips']) == 0: continue

            primary_ip = value['ips'].pop(0)
            device = {
                'name': mac_dev[value['mac']],
                'addr': primary_ip['ip'],
                'netmask': primary_ip['netmask'],
                'gateway': primary_ip['gateway'],
                'mac': value['mac'],
                'ips': []
            }

            if len(value['dns']) != 0:
                device['dns'] = ' '.join(value['dns'])

            for ip in value['ips']:
                device['ips'] += [{
                    'addr': ip['ip'],
                    'netmask': ip['netmask'],
                }]

            devices += [device]
        return devices
