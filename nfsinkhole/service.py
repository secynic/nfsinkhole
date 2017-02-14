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

from .tcpdump import TCPDump
from .utils import popen_wrapper
import logging
import os
import subprocess
import sys

log = logging.getLogger(__name__)
uid = os.geteuid()  # Linux req; autodoc_mock_imports for Sphinx cross platform

# systemd service template
SYSTEMD_SERVICE_TEMPLATE = (
    '[Unit]\n'
    'Description=Service for nfsinkhole\n'
    'After=iptables.service\n'
    '\n'
    '[Service]\n'
    'Type=forking\n'
    'ExecStartPre={svcexecstartpre}\n'
    'ExecStart={svcexecstart}\n'
    'ExecStop={svcexecstop}\n'
    'User=root\n'
    '\n'
    '[Install]\n'
    'WantedBy=multi-user.target'
)

# init.d service template
INITD_SERVICE_TEMPLATE = (
    '#!/bin/bash\n'
    '# chkconfig: 2345 20 80\n'
    '# description: Service for nfsinkhole\n'
    '. /etc/init.d/functions\n'
    'start() {{\n{start}\n'
    '}}\n'
    '\n'
    'stop() {{\n{stop}\n'
    '}}\n'
    '\n'
    'case "$1" in\n'
    '    start)\n'
    '        start\n'
    '        ;;\n'
    '    stop)\n'
    '        stop\n'
    '        ;;\n'
    '    restart)\n'
    '        stop\n'
    '        start\n'
    '        ;;\n'
    '    status)\n'
    '        ;;\n'
    '    *)\n'
    '        echo "Usage: $0 {{start|stop|status|restart}}"\n'
    'esac\n'
    'exit 0'
)


class SystemService:
    """
    The class for managing the nfsinkhole init.d/systemd service.
    
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
        pcap: Enable packet capture text or raw depending on tcpdump version.
        loglevel: Logging level for nfsinkhole events. This does not affect
            sinkhole traffic logs, only service/library event logs. Must be
            one of debug, info, warning, error, critical.
    """

    def __init__(self, interface=None, interface_addr=None,
                 log_prefix='"[nfsinkhole] "',
                 protocol='all', dport='0:65535',
                 hashlimit='1/h', hashlimitmode='srcip,dstip,dstport',
                 hashlimitburst='1', hashlimitexpire='1800000',
                 srcexclude='127.0.0.1', pcap=True, loglevel='info'
                 ):

        self.exists = os.path.exists('/etc/systemd')
        self.is_systemd = False
        self.svc_path = '/etc/init.d/nfsinkhole'
        self.pcap = pcap
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
        self.loglevel = loglevel

        # Check if packet printing is supported
        tcp_dump = TCPDump()
        self.packet_print = tcp_dump.check_packet_print()

    def check_systemd(self):
        """
        The function for checking if systemd is implemented.

        Returns:
            Tuple (Boolean, String): A tuple: is_systemd, svc_path.
        """

        log.info('Checking for systemd support.')

        if self.exists:

            self.is_systemd = True
            self.svc_path = '/etc/systemd/system/nfsinkhole.service'

        return self.is_systemd, self.svc_path

    def create_service(self):
        """
        The function for creating the init.d/systemd service.
        """

        log.info('Generating nfsinkhole service')

        # Write the service file
        service = open('nfsinkhole.service', "w")
        with service:

            # Run pre main process execution
            execstartpre = (
                '-{pyfp} {fp}/nfsinkhole-service.py '
                '--create --interface {interface} '
                '--protocol {protocol} '
                '--dport {dport} '
                '--prefix {prefix} '
                '--hashlimit {hashlimit} '
                '--hashlimitmode {hashlimitmode} '
                '--hashlimitburst {hashlimitburst} '
                '--hashlimitexpire {hashlimitexpire} '
                '--srcexclude {srcexclude} '
                '--loglevel {loglevel} '
                ''.format(
                    pyfp=sys.executable,
                    fp=os.path.dirname(sys.executable),
                    interface=self.interface,
                    protocol=self.protocol,
                    dport=self.dport,
                    prefix=self.log_prefix,
                    hashlimit=self.hashlimit,
                    hashlimitmode=self.hashlimitmode,
                    hashlimitburst=self.hashlimitburst,
                    hashlimitexpire=self.hashlimitexpire,
                    srcexclude=self.srcexclude,
                    loglevel=self.loglevel
                )
            )

            # Run after main process stops
            execstop = (
                '-{pyfp} {fp}/nfsinkhole-service.py '
                '--delete --interface {interface} --loglevel {loglevel}'.format(
                    pyfp=sys.executable,
                    fp=os.path.dirname(sys.executable),
                    interface=self.interface,
                    loglevel=self.loglevel
                )
            )

            if self.pcap:

                if self.packet_print:

                    # Main process, with tcp dump version >= 4.5.
                    # Output printed packets to /var/log/nfsinkhole-pcap.log.
                    execstart = (
                        '/usr/sbin/tcpdump '
                        '-nnlttttvvXXs 0 -i nflog >> '
                        '/var/log/nfsinkhole-pcap.log 2>&1 &'
                    )

                else:

                    # Main process, with tcp dump version < 4.5.
                    # Output to pcap file (/var/log/nfsinkhole.pcap),
                    # packet printing is not supported.
                    execstart = (
                        '/usr/sbin/tcpdump '
                        '-UnnttttvvXXs 0 -i '
                        'nflog -w /var/log/nfsinkhole.pcap '
                        '> /dev/null 2>&1 &'
                    )

                # Doesn't work with init.d
                if self.is_systemd:

                    execstart = '/bin/sh -c \'' + execstart + '\''

            else:

                # Run to keep service activated when tcpdump isn't used.
                execstart = ('/bin/sh -c \'/usr/bin/tail -f '
                             '/var/log/nfsinkhole-service.log &\'')

            # Write the systemd service
            if self.is_systemd:

                service.write(SYSTEMD_SERVICE_TEMPLATE.format(
                    svcexecstartpre=execstartpre,
                    svcexecstart=execstart,
                    svcexecstop=execstop
                ))

            # Write the init.d service
            else:
                service.write(INITD_SERVICE_TEMPLATE.format(
                    start='{0}\ndaemon {1}'.format(execstartpre[1:],
                                                   execstart),
                    stop=execstop[1:]
                ))

        # Write the temporary service file to svc_path
        # (/etc/init.d/nfsinkhole or /etc/systemd/system/nfsinkhole.service)
        subprocess.call(
            ['{0}/bin/sh -c \'cat nfsinkhole.service > '
             '{1}\''.format('/usr/bin/sudo ' if uid != 0 else '',
                            self.svc_path)],
            shell=True
        )

        # Set execute permission on svc_path
        # (/etc/init.d/nfsinkhole or /etc/systemd/system/nfsinkhole.service)
        cmd = ['chmod', '+x', self.svc_path]
        popen_wrapper(cmd, sudo=True)

        # Delete the temporary service file
        cmd = ['rm', 'nfsinkhole.service']
        popen_wrapper(cmd, sudo=True)

    def delete_service(self):
        """
        The function for deleting the init.d/systemd service.
        """

        log.info('Deleting nfsinkhole service')

        cmd = ['rm', self.svc_path]
        popen_wrapper(cmd, sudo=True)
