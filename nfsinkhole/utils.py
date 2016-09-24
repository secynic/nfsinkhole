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

from .exceptions import SubprocessError
import fcntl  # Unix req; autodoc_mock_imports for Sphinx cross platform
import logging
import os
import socket
import struct
import subprocess

log = logging.getLogger(__name__)
uid = os.geteuid()  # Unix req; autodoc_mock_imports for Sphinx cross platform

# CLI ANSI rendering
ANSI = {
    'end': '\033[0m',
    'b': '\033[1m',
    'ul': '\033[4m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'cyan': '\033[36m'
}


def popen_wrapper(cmd_arr=None, raise_err=False, log_stdout_line=True):
    """
    The function for subprocess with custom logging output.

    Args:
        cmd_arr: Array of command strings to pass to subprocess.Popen().
        raise_err: If stderr is encountered, raise SubprocessError.
        log_stdout_line: If True, logs each stdout line as a separate log
            entry. If False, logs all of stdout in a single log entry.

    Returns:
        Tuple: stdout, stderr of the completed subprocess.

    Raises:
        ValueError: cmd_arr argument is not provided or is None.
        TypeError: cmd_arr argument is not a list.
        SubprocessError: The subprocess encountered an error (stderr).
            raise_err must be True for this.
    """

    log.debug('Running: {0}'.format(' '.join(cmd_arr)))

    if not cmd_arr:
        raise ValueError('cmd_arr is required (list of commands)')

    if not isinstance(cmd_arr, list):
        raise TypeError('cmd_arr must be a list of commands')

    # Create a subprocess for the command, piping stdout, with stderr to
    # stdout for logging.
    try:
        proc = subprocess.Popen(
            cmd_arr,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        # Command is done, get the stdout.
        out, err = proc.communicate()
    except OSError as e:
        out = None
        err = 'subprocess OSError: {0}'.format(e)

    # Each stdout line is a log entry.
    if log_stdout_line:

        # Iterate subprocess stdout, and write to the debug log.
        out_arr = out.splitlines(True) if out else []
        for line in out_arr:

            log.debug('[{0}] {1}'.format(
                ' '.join(cmd_arr),
                line.replace(b'\n', b'').decode('ascii', 'ignore')
            ))

    # Log stdout as a single entry.
    elif out:

        log.debug('[{0}] {1}'.format(' '.join(cmd_arr), out))

    # Iterate subprocess stderr, and write to the error log.
    err_arr = err.splitlines(True) if err else []
    for line in err_arr:
        log.error('[{0}] {1}'.format(
            ' '.join(cmd_arr),
            line.replace(b'\n', b'').decode('ascii', 'ignore')
        ))

    # If any errors, iterate them and write to log, then raise
    # SubprocessError.
    if raise_err and err:
        arr = err.splitlines()
        raise SubprocessError(
            'Error encountered when running process "{0}":\n{1}'.format(
                ' '.join(cmd_arr), b'\n'.join(arr).decode('ascii', 'ignore')
            )
        )

    return out, err


def get_default_interface():
    """
    The function for getting the default Unix network interface
    address.

    Returns:
        String: The network interface name, or None.
    """

    log.info('Retrieving default interface')

    # Get interface for default route. Borrowed from
    # http://stackoverflow.com/a/33550399 (colin-fletcher)
    out, err = popen_wrapper([
        'netstat', '-', 'rn', '|', 'awk',
        '/^0.0.0.0/ {thif=substr($0,74,10); print thif;} /^default.*UG/ '
        '{thif=substr($0,65,10); print thif;}'
    ])

    default_interface = None
    if out and len(out) > 0:

        default_interface = out
        log.info('Default network interface found: {0}'
                 ''.format(default_interface))

    else:

        log.info('Default network interface not found')

    return default_interface


def get_interface_addr(interface=None):
    """
    The function for automatically determining a Unix network interface
    address.

    Args:
        interface: The network interface name.

    Returns:
        String: The IP address for the interface, or None.
    """

    log.info('Retrieving address for interface {0}'.format(interface))

    log.debug('Creating socket...'.format(interface))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Query the interface and attempt to get the IP. Fail if interface is down.
    log.debug('Attempting IP extract/conversion... '.format(interface))
    try:

        # TODO: is this faster than ifconfig/ip route parsing?
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', interface[:15])
            )[20:24]
        )

    except IOError:

        log.error('Could not get an address for interface {0}. Is it up?'
                  ''.format(interface))
        return None


def set_system_timezone(timezone='UTC'):
    """
    The function for setting the system timezone.

    Args:
        timezone: The timezone to set, see /usr/share/zoneinfo/* for options.

    Raises:
        SubprocessError: One of the processes associated with manual timezone
            configuration encountered an error.
    """

    log.info('Setting system timzone to {0}.'.format(timezone))

    # Try setting the timzone with timedatectl
    cmd = ['timedatectl', 'set-timezone', timezone]

    # run sudo if not root
    if uid != 0:
        cmd = ['/usr/bin/sudo'] + cmd

    out, err = popen_wrapper(cmd)

    if out or err:

        # timedatectl failed or missing, set /etc/localtime manually
        log.info('Reverting to manual timezone config (no timedatectl, or '
                 'errors).'.format(timezone))

        # Backup localtime to /root/localtime.old
        cmd = ['cp', '/etc/localtime', '/root/localtime.old']

        # run sudo if not root
        if uid != 0:
            cmd = ['/usr/bin/sudo'] + cmd

        out, err = popen_wrapper(cmd, raise_err=True)

        # stdout is not expected on success.
        if out and len(out) > 0:
            raise SubprocessError(out)

        # Remove /etc/localtime
        cmd = ['rm', '/etc/localtime']

        # run sudo if not root
        if uid != 0:
            cmd = ['/usr/bin/sudo'] + cmd

        out, err = popen_wrapper(cmd, raise_err=True)

        # stdout is not expected on success.
        if out and len(out) > 0:
            raise SubprocessError(out)

        # Create symbolic link to /usr/share/zoneinfo/{timezone} for
        # /etc/localtime
        cmd = [
            'ln', '-s', '/usr/share/zoneinfo/{0}'.format(timezone),
            '/etc/localtime'
        ]

        # run sudo if not root
        if uid != 0:
            cmd = ['/usr/bin/sudo'] + cmd

        out, err = popen_wrapper(cmd, raise_err=True)

        # stdout is not expected on success.
        if out and len(out) > 0:
            raise SubprocessError(out)
