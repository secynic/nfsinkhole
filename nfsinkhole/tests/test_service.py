import logging
from nfsinkhole.tests import TestCommon
from nfsinkhole.service import SystemService

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestSystemService(TestCommon):

    def test_check_systemd(self):

        # TODO: this
        return

    def test_check_service(self):

        # TODO: this
        return

    def test_delete_service(self):

        # TODO: this
        return
