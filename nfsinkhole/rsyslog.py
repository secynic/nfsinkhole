# Copyright (c) 2016-2017 Philip Hane
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from .exceptions import BinaryNotFound
from .selinux import SELinux
from .utils import popen_wrapper
import logging
import os
import re

log = logging.getLogger(__name__)
se_linux = SELinux()


class RSyslog:
    """
    The class for managing rsyslog checks and configuration.

    Args:
        is_systemd: True if systemd is in use, False if not (use init.d).
    """

    def __init__(self, is_systemd=False):

        self.is_systemd = is_systemd

        # Raise error if rsyslogd is not found
        if not os.path.exists('/sbin/rsyslogd'):

            log.debug('Path not found: /sbin/rsyslogd')
            raise BinaryNotFound('rsyslogd was not detected.')

    def get_version(self):
        """
        The function for checking the rsyslog version.

        Returns:
            String: rsyslog version string if found, or None.
        """

        log.info('Checking rsyslog version.')

        out, err = popen_wrapper(['rsyslogd', '-version'],
                                 log_stdout_line=False)

        rsyslog_version = None
        if out and len(out) > 0:

            log.debug('Attempting to parse version number from stdout')
            m = re.search(b'rsyslogd\s([0-9]+\.[0-9]+\.[0-9]+),', out)
            try:

                rsyslog_version = m.group(1)
                log.info('rsyslog version found: {0}'.format(rsyslog_version))

            except IndexError:

                log.info('rsyslog version not found')
                pass

        else:

            log.info('rsyslog version not found')

        return rsyslog_version

    def selinux_associate(self):
        """
        The function for associating the rsyslog config with selinux.
        """

        log.info('Associating rsyslog config with SELinux')

        se_linux.associate('/etc/rsyslog.d/nfsinkhole.conf')

    # TODO: syslog target options; currently, forwarding config is manual
    def create_config(self, prefix='[nfsinkhole] '):
        """
        The function for creating the rsyslog config.

        Args:
            prefix: The log prefix set in iptables.
        """

        log.info('Creating rsyslog config')

        log.debug('Writing nfsinkhole.conf')
        with open("nfsinkhole.conf", "wt") as syslog_config:
            syslog_config.write(
                ':msg,contains,{0} {1}'
                ''.format(prefix,
                          '/var/log/nfsinkhole-events.log'))

        log.debug('Moving nfsinkhole.conf to /etc/rsyslog.d')

        cmd = ['mv', 'nfsinkhole.conf', '/etc/rsyslog.d']
        popen_wrapper(cmd, sudo=True)

        log.debug('Setting root ownership for '
                  '/etc/rsyslog.d/nfsinkhole.conf')

        cmd = ['chown', 'root:root', '/etc/rsyslog.d/nfsinkhole.conf']
        popen_wrapper(cmd, sudo=True)

    def delete_config(self):
        """
        The function for deleting the rsyslog config.
        """

        log.info('Deleting rsyslog config')

        log.debug('Removing file: /etc/rsyslog.d/nfsinkhole.conf')

        cmd = ['rm', '/etc/rsyslog.d/nfsinkhole.conf']
        popen_wrapper(cmd, sudo=True)

    def restart(self):
        """
        The function for restarting the rsyslog service.
        """

        log.info('Restarting rsyslog service')

        if self.is_systemd:

            log.debug('Restarting systemd rsyslog service (via systemctl)')

            cmd = ['systemctl', 'restart', 'rsyslog.service']
            popen_wrapper(cmd, sudo=True)

        else:

            log.debug('Restarting init.d rsyslog service (via service)')

            cmd = ['service', 'rsyslog', 'restart']
            popen_wrapper(cmd, sudo=True)
