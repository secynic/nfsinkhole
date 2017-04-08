import logging
from nfsinkhole.tests import TestCommon
from nfsinkhole.tcpdump import TCPDump

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestTCPDump(TestCommon):

    def test_check_packet_print(self):

        # TODO: this
        return

    def test_get_version(self):

        # TODO: this
        return
