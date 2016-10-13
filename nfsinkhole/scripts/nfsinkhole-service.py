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
import subprocess
import time
# TODO: generic errors via IPTablesError
from nfsinkhole.exceptions import (IPTablesError, IPTablesExists,
                                   IPTablesNotExists)
from nfsinkhole.iptables import IPTablesSinkhole
from nfsinkhole.utils import (ANSI, popen_wrapper, get_interface_addr)

# Setup the arg parser.
parser = argparse.ArgumentParser(
    description='nfsinkhole service script',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# Mututally exclusive arg group - must be --create OR --delete (not both)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    '--create',
    action='store_true',
    help='Perform the configuration.'
)
group.add_argument(
    '--delete',
    action='store_true',
    help='Remove the configuration.'
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
    default='0:65535',
    help='The destination port or range to log (for applicable protocols). '
         'Range should be in the format startport:endports'
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
    '--loglevel',
    type=str,
    default='info',
    choices=['debug', 'info', 'warning', 'error', 'critical'],
    help='Logging level for nfsinkhole events. This does not affect sinkhole '
         'traffic logs, only service/library event logs. Must be one of debug,'
         ' info, warning, error, critical.'
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

# Logging
LOG_FORMAT = ('[%(asctime)s.%(msecs)03d] [%(levelname)s] '
              '[%(filename)s:%(lineno)s] [%(funcName)s()] %(message)s')
logging.basicConfig(filename='/tmp/nfsinkhole-service.log', format=LOG_FORMAT,
                    level=getattr(logging, script_args.loglevel.upper()),
                    datefmt='%Y-%m-%dT%H:%M:%S')
logging.Formatter.converter = time.gmtime
log = logging.getLogger(__name__)
log.info('nfsinkhole-service.py called')

# Get the network interface info
interface = script_args.interface
interface_addr = get_interface_addr(interface)

if interface_addr:

    # Instantiate the iptable object with the script arguments.
    myobj = IPTablesSinkhole(
        interface=interface,
        interface_addr=interface_addr,
        log_prefix=script_args.prefix,
        protocol=script_args.protocol,
        dport=script_args.dport,
        hashlimit=script_args.hashlimit,
        hashlimitmode=script_args.hashlimitmode,
        hashlimitburst=script_args.hashlimitburst,
        hashlimitexpire=script_args.hashlimitexpire,
        srcexclude=script_args.srcexclude
    )

    # Delete the iptables configuration (not DROP statements)
    if script_args.delete:

        log.info('Deleting configuration (--delete).')

        try:

            myobj.delete_rules()

        except IPTablesError as e:

            log.info('An error occurred deleting the iptables rules: {0}'
                     ''.format(e))
            raise e

        except IPTablesNotExists as e:

            log.info('An error occurred deleting the iptables rules: {0}'
                     ''.format(e))
            pass

    # Create the iptables configuration (create DROP statements if missing)
    if script_args.create:

        log.info('Creating configuration (--create)')

        log.info('Creating iptables DROP rules for interface {0}. This should '
                 'fail under normal circumstances. '
                 'nfsinkhole-setup.py --install should have already done this.'
                 ''.format(script_args.interface))
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

        log.info('Creating iptables sinkhole logging rules for interface {0}'
                 ''.format(script_args.interface))
        try:

            myobj.create_rules()

        except (IPTablesError, IPTablesExists) as e:

            log.info('An error occurred creating the iptables rules: {0}'
                     ''.format(e))
            raise e

else:

    log.error('No address found for interface: {0}'.format(interface))

# Append the temporary service log to /var/log/nfsinkhole-service.log
subprocess.call(
    ['/bin/sh -c \'cat /tmp/nfsinkhole-service.log >> '
     '/var/log/nfsinkhole-service.log\''],
    shell=True
)

# Delete the temporary service log
popen_wrapper(['rm', '/tmp/nfsinkhole-service.log'])

# All done
log.info('Operations completed.')
