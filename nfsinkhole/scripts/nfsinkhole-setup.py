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

import argparse
import logging
import os
import subprocess
import time
from nfsinkhole.apparmor import AppArmor
from nfsinkhole.exceptions import (IPTablesError, IPTablesExists,
                                   IPTablesNotExists, BinaryNotFound)
from nfsinkhole.iptables import IPTablesSinkhole
from nfsinkhole.rsyslog import RSyslog
from nfsinkhole.service import SystemService
from nfsinkhole.syslog_ng import SyslogNG
from nfsinkhole.utils import (ANSI, popen_wrapper, set_system_timezone)

# TODO: add --log_level arg, currently set to debug
LOG_FORMAT = ('[%(asctime)s.%(msecs)03d] [%(levelname)s] '
              '[%(filename)s:%(lineno)s] [%(funcName)s()] %(message)s')
logging.basicConfig(filename='nfsinkhole-setup.log', format=LOG_FORMAT,
                    level=logging.DEBUG, datefmt='%Y-%m-%dT%H:%M:%S')
logging.Formatter.converter = time.gmtime
log = logging.getLogger(__name__)
log.debug('nfsinkhole-setup.py called')
uid = os.geteuid()  # Unix req; autodoc_mock_imports for Sphinx cross platform

scripts_dir = os.path.dirname(os.path.realpath(__file__))

# Setup the arg parser.
parser = argparse.ArgumentParser(
    description='nfsinkhole service setup script',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# Mututally exclusive arg group - must be --install OR --uninstall (not both)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    '--install',
    action='store_true',
    help='Install the service.\nSinkhole events will be logged to '
         '/var/log/nfsinkhole-events.log\n'
         '{0}{1}Warning:{2}{3} If you are running SELinux, --install will run '
         '/sbin/restorecon -v /etc/rsyslog.d/nfsinkhole.conf, '
         'relabeling the config to allow it in SELinux. '
         'rsyslog will also be restarted.{4}'
         ''.format(
            ANSI['red'], ANSI['b'], ANSI['end'], ANSI['red'], ANSI['end']
         )
)
group.add_argument(
    '--uninstall',
    action='store_true',
    help='Uninstall the service. This will also delete '
         '/etc/rsyslog.d/nfsinkhole.conf and restart rsyslog.'
)

parser.add_argument(
    '--protocol',
    type=str,
    default='all',
    help='The protocol(s) to log (all traffic will still be dropped). Accepts '
         'a comma separated string of protocols '
         '(tcp,udp,udplite,icmp,esp,ah,sctp) or all.'
)

parser.add_argument(
    '--dport',
    type=str,
    default='"0:65535"',
    help='The destination ports range to log (for applicable protocols). '
         'Range should be in the format startport:endports or '
)

parser.add_argument(
    '--prefix',
    type=str,
    default='"[nfsinkhole] "',
    help='Prefix for syslog messages.'
)

parser.add_argument(
    '--hashlimit',
    type=str,
    default='1/h',
    help='Set the hashlimit rate. Hashlimit is used to tune the amount of '
         'events logged. See the iptables-extensions docs: '
         'http://ipset.netfilter.org/iptables-extensions.man.html'
)

parser.add_argument(
    '--hashlimitmode',
    type=str,
    default='srcip,dstip,dstport',
    help='Set the hashlimit mode, a comma separated string of options '
         '(srcip,srcport,dstip,dstport). More options here results in more '
         'logs generated.'
)

parser.add_argument(
    '--hashlimitburst',
    type=str,
    default='1',
    help='Maximum initial number of packets to match.'
)

parser.add_argument(
    '--hashlimitexpire',
    type=str,
    default='3600000',
    help='Number of milliseconds to keep entries in the hash table.'
)

parser.add_argument(
    '--srcexclude',
    type=str,
    default='127.0.0.1',
    help='Exclude a comma separated string of source IPs/CIDRs from logging.'
)

parser.add_argument(
    '--pcap',
    action='store_true',
    help='Enable packet capture text to /var/log/nfsinkhole-pcap.log.\n'
         '{0}{1}Warning:{2}{3} if this argument is provided, and you are '
         'running AppArmor, --create will disable '
         '/etc/apparmor.d/usr.sbin.tcpdump so tcpdump can monitor NFLOG. '
         'Running --uninstall will revert these modifications.{4}'
         ''.format(
            ANSI['red'], ANSI['b'], ANSI['end'], ANSI['red'], ANSI['end']
         )
)

# Input (required)
group = parser.add_argument_group('Input (Required)')

