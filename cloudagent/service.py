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
import json
import platform
import sys

import serial

from cloudagent import __version__
from cloudagent import daemon


class AgentService(daemon.Daemon):
    """Agent serial service"""

    def __init__(self):
        """Load the configuration and the proper driver"""
        super(AgentService, self).__init__(pidfile='/var/run/cloudagent.pid',
            verbose=0)

        self.running = True

        if platform.system() == 'Windows':
            from cloudagent.drivers import windows
            self.driver = windows.WindowsDriver()
        else:
            from cloudagent import utils
            distro, version, codename = utils.linux_distribution()

            if distro in ('debian', 'Ubuntu'):
                from cloudagent.drivers import debian
                self.driver = debian.DebianDriver()
            elif distro in ('CentOS', 'CentOS Linux', 'Scientific Linux', 'Fedora'):
                from cloudagent.drivers import redhat
                self.driver = redhat.RedhatDriver()
            else:
                sys.exit("Unable to find driver for distro: %s" % distro)


    def install(self):
        self.driver.install()

    def run(self):
        # NOTE(mnaser): COM3 is not available under Windows without major
        #               modifications and Windows does not need a console
        #               redirect so we use COM1 instead.
        port = 0 if platform.system() == 'Windows' else 2
        self.serial = serial.Serial(port, timeout=1)

        while self.running:
            b64_args = self.serial.readline().strip().split()
            if not b64_args: continue

            try:
                args = [base64.b64decode(a) for a in b64_args]
            except TypeError, e:
                self.serial.write('error:invalid-data\n')
                continue

            command = args.pop(0)
            self.run_command(command, args)

    def stop(self):
        self.running = False

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

            if ret:
                self.serial.write("%s\n" % ret)
            else:
                self.serial.write("ok\n")
        except AttributeError, e:
            self.serial.write('error:invalid-cmd\n')
        except TypeError, e:
            self.serial.write('error:missing-args\n')
        except Exception, e:
            self.serial.write('error:system\n')
