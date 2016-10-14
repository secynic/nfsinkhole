import logging
from nfsinkhole.exceptions import SubprocessError
from nfsinkhole.tests import TestCommon
from nfsinkhole.utils import (popen_wrapper, get_default_interface,
                              get_interface_addr, set_system_timezone)

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestIPTablesSinkhole(TestCommon):

    def test_popen_wrapper(self):

        # Argument checks
        self.assertRaises(ValueError, popen_wrapper)
        self.assertRaises(TypeError, popen_wrapper, 'notalist')
        self.assertNotEqual(popen_wrapper(['ls'], log_stdout_line=False), None)
        self.assertNotEqual(get_interface_addr('eth0'), None)
        self.assertEqual(get_interface_addr('asdasd'), None)

        # raise_err test
        self.assertRaises(SubprocessError, popen_wrapper, **dict(
            cmd_arr=['asdasd'],
            raise_err=True
        ))

    def test_get_default_interface(self):

        self.assertNotEqual(get_default_interface(), None)

    def test_set_system_timezone(self):

        set_system_timezone('UTC')
        set_system_timezone('UTC', skip_timedatectl=True)
