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
import re

log = logging.getLogger(__name__)


class TCPDump:
    """
    The class for managing tcpdump checks.

    Args:
        sbin: Path to tcpdump binary
    """

    def __init__(self, sbin='/usr/sbin/tcpdump'):

        self.sbin = sbin
        self.exists = os.path.exists(self.sbin)

    def check_packet_print(self):
        """
        The function for checking if tcpdump/nflog support packet printing.

        Returns:
            Boolean: True if packet printing is supported, or False.
        """

        log.info('Checking tcpdump/nflog packet printing support.')

        tcpdump_version = self.get_version()
        if not tcpdump_version or tcpdump_version < '4.5':

            log.warn('Packet printing is not supported. Consider upgrading '
                     'your kernel/tcpdump.')
            return False

        return True

    def get_version(self):
        """
        The function for checking the tcpdump version.

        Returns:
            String: tcpdump version string if found, or None.
        """

        log.info('Checking tcpdump version.')

        out, err = popen_wrapper([self.sbin, '-w'], log_stdout_line=False)

        tcpdump_version = None
        if out and len(out) > 0:

            for o in out.splitlines():

                # TODO: eliminate loop, re search the whole output
                if 'tcpdump version' in o:

                    m = re.search('tcpdump\sversion\s([0-9]+\.[0-9]+)?.*', o)
                    try:

                        tcpdump_version = m.group(1)
                        log.info('tcpdump version found: {0}'
                                 ''.format(tcpdump_version))

                    except IndexError:

                        log.info('tcpdump version not found')
                        pass

        return tcpdump_version
