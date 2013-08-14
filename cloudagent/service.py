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
Agent configuration, service management and execution class
"""

import base64
import platform

import serial

from cloudagent import __version__
from cloudagent.drivers import debian


class AgentService(object):
    """Agent serial service"""

    def __init__(self):
        """Load the configuration and the proper driver"""
        distro, version, codename = platform.linux_distribution()

        if distro == 'debian':
            self.driver = debian.DebianDriver()

        self.serial = serial.Serial(2)

    def run(self):
        while True:
            b64_args = self.serial.readline().strip().split()
            args = []

            try:
                for arg in b64_args:
                    args += [base64.b64decode(arg)]
            except TypeError, e:
                self.serial.write('invalid-data\n')
                continue

            command = args.pop(0)
            self.run_command(command, args)

    def run_command(self, command, args):
        try:
            # If set_admin_password then decrypt argument
            if command == 'set_admin_password':
                args[0] = self.driver.dh.decrypt(args[0])
            print command, args

            driver_command = getattr(self.driver, command)
            ret = driver_command(*args)

            print 'ret:', ret

            if ret:
                self.serial.write("%s\n" % ret)
            else:
                self.serial.write("ok\n")
        except AttributeError, e:
            self.serial.write('invalid-cmd\n')
        except TypeError, e:
            self.serial.write('missing-args\n')
        except Exception, e:
            print e
            self.serial.write('%s\n' % e)
