import logging
from nfsinkhole.exceptions import (IPTablesError, IPTablesExists,
                                   IPTablesNotExists, SubprocessError)
from nfsinkhole.iptables import IPTablesSinkhole
from nfsinkhole.tests import TestCommon

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestIPTablesSinkhole(TestCommon):

    def _test_create_drop_rule(self):

        # Bad interface
        myobj = IPTablesSinkhole(
            interface='~!@#$%^&*()',
        )
        myobj.create_drop_rule()

        # Success
        myobj = IPTablesSinkhole(
            interface='eth1',
        )
        myobj.create_drop_rule()

        # Exists
        self.assertRaises(IPTablesExists, myobj.create_drop_rule)

        # Content check
        expected = [
            '-A INPUT -i eth1 -j DROP',
            '-A OUTPUT -o eth1 -j DROP'
        ]
        existing = myobj.list_existing_rules(filter_io_drop=True)
        self.assertListEqual(existing, expected)

    def _test_delete_drop_rule(self):

        # Bad interface
        myobj = IPTablesSinkhole(
            interface='~!@#$%^&*()',
        )
        myobj.delete_drop_rule()
        self.assertRaises(IPTablesNotExists, myobj.delete_drop_rule)

        # Success
        myobj = IPTablesSinkhole(
            interface='eth1',
        )
        myobj.delete_drop_rule()

        # Exists
        self.assertRaises(IPTablesNotExists, myobj.delete_drop_rule)

    def test_drop_rule(self):

        self._test_create_drop_rule()
        self._test_delete_drop_rule()

    def _test_create_rules(self):

        # Success
        myobj = IPTablesSinkhole(
            interface='eth1',
            interface_addr='127.0.0.1',
            protocol='tcp',
            dport='0:53'
        )
        myobj.create_rules()

        # Exists
        self.assertRaises(IPTablesExists, myobj.create_rules)

    def _test_delete_rules(self):

        # Success
        myobj = IPTablesSinkhole(
            interface='eth1',
            interface_addr='127.0.0.1'
        )
        myobj.delete_rules()

        # Exists
        self.assertRaises(IPTablesNotExists, myobj.delete_rules)

    def test_rules(self):

        self._test_create_rules()
        self._test_delete_rules()
