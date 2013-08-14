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
import subprocess

from cloudagent.drivers import base


class LinuxDriver(base.BaseDriver):
    """Base Linux driver"""

    def set_admin_password(self, new_pass):
        """Update the password of the root/administrator account"""
        salt = os.urandom(16).encode('hex')
        password = crypt.crypt(new_pass,'$1$' + salt + '$')
        ret = subprocess.call(('usermod', '-p', password, 'root'))

        if ret != 0:
            raise RuntimeError('Failed to change password')

    def inject_file(self, path, contents):
        """Creates/update the content of file with specified contents"""
        fd = open(path, 'w')
        fd.write(contents)
        fd.close()
