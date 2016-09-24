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

from .utils import popen_wrapper
import logging
import os

log = logging.getLogger(__name__)
uid = os.geteuid()  # Unix req; autodoc_mock_imports for Sphinx cross platform


class AppArmor:
    """
    The class for managing apparmor policy enforcement, if it is installed.
    """

    def __init__(self):

        self.exists = os.path.exists('/etc/apparmor.d')

    def disable_enforcement(self, module='usr.sbin.tcpdump'):
        """
        The function for disabling AppArmor enforcement for a module.

        Args:
            module: Module in /etc/apparmor.d to disable.

        Returns:
            Boolean: True if disabling enforcement was successful, or False.
        """

        log.info('Attempting to disable AppArmor enforcement for: {0}.'
                 ''.format(module))

        if self.exists:

            log.debug('AppArmor found; disabling enforcement.')

            cmd = [
                'ln', '-s',
                '/etc/apparmor.d/{0}'.format(module),
                '/etc/apparmor.d/disable/'
            ]

            # run sudo if not root
            if uid != 0:
                cmd = ['/usr/bin/sudo'] + cmd

            popen_wrapper(cmd)

            log.debug('Restarting AppArmor service')

            cmd = ['/etc/init.d/apparmor', 'restart']

            # run sudo if not root
            if uid != 0:
                cmd = ['/usr/bin/sudo'] + cmd

            popen_wrapper(cmd)

            return True

        else:

            log.error('AppArmor was not found.')
            return False

    def enable_enforcement(self, module='usr.sbin.tcpdump'):
        """
        The function for enabling AppArmor enforcement for a module.

        Args:
            module: Module in /etc/apparmor.d to enable.

        Returns:
            Boolean: True if enabling enforcement was successful, or False.
        """

        log.info('Attempting to enable AppArmor enforcement for: {0}.'
                 ''.format(module))

        if self.exists:

            log.debug('AppArmor found; enabling enforcement.')

            cmd = ['rm', '/etc/apparmor.d/disable/{0}'.format(module)]

            # run sudo if not root
            if uid != 0:
                cmd = ['/usr/bin/sudo'] + cmd

            popen_wrapper(cmd)

            log.debug('Restarting AppArmor service')

            cmd = ['/etc/init.d/apparmor', 'restart']

            # run sudo if not root
            if uid != 0:
                cmd = ['/usr/bin/sudo'] + cmd

            popen_wrapper(cmd)

            return True

        else:

            log.error('AppArmor was not found.')
            return False
