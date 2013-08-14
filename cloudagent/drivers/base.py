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


class BaseDriver(object):
    """Base class for compute drivers."""

    def set_admin_password(new_pass):
        """Update the password of the root/administrator account"""
        raise NotImplementedError()

    def inject_file(self, path, contents):
        """Creates/update the content of file with specified contents"""
        raise NotImplementedError()

    def reset_network(self, network_info):
        """Update and re-apply new network configuration"""
        raise NotImplementedError()
