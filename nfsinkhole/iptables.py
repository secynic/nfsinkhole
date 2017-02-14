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

from .exceptions import (IPTablesError, IPTablesExists, IPTablesNotExists,
                         SubprocessError)
from .utils import popen_wrapper
import logging

log = logging.getLogger(__name__)


class IPTablesSinkhole:
    """
    The class for managing sinkhole configuration within iptables.

    Args:
        interface: The secondary network interface dedicated to sinkhole
            traffic.
            Warning: Do not accidentally set this to your primary interface.
            It will drop all traffic, and kill your remote access.
        interface_addr: The IP address assigned to interface.
        log_prefix: Prefix for syslog messages.
        protocol: The protocol(s) to log (all traffic will still be dropped).
            Accepts a comma separated string of protocols
            (tcp,udp,udplite,icmp,esp,ah,sctp) or all.
        dport: The destination port(s) to log (for applicable protocols).
            Range should be in the format startport:endport or 0,1,2,3,n..
        hashlimit: Set the hashlimit rate. Hashlimit is used to tune the
            amount of events logged. See the iptables-extensions docs:
            http://ipset.netfilter.org/iptables-extensions.man.html
        hashlimitmode: Set the hashlimit mode, a comma separated string of
            options (srcip,srcport,dstip,dstport). More options here results
            in more logs generated.
        hashlimitburst: Maximum initial number of packets to match.
        hashlimitexpire: Number of milliseconds to keep entries in the hash
            table.
        srcexclude: Exclude a comma separated string of source IPs/CIDRs from
            logging.
    """

    def __init__(self, interface=None, interface_addr=None,
                 log_prefix='"[nfsinkhole] "',
                 protocol='all', dport='0:65535',
                 hashlimit='1/h', hashlimitmode='srcip,dstip,dstport',
                 hashlimitburst='1', hashlimitexpire='3600000',
                 srcexclude='127.0.0.1'
                 ):

        # TODO: add arg checks across all classes
        self.interface = interface
        self.interface_addr = interface_addr
        self.log_prefix = log_prefix
        self.protocol = protocol
        self.dport = dport
        self.hashlimit = hashlimit
        self.hashlimitmode = hashlimitmode
        self.hashlimitburst = hashlimitburst
        self.hashlimitexpire = hashlimitexpire
        self.srcexclude = srcexclude

    def list_existing_rules(self, filter_io_drop=False):
        """
        The function for retrieving current iptables rules related to
        nfsinkhole.

        Args:
            filter_io_drop: Boolean for only showing the DROP rules for INPUT
                and OUTPUT. These are not shown by default. This exists to
                avoid allowing packets on the interface if the service is down.
                If installed, the interface always drops all traffic regardless
                of the service state.

        Returns:
            List: Matching sinkhole lines returned by iptables -S.

        Raises:
            IPTablesError: A Linux process had an error (stderr).
        """

        # Get list summary of iptables rules
        cmd = ['iptables', '-S']

        existing = []

        # Get all of the iptables rules
        try:

            out, err = popen_wrapper(cmd, sudo=True)

        except OSError as e:  # pragma: no cover

            raise IPTablesError('Error encountered when running process "{0}":'
                                '\n{1}'.format(' '.join(cmd), e))

        # If any errors, iterate them and write to log, then raise
        # IPTablesError.
        if err:  # pragma: no cover

            arr = err.splitlines()
            raise IPTablesError('Error encountered when running process "{0}":'
                                '\n{1}'.format(' '.join(cmd), '\n'.join(arr)))

        # Iterate the iptables rules, only grabbing nfsinkhole related rules.
        arr = out.splitlines()
        for line in arr:
            tmp_line = line.decode('ascii', 'ignore')
            if ('SINKHOLE' in tmp_line
                ) or filter_io_drop and tmp_line.strip() in [
                    '-A INPUT -i {0} -j DROP'.format(self.interface),
                    '-A OUTPUT -o {0} -j DROP'.format(self.interface)
            ]:
                existing.append(tmp_line.strip())

        return existing

    def create_rules(self):
        """
        The function for writing iptables rules related to nfsinkhole.
        """

        log.info('Checking for existing iptables rules.')
        existing = self.list_existing_rules()

        # Existing sinkhole related iptables lines found, can't create.
        if len(existing) > 0:

            raise IPTablesExists('Existing iptables rules found for '
                                 'nfsinkhole:\n{0}'
                                 ''.format('\n'.join(existing)))

        log.info('Writing iptables config')

        # Create a new iptables chain for logging
        tmp_arr = ['iptables', '-N', 'SINKHOLE']

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))
        popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Exclude IPs/CIDRs from logging (scanners, monitoring, pen-testers,
        # etc):
        for addr in self.srcexclude.split(','):

            tmp_arr = [
                'iptables',
                '-A', 'SINKHOLE',
                '-s', addr,
                '-j', 'RETURN'
            ]

            log.info('Writing: {0}'.format(' '.join(tmp_arr)))
            popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Tell the chain to log and use the prefix self.log_prefix:
        tmp_arr = [
            'iptables',
            '-A', 'SINKHOLE',
            '-j', 'LOG',
            '--log-prefix', self.log_prefix
        ]

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))
        popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Tell the chain to also log to netfilter (for packet capture):
        tmp_arr = ['iptables', '-A', 'SINKHOLE',
                   '-j', 'NFLOG']

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))
        popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Tell the chain to trigger on hashlimit and protocol/port settings
        tmp_arr = [
            'iptables',
            '-i', self.interface,
            '-d', self.interface_addr,
            '-j', 'SINKHOLE',
            '-m', 'hashlimit',
            '--hashlimit', self.hashlimit,
            '--hashlimit-burst', self.hashlimitburst,
            '--hashlimit-mode', self.hashlimitmode,
            '--hashlimit-name', 'sinkhole',
            '--hashlimit-htable-expire', self.hashlimitexpire,
            '-I', 'INPUT', '1'
        ]

        # if --protocol filtered, set mode to multiport with protocol, and
        # set destination port if provided and applicable to the protocol(s)
        if self.protocol != 'all':

            tmp_arr += ['-m', 'multiport', '--protocol', self.protocol]

            if self.dport != '0:65535':
                tmp_arr += ['--dport', self.dport]

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))
        popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

    def create_drop_rule(self):
        """
        The function for writing the iptables DROP rule for the interface.
        """

        log.info('Checking for existing iptables DROP rules.')
        existing = self.list_existing_rules(filter_io_drop=True)

        # Existing sinkhole related iptables lines found, can't create.
        if len(existing) > 0:

            for line in existing:

                if line in (
                    '-A INPUT -i {0} -j DROP'.format(self.interface),
                    '-A OUTPUT -o {0} -j DROP'.format(self.interface)
                ):

                    raise IPTablesExists('Existing iptables DROP rules found '
                                         'for nfsinkhole:\n{0}'
                                         ''.format(line))

        log.info('Writing iptables DROP config')

        # Create rules to drop all I/O traffic:
        tmp_arr = [
            'iptables',
            '-i', self.interface,
            '-j', 'DROP',
            '-I', 'INPUT', '1'
        ]

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))
        popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        tmp_arr = [
            'iptables',
            '-o', self.interface,
            '-j', 'DROP',
            '-I', 'OUTPUT', '1'
        ]

        log.info('Writing: {0}'.format(' '.join(tmp_arr)))

        # TODO: replicate exception handling to other subprocess calls
        try:

            popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        except SubprocessError as e:  # pragma: no cover

            raise IPTablesError(e)

    def delete_rules(self):
        """
        The function for deleting iptables rules related to nfsinkhole.
        """

        log.info('Checking for existing iptables rules.')
        existing = self.list_existing_rules()

        # No sinkhole related iptables lines found.
        if len(existing) == 0:

            raise IPTablesNotExists('No existing rules found.')

        log.info('Deleting iptables config (only what was created)')

        # Iterate all of the active sinkhole related iptables lines
        flush = False
        for line in existing:

            if '-A SINKHOLE' in line or line == '-N SINKHOLE':

                # Don't try to delete the SINKHOLE chain yet, it needs to be
                # empty. Set flush to clear it after this loop.
                flush = True

            elif line not in (
                '-A INPUT -i {0} -j DROP'.format(self.interface),
                '-A OUTPUT -o {0} -j DROP'.format(self.interface)
            ):

                # Delete a single line (not the SINKHOLE chain itself).
                stmt = line.replace('-A', '-D').strip().split(' ')
                tmp_arr = ['iptables'] + stmt

                log.info('Deleting: {0}'.format(' '.join(tmp_arr)))
                popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # The SINKHOLE chain was detected. Remove it.
        if flush:

            # All lines in the SINKHOLE chain should have been flushed already,
            # but run a flush to be sure.
            tmp_arr = ['iptables', '-F', 'SINKHOLE']

            log.info('Flushing: {0}'.format(' '.join(tmp_arr)))
            popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

            # Now that the SINKHOLE chain has been flushed, we can delete it.
            tmp_arr = ['iptables', '-X', 'SINKHOLE']

            log.info('Deleting: {0}'.format(' '.join(tmp_arr)))
            popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Return a list of matching lines.
        return len(existing)

    def delete_drop_rule(self):
        """
        The function for deleting the iptables DROP rule for the interface.
        """

        log.info('Checking for existing iptables DROP rules.')
        existing = self.list_existing_rules(filter_io_drop=True)

        # No sinkhole related iptables lines found.
        if len(existing) == 0:

            raise IPTablesNotExists('No existing rules found.')

        log.info('Deleting iptables DROP config.')

        count = 0
        for line in existing:

            if line in (
                    '-A INPUT -i {0} -j DROP'.format(self.interface),
                    '-A OUTPUT -o {0} -j DROP'.format(self.interface)
            ):
                count += 1
                # Delete a single line (not the SINKHOLE chain itself).
                stmt = line.replace('-A', '-D').split(' ')
                tmp_arr = ['iptables'] + stmt

                log.info('Deleting: {0}'.format(' '.join(tmp_arr)))
                popen_wrapper(cmd_arr=tmp_arr, raise_err=True, sudo=True)

        # Return the number of matching lines.
        return count
