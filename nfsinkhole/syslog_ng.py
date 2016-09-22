# Copyright (c) 2016 Philip Hane
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
from .utils import popen_wrapper
from .selinux import SELinux
import logging
import os

log = logging.getLogger(__name__)
se_linux = SELinux()


# TODO: this is just a placeholder, this class is not finished or used yet
class SyslogNG:
    """
    The class for managing syslog-ng checks and configuration.

    Args:
        is_systemd: True if systemd is in use, False if not (init.d).
    """

    def __init__(self, is_systemd=False):

        self.is_systemd = is_systemd

        # Raise error if syslog-ng is not found
        if not os.path.exists('/usr/sbin/syslog-ng'):

            log.debug('Path not found: /usr/sbin/syslog-ng')
            raise BinaryNotFound('syslog-ng was not detected.')

    def get_version(self):
        """
        The function for checking the syslog-ng version.

        Returns:
            String: syslog-ng version string if found, or None.
        """

        log.info('Checking syslog-ng version.')

        out, err = popen_wrapper(['syslog-ng', '-V'])

        syslog_ng_version = None
        if out and len(out) > 0:

            syslog_ng_version = out
            log.info('syslog-ng version found: {0}'.format(syslog_ng_version))

        else:

            log.info('syslog-ng version not found')

        return syslog_ng_version

    def selinux_associate(self):
        """
        The function for associating the syslog-ng config with selinux.
        """

        log.info('Associating syslog-ng config with SELinux')

        se_linux.associate('/etc/syslog-ng/nfsinkhole.conf')

    # TODO: syslog target options; currently, forwarding config is manual
    # TODO: actual config, currently writes nothing
    def create_config(self, prefix='[nfsinkhole] '):
        """
        The function for creating the syslog-ng config. (incomplete/unused)

        Args:
            prefix: The log prefix set in iptables.
        """

        log.info('Creating syslog-ng config')

        log.debug('Writing nfsinkhole.conf')
        with open("nfsinkhole.conf", "wt") as syslog_config:
            syslog_config.write('')

        log.debug('Moving nfsinkhole.conf to /etc/syslog-ng')
        popen_wrapper(['/usr/bin/sudo', 'mv', 'nfsinkhole.conf',
                       '/etc/syslog-ng'])

        log.debug('Setting execute permissions for '
                  '/etc/syslog-ng/nfsinkhole.conf')
        popen_wrapper(['/usr/bin/sudo', 'chmod', '-x',
                       '/etc/syslog-ng/nfsinkhole.conf'])

        log.debug('Setting root ownership for '
                  '/etc/syslog-ng/nfsinkhole.conf')
        popen_wrapper(['/usr/bin/sudo', 'chown', 'root:root',
                       '/etc/syslog-ng/nfsinkhole.conf'])

    def delete_config(self):
        """
        The function for deleting the syslog-ng config.
        """

        log.info('Deleting syslog-ng config')

        log.debug('Removing file: /etc/syslog-ng/nfsinkhole.conf')
        popen_wrapper(
            ['/usr/bin/sudo', 'rm', '/etc/syslog-ng/nfsinkhole.conf'])

    def restart(self):
        """
        The function for restarting the syslog-ng service.
        """

        log.info('Restarting syslog-ng service')

        if self.is_systemd:

            log.debug('Restarting systemd syslog-ng service (via systemctl)')
            popen_wrapper(['/usr/bin/sudo', 'systemctl', 'restart',
                           'syslog-ng.service'])

        else:

            log.debug('Restarting init.d syslog-ng service (via service)')
            popen_wrapper(
                ['/usr/bin/sudo', 'service', 'syslog-ng', 'restart'])
