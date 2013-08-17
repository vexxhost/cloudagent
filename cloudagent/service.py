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

import serial
import simplejson as json

from cloudagent import __version__
from cloudagent import daemon
from cloudagent.drivers import debian
from cloudagent.drivers import redhat
from cloudagent import utils


class AgentService(daemon.Daemon):
    """Agent serial service"""

    def __init__(self):
        """Load the configuration and the proper driver"""
        super(AgentService, self).__init__(pidfile='/var/run/cloudagent.pid',
            verbose=0)

        distro, version, codename = utils.linux_distribution()

        if distro == 'debian' or distro == 'Ubuntu':
            self.driver = debian.DebianDriver()
        elif distro == 'CentOS':
            self.driver = redhat.RedhatDriver()

    def install(self):
        self.driver.install()

    def run(self):
        self.serial = serial.Serial(2)
        self.mdata_serial = serial.Serial(1)

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

            # If reset network, then get all network_info
            if command == 'reset_network':
                args[0] = json.loads(args[0])

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
            self.serial.write('%s\n' % e)
