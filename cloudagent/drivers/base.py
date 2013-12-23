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
Base driver to be implemented by each operating system / platform driver.
"""

from cloudagent import __version__
from cloudagent import simpledh

class BaseDriver(object):
    """Base class for compute drivers."""

    def install(self):
        """Install scripts to ensure running on boot"""
        raise NotImplementedError()

    def get_version(self):
        """Get the current agent version"""
        return __version__

    def key_init(self, compute_pub):
        """Initialize SimpleDH for encrypted communication"""
        self.dh = simpledh.SimpleDH()
        self.dh.compute_shared(int(compute_pub))
        return 'ok:%s' % self.dh.get_public()

    def backup_file(self, path):
        """Create a backup copy of a file"""
        raise NotImplementedError()

    def set_admin_password(self, new_pass):
        """Update the password of the root/administrator account"""
        raise NotImplementedError()

    def inject_file(self, path, contents):
        """Creates/update the content of file with specified contents"""
        raise NotImplementedError()

    def get_nics(self):
        """Get all NICs and their MAC addreses on this instance"""
        raise NotImplementedError()

    def reset_hostname(self, network_info):
        """Reset the hostname of this instance"""
        raise NotImplementedError()

    def reset_resolvers(self, network_info):
        """Reset the resolvers of this instance"""
        raise NotImplementedError()

    def reset_nics(self, network_info):
        """Reset the resolvers of this instance"""
        raise NotImplementedError()

    def reload_network(self):
        """Reload the network configuration on the instance"""
        raise NotImplementedError()

    def reset_network(self, network_info):
        """Update and re-apply new network configuration"""
        self.reset_hostname(network_info)
        self.reset_resolvers(network_info)
        self.reset_nics(network_info)
        self.reload_network()
