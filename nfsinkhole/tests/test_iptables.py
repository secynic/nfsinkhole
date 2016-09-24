import logging
from nfsinkhole.exceptions import (IPTablesError, IPTablesExists,
                                   IPTablesNotExists, SubprocessError)
from nfsinkhole.iptables import IPTablesSinkhole
from nfsinkhole.tests import TestCommon
from nfsinkhole.utils import (popen_wrapper, set_system_timezone)

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestIPTablesSinkhole(TestCommon):

    def test_drop(self):

        # Bad interface
        myobj = IPTablesSinkhole(
            interface='~!@#$%^&*()',
        )
        myobj.create_drop_rule()
        self.assertRaises(IPTablesExists, myobj.create_drop_rule)

        # Success
        myobj = IPTablesSinkhole(
            interface='eth1',
        )
        myobj.create_drop_rule()

        # Exists
        self.assertRaises(IPTablesExists, myobj.create_drop_rule)

    # TODO: move to test_utils.py
    def test_timezone(self):

        set_system_timezone('UTC')

        # Remove /etc/localtime
        out, err = popen_wrapper(['rm', '/usr/bin/timedatectl'],
                                 raise_err=True, sudo=True)

        # stdout is not expected on success.
        if (out or err) and (len(out) > 0 or len(err) > 0):
            raise SubprocessError('{0}{1}'.format(
                '{0}\n'.format(out) if out else '',
                '{0}\n'.format(err) if err else ''
            ))

        # Create bad symbolic link
        cmd = ['ln', '-s', '/usr/bin/sudo', '/usr/bin/timedatectl']
        out, err = popen_wrapper(cmd, raise_err=True, sudo=True)

        # stdout is not expected on success.
        if (out or err) and (len(out) > 0 or len(err) > 0):
            raise SubprocessError('{0}{1}'.format(
                '{0}\n'.format(out) if out else '',
                '{0}\n'.format(err) if err else ''
            ))

        # Remove /etc/localtime
        out, err = popen_wrapper(['rm', '/etc/localtime'],
                                 raise_err=True, sudo=True)

        # stdout is not expected on success.
        if (out or err) and (len(out) > 0 or len(err) > 0):
            raise SubprocessError('{0}{1}'.format(
                '{0}\n'.format(out) if out else '',
                '{0}\n'.format(err) if err else ''
            ))

        # localtime is removed, set_system_timezone should fail on copy attempt
        self.assertRaises(SubprocessError, set_system_timezone, 'UTC')
