import logging
from nfsinkhole.tests import TestCommon
from nfsinkhole.rsyslog import RSyslog

LOG_FORMAT = ('[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)s] '
              '[%(funcName)s()] %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)


class TestRSyslog(TestCommon):

    def test_get_version(self):

        # TODO: this
        return

    def test_selinux_associate(self):

        # TODO: this
        return

    def test_create_config(self):

        # TODO: this
        return

    def test_delete_config(self):

        # TODO: this
        return

    def test_restart(self):

        # TODO: this
        return
