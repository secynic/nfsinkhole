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
from .utils import popen_wrapper
from .selinux import SELinux
import logging
import os
import subprocess

log = logging.getLogger(__name__)
uid = os.geteuid()  # Linux req; autodoc_mock_imports for Sphinx cross platform
se_linux = SELinux()


class SyslogNG:
    """
    The class for managing syslog-ng checks and configuration.

    Args:
        is_systemd: True if systemd is in use, False if not (init.d).
    """

    def __init__(self, is_systemd=False):

        self.is_systemd = is_systemd

        # Raise error if syslog-ng is not found
        if not os.path.exists('/sbin/syslog-ng'):

            log.debug('Path not found: /sbin/syslog-ng')
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

        se_linux.associate('/etc/syslog-ng/conf.d/nfsinkhole.conf')

    def check_confd(self):
        """
        The function to check syslog-ng.conf for conf.d inclusion, and
        create the @include statement if missing. Will also create the conf.d
        directory, if missing.
        """

        log.info('Checking syslog-ng.conf for conf.d inclusion.')

        cmd = ['grep', '"@include \\"/etc/syslog-ng/conf.d/\\""',
               '/etc/syslog-ng/syslog-ng.conf']
        out, err = popen_wrapper(cmd, sudo=True)

        if not out:

            log.info('conf.d inclusion not found in syslog-ng.conf, appending')

            subprocess.call(
                ['{0}/bin/sh -c '
                 '\'echo "@include \\"/etc/syslog-ng/conf.d/\\"" >> '
                 '/etc/syslog-ng/syslog-ng.conf\''.format(
                    '/usr/bin/sudo ' if uid != 0 else '')],
                shell=True
            )

        log.info('Checking for /etc/syslog-ng/conf.d')

        # Raise error if conf.d is not found
        if not os.path.exists('/etc/syslog-ng/conf.d'):

            log.info('/etc/syslog-ng/conf.d not found, creating directory')

            cmd = ['mkdir', '/etc/syslog-ng/conf.d']
            popen_wrapper(cmd, sudo=True)

    # TODO: syslog target options; currently, forwarding config is manual
    def create_config(self, prefix='[nfsinkhole] '):
        """
        The function for creating the syslog-ng config. (incomplete/unused)

        Args:
            prefix: The log prefix set in iptables.
        """

        log.info('Creating syslog-ng config')

        log.debug('Writing nfsinkhole.conf')
        with open("nfsinkhole.conf", "wt") as syslog_config:
            tmp = (
                'destination d_nfsinkhole {{ '
                'file("/var/log/nfsinkhole-events.log"); }};\n'
                'filter f_nfsinkhole {{ facility(kern) and message({0}); }};\n'
                'log {{ source(s_sys); filter(f_nfsinkhole); '
                'destination(d_nfsinkhole); }};'
            )
            syslog_config.write(
                tmp.format(
                    prefix.replace('[', '\\[').replace(']', '\\]').replace(
                        ' ', '\\s')
                )
            )

        log.debug('Moving nfsinkhole.conf to /etc/syslog-ng/conf.d')
        cmd = ['mv', 'nfsinkhole.conf', '/etc/syslog-ng/conf.d']
        popen_wrapper(cmd, sudo=True)

        log.debug('Setting root ownership for '
                  '/etc/syslog-ng/conf.d/nfsinkhole.conf')

        cmd = ['chown', 'root:root', '/etc/syslog-ng/conf.d/nfsinkhole.conf']
        popen_wrapper(cmd, sudo=True)

    def delete_config(self):
        """
        The function for deleting the syslog-ng config.
        """

        log.info('Deleting syslog-ng config')

        log.debug('Removing file: /etc/syslog-ng/conf.d/nfsinkhole.conf')

        cmd = ['rm', '/etc/syslog-ng/conf.d/nfsinkhole.conf']
        popen_wrapper(cmd, sudo=True)

    def restart(self):
        """
        The function for restarting the syslog-ng service.
        """

        log.info('Restarting syslog-ng service')

        if self.is_systemd:

            log.debug('Restarting systemd syslog-ng service (via systemctl)')

            cmd = ['systemctl', 'restart', 'syslog-ng.service']
            popen_wrapper(cmd, sudo=True)

        else:

            log.debug('Restarting init.d syslog-ng service (via service)')

            cmd = ['service', 'syslog-ng', 'restart']
            popen_wrapper(cmd, sudo=True)
