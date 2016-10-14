import logging
from nfsinkhole.tests import TestCommon
from nfsinkhole.apparmor import AppArmor
from nfsinkhole.utils import popen_wrapper

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestAppArmor(TestCommon):

    def test_disable_enforcement(self):

        # Passing
        apparmor = AppArmor()
        popen_wrapper(['touch', '/tmp/test_apparmor'], raise_err=True,
                      sudo=True)
        apparmor.disable_enforcement(module='/tmp/test_apparmor')

        # Manual fail
        apparmor.exists = False
        apparmor.disable_enforcement(module='/tmp/test_apparmor')

    def test_enable_enforcement(self):

        # Passing
        apparmor = AppArmor()
        popen_wrapper(['touch', '/tmp/test_apparmor'], raise_err=True,
                      sudo=True)
        apparmor.enable_enforcement(module='/tmp/test_apparmor')

        # Manual fail
        apparmor.exists = False
        apparmor.enable_enforcement(module='/tmp/test_apparmor')
