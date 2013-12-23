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
A driver for Windows operating systems
"""

import os
import sys

import wmi

from ctypes import windll
from win32com import adsi

from cloudagent.drivers import base

class WindowsDriver(base.BaseDriver):
    """Windows driver"""

    def install(self):
        """Install scripts to ensure running on boot"""
        dir_path = os.path.dirname(sys.executable)
        os.system(dir_path + "\AgentService.exe -install -auto")
        os.system("net start cloudagent")

    def set_admin_password(self, new_pass):
        """Update the password of the root/administrator account"""
        ads_obj = adsi.ADsGetObject("WinNT://localhost/Administrator,user")
        ads_obj.Getinfo()
        ads_obj.SetPassword(new_pass)

    def get_nics(self):
        """Get all NICs and their MAC addreses on this instance"""
        pass

    def reset_hostname(self, network_info):
        """Reset the hostname of this instance"""
        hostname = network_info['hostname']
        windll.kernel32.SetComputerNameExW(5, hostname)

    def reset_resolvers(self, network_info):
        """Reset the resolvers of this instance"""
        c = wmi.WMI()
        for nic in c.Win32_NetworkAdapterConfiguration():
            if not nic.MACAddress: continue
            key = 'vif-' + nic.MACAddress.lower().replace(':', '')
            if key in network_info:
                nic.SetDNSServerSearchOrder(network_info[key]['dns'])


    def reset_nics(self, network_info):
        """Reset the resolvers of this instance"""
        c = wmi.WMI()

        # Configure IP addresses
        for nic in c.Win32_NetworkAdapterConfiguration():
            if not nic.MACAddress: continue
            key = 'vif-' + nic.MACAddress.lower().replace(':', '')
            if key in network_info:
                ips = [i['ip'] for i in network_info[key]['ips']]
                subnets = [i['netmask'] for i in network_info[key]['ips']]
                nic.EnableStatic(ips, subnets)
                nic.SetGateways([network_info[key]['gateway']], [1])

        # Rename the network name
        for nic in c.Win32_NetworkAdapter():
            if not nic.MACAddress: continue
            key = 'vif-' + nic.MACAddress.lower().replace(':', '')
            if key in network_info:
                nic.NetConnectionID = network_info[key]['label'].title()
                nic.put()

    def reload_network(self):
        """Reload the network configuration on the instance"""
        pass
