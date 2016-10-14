import logging
from nfsinkhole.tests import TestCommon
from nfsinkhole.selinux import SELinux
from nfsinkhole.utils import popen_wrapper

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestSELinux(TestCommon):

    def test_associate(self):

        # Passing
        selinux = SELinux()
        popen_wrapper(['touch', '/tmp/test_selinux'], raise_err=True,
                      sudo=True)
        selinux.associate(path='/tmp/test_selinux')

        # Manual fail
        selinux.exists = False
        selinux.associate(path='/tmp/test_selinux')
