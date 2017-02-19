Changelog
=========

0.2.0 (TBD)
-----------

- Added syslog-ng support (#2)
- Added sudo arg to utils.popen_wrapper() - code consolidation
- Adding loglevel argument to scripts and service.SystemService (#5). Defaults
  to info. Travis defaults to debug.
- Fixed bytes to str decoding issue on Python 3
- Fixed splitlines list[bytes] decode on Python 3
- Logging output tweaks
- Fixed redundant TCPDump.check_packet_print() in nfsinkhole-setup.py
- Simplified utils.set_system_timezone(), removing unnecessary system calls.
- Python 3.6 support

0.1.0 (2016-08-29)
------------------

- Initial release