group.add_argument(
    '--interface',
    type=str,
    help='The secondary network interface dedicated to sinkhole traffic. '
         '{0}{1}Warning:{2}{3} Do not accidentally set this to your primary '
         'interface. It will drop all traffic, and kill your remote access.{4}'
         ''.format(
            ANSI['red'], ANSI['b'], ANSI['end'], ANSI['red'], ANSI['end']
         ),
    required=True
)

# Get the args
script_args = parser.parse_args()

# Check if systemd or legacy
system_service = SystemService(
    interface=script_args.interface,
    protocol=script_args.protocol,
    dport=script_args.dport,
    log_prefix=script_args.prefix,
    hashlimit=script_args.hashlimit,
    hashlimitmode=script_args.hashlimitmode,
    hashlimitburst=script_args.hashlimitburst,
    hashlimitexpire=script_args.hashlimitexpire,
    srcexclude=script_args.srcexclude,
    pcap=script_args.pcap
)
is_systemd, svc_path = system_service.check_systemd()

try:

    # Get the rsyslog version
    r_syslog = RSyslog(is_systemd)
    rsyslog_version = r_syslog.get_version()
    syslog_ng = None

except BinaryNotFound:

    r_syslog = None
    rsyslog_version = None

    # Get the syslog-ng version
    syslog_ng = SyslogNG(is_systemd)
    syslog_ng_version = syslog_ng.get_version()

# Initialize the AppArmor object
app_armor = AppArmor()

if script_args.uninstall:

    log.info('Deleting nfsinkhole configuration (--uninstall)')

    log.info('Deleting iptables DROP rules for interface {0}'.format(
        script_args.interface
    ))
    myobj = IPTablesSinkhole(
        interface=script_args.interface,
    )

    try:

        myobj.delete_drop_rule()

    except IPTablesError as e:

        log.info('An error occurred deleting the iptables DROP rules: {0}'
                 ''.format(e))
        raise e

    except IPTablesNotExists as e:

        log.info('An error occurred deleting the iptables DROP rules: {0}'
                 ''.format(e))
        pass

    if app_armor.exists and script_args.pcap:

        log.info('AppArmor found and --pcap provided, enabling enforcement '
                 'for usr.sbin.tcpdump')
        app_armor.enable_enforcement('usr.sbin.tcpdump')

    if r_syslog:

        log.info('Deleting rsyslog config for nfsinkhole')
        r_syslog.delete_config()

        log.info('Restarting rsyslog')
        r_syslog.restart()

    else:

        log.info('Deleting syslog-ng config for nfsinkhole')
        syslog_ng.delete_config()

        log.info('Restarting syslog-ng')
        syslog_ng.restart()

    log.info('Deleting nfsinkhole service')
    system_service.delete_service()

if script_args.install:

    log.info('Configuring nfsinkhole (--install)')

    log.info('Creating iptables DROP rules for interface {0}'.format(
        script_args.interface
    ))
    myobj = IPTablesSinkhole(
        interface=script_args.interface,
    )

    try:

        myobj.create_drop_rule()

    except IPTablesError as e:

        log.info('An error occurred creating the iptables DROP rules: {0}'
                 ''.format(e))
        raise e

    except IPTablesExists as e:

        log.info('An error occurred creating the iptables DROP rules: {0}'
                 ''.format(e))
        pass

    log.info('Setting system timezone to UTC')
    set_system_timezone('UTC')

    if app_armor.exists and script_args.pcap:

        log.info('AppArmor found and --pcap provided, disabling enforcement '
                 'for usr.sbin.tcpdump')
        app_armor.disable_enforcement('usr.sbin.tcpdump')

    if r_syslog:

        log.info('Writing rsyslog config')
        r_syslog.create_config(script_args.prefix)

        log.info('Associating rsyslog config with SELinux')
        r_syslog.selinux_associate()

        log.info('Restarting rsyslog')
        r_syslog.restart()

    else:

        log.info('Checking syslog-ng conf.d')
        syslog_ng.check_confd()

        log.info('Writing syslog-ng config')
        syslog_ng.create_config(script_args.prefix)

        log.info('Associating syslog-ng config with SELinux')
        syslog_ng.selinux_associate()

        log.info('Restarting syslog-ng')
        syslog_ng.restart()

    log.info('Generating and writing nfsinkhole service')
    system_service.create_service()


# Append the temporary setup log to /var/log/nfsinkhole-setup.log
subprocess.call(
    ['{0}/bin/sh -c \'cat nfsinkhole-setup.log >> '
     '/var/log/nfsinkhole-setup.log\''.format(
        '/usr/bin/sudo ' if uid != 0 else '')],
    shell=True
)

# Delete the temporary setup log
popen_wrapper(['rm', 'nfsinkhole-setup.log'])

# All done
log.info('Operations completed.')
