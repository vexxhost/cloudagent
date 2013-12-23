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
Misc. utilities
"""

import binascii
import fcntl
import re
import os
import signal
import socket
import string
import struct
import subprocess


_release_filename = re.compile(r'(\w+)[-_](release|version)')
_lsb_release_version = re.compile(r'(.+)'
                                   ' release '
                                   '([\d.]+)'
                                   '[^(]*(?:\((.+)\))?')
_release_version = re.compile(r'([^0-9]+)'
                               '(?: release )?'
                               '([\d.]+)'
                               '[^(]*(?:\((.+)\))?')

# See also http://www.novell.com/coolsolutions/feature/11251.html
# and http://linuxmafia.com/faq/Admin/release-files.html
# and http://data.linux-ntfs.org/rpm/whichrpm
# and http://www.die.net/doc/linux/man/man1/lsb_release.1.html

_supported_dists = (
    'SuSE', 'debian', 'fedora', 'redhat', 'centos',
    'mandrake', 'mandriva', 'rocks', 'slackware', 'yellowdog', 'gentoo',
    'UnitedLinux', 'turbolinux')


def _subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def execute(*cmd, **kwargs):
    """Helper method to execute command with optional retry.

    :param cmd:                Passed to subprocess.Popen.
    :param process_input:      Send to opened process.
    :param check_exit_code:    Single bool, int, or list of allowed exit
                               codes.  Defaults to [0].  Raise
                               exception.ProcessExecutionError unless
                               program exits with one of these code.
    :param delay_on_retry:     True | False. Defaults to True. If set to
                               True, wait a short amount of time
                               before retrying.
    :param attempts:           How many times to retry cmd.

    :raises exception.NovaException: on receiving unknown arguments
    :raises exception.ProcessExecutionError:

    :returns: a tuple, (stdout, stderr) from the spawned process, or None if
             the command fails.
    """
    process_input = kwargs.pop('process_input', None)
    check_exit_code = kwargs.pop('check_exit_code', [0])
    ignore_exit_code = False
    if isinstance(check_exit_code, bool):
        ignore_exit_code = not check_exit_code
        check_exit_code = [0]
    elif isinstance(check_exit_code, int):
        check_exit_code = [check_exit_code]
    delay_on_retry = kwargs.pop('delay_on_retry', True)
    attempts = kwargs.pop('attempts', 1)
    shell = kwargs.pop('shell', False)
    cmd = map(str, cmd)

    if len(kwargs):
        raise Exception(_('Got unknown keyword args '
                          'to utils.execute: %r') % kwargs)

    while attempts > 0:
        attempts -= 1
        try:
            _PIPE = subprocess.PIPE  # pylint: disable=E1101
            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE,
                                   stdout=_PIPE,
                                   stderr=_PIPE,
                                   close_fds=True,
                                   preexec_fn=_subprocess_setup,
                                   shell=shell)
            result = None
            if process_input is not None:
                result = obj.communicate(process_input)
            else:
                result = obj.communicate()
            obj.stdin.close()  # pylint: disable=E1101
            _returncode = obj.returncode  # pylint: disable=E1101
            if not ignore_exit_code and _returncode not in check_exit_code:
                (stdout, stderr) = result
                raise Exception()
            return result
        except Exception, e:
            if not attempts:
                raise


def get_mac_addr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]


def _dist_try_harder(distname,version,id):

    """ Tries some special tricks to get the distribution
        information in case the default method fails.

        Currently supports older SuSE Linux, Caldera OpenLinux and
        Slackware Linux distributions.

    """
    if os.path.exists('/var/adm/inst-log/info'):
        # SuSE Linux stores distribution information in that file
        info = open('/var/adm/inst-log/info').readlines()
        distname = 'SuSE'
        for line in info:
            tv = string.split(line)
            if len(tv) == 2:
                tag,value = tv
            else:
                continue
            if tag == 'MIN_DIST_VERSION':
                version = string.strip(value)
            elif tag == 'DIST_IDENT':
                values = string.split(value,'-')
                id = values[2]
        return distname,version,id

    if os.path.exists('/etc/.installed'):
        # Caldera OpenLinux has some infos in that file (thanks to Colin Kong)
        info = open('/etc/.installed').readlines()
        for line in info:
            pkg = string.split(line,'-')
            if len(pkg) >= 2 and pkg[0] == 'OpenLinux':
                # XXX does Caldera support non Intel platforms ? If yes,
                #     where can we find the needed id ?
                return 'OpenLinux',pkg[1],id

    if os.path.isdir('/usr/lib/setup'):
        # Check for slackware verson tag file (thanks to Greg Andruk)
        verfiles = os.listdir('/usr/lib/setup')
        for n in range(len(verfiles)-1, -1, -1):
            if verfiles[n][:14] != 'slack-version-':
                del verfiles[n]
        if verfiles:
            verfiles.sort()
            distname = 'slackware'
            version = verfiles[-1][14:]
            return distname,version,id

    return distname,version,id


def _parse_release_file(firstline):

    # Default to empty 'version' and 'id' strings.  Both defaults are used
    # when 'firstline' is empty.  'id' defaults to empty when an id can not
    # be deduced.
    version = ''
    id = ''

    # Parse the first line
    m = _lsb_release_version.match(firstline)
    if m is not None:
        # LSB format: "distro release x.x (codename)"
        return tuple(m.groups())

    # Pre-LSB format: "distro x.x (codename)"
    m = _release_version.match(firstline)
    if m is not None:
        return tuple(m.groups())

    # Unkown format... take the first two words
    l = string.split(string.strip(firstline))
    if l:
        version = l[0]
        if len(l) > 1:
            id = l[1]
    return '', version, id


def linux_distribution(distname='', version='', id='',
                       supported_dists=_supported_dists,
                       full_distribution_name=1):
    # Backported from platform.py for old Python platforms
    """ Tries to determine the name of the Linux OS distribution name.

        The function first looks for a distribution release file in
        /etc and then reverts to _dist_try_harder() in case no
        suitable files are found.

        supported_dists may be given to define the set of Linux
        distributions to look for. It defaults to a list of currently
        supported Linux distributions identified by their release file
        name.

        If full_distribution_name is true (default), the full
        distribution read from the OS is returned. Otherwise the short
        name taken from supported_dists is used.

        Returns a tuple (distname,version,id) which default to the
        args given as parameters.

    """
    try:
        etc = os.listdir('/etc')
    except os.error:
        # Probably not a Unix system
        return distname,version,id
    etc.sort()
    for file in etc:
        m = _release_filename.match(file)
        if m is not None:
            _distname,dummy = m.groups()
            if _distname in supported_dists:
                distname = _distname
                break
    else:
        return _dist_try_harder(distname,version,id)

    # Read the first line
    f = open('/etc/'+file, 'r')
    firstline = f.readline()
    f.close()
    _distname, _version, _id = _parse_release_file(firstline)

    if _distname and full_distribution_name:
        distname = _distname
    if _version:
        version = _version
    if _id:
        id = _id
    return distname, version, id
