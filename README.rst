==========
nfsinkhole
==========

.. image:: https://travis-ci.org/secynic/nfsinkhole.svg?branch=master
    :target: https://travis-ci.org/secynic/nfsinkhole
.. image:: https://coveralls.io/repos/github/secynic/nfsinkhole/badge.svg?branch=master&dummy=none
    :target: https://coveralls.io/github/secynic/nfsinkhole?branch=master
.. image:: https://img.shields.io/badge/license-BSD%202--Clause-blue.svg
    :target: https://github.com/secynic/nfsinkhole/tree/master/LICENSE.txt
.. image:: https://img.shields.io/badge/python-2.6%2C%202.7%2C%203.3+-blue.svg
.. image:: https://img.shields.io/badge/os-RHEL%2FCentOS%206%2F7-blue.svg
.. image:: https://img.shields.io/badge/docs-release%20v0.2.0-green.svg?style=flat
    :target: https://nfsinkhole.readthedocs.io/en/v0.2.0
.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
    :target: https://nfsinkhole.readthedocs.io/en/latest
.. image:: https://img.shields.io/badge/docs-dev-yellow.svg?style=flat
    :target: https://nfsinkhole.readthedocs.io/en/dev

Summary
=======

nfsinkhole is a Python library and scripts for setting up a Linux server
as a sinkhole (monitor, log/capture, and drop all traffic to a secondary
interface).

The default setup arguments monitor/capture all traffic. Setup arguments are
provided to configure protocols, ports, rate limiting, logging,
source IP/CIDR exclusions from logging, and optional packet capture.

All sinkhole events are written to /var/log/nfsinkhole-events.log. Optionally,
you can enable tcpdump to output packet capture text to
/var/log/nfsinkhole-pcap.log if your version of tcpdump supports packet
printing; otherwise reverts to /var/log/nfsinkhole.pcap.

.. warning::

    This version is considered experimental. Do not attempt to use this
    library in production until tests via travis and docker are setup, stable,
    and sufficiently covered.

.. attention::

    You are responsible for rotating log files (/var/log/nfsinkhole*), and
    syslog forwarding must be configured manually (automation pending).

Features
========

* Simple install script
* Installs as a init.d/systemctl service
* Service modifies iptables on start/stop, no need to persist iptables
* rsyslog and syslog-ng supported
* RedHat/CentOS 6/7 tested
* Python 2.6+ and 3.3+ supported
* Built-in support for dealing with SELinux/AppArmor
* Packet capture of sinkhole traffic (printed output to log for tcpdump v4.5+)
* Useful set of utilities
* Detailed logging to /var/log/nfsinkhole-*
* Syslog forwarding configuration (pending)
* BSD license

Planned Improvements
====================

* API/class documentation
* Tests via travis-ci/docker
* Exception handling overhaul
* Set logging level (currently debug)
* BIND/Microsoft/etc DNS server configuration documentation/examples
* Monitoring use case examples
* Automatic configuration for syslog forwarding
* SIEM parsers/apps/plugins
* Official support/testing for more OS environments
* Support handling exceptions for HIPS and other endpoint security products
* Intelligent handling/handshakes (inspired by iptrap -
  https://github.com/jedisct1/iptrap)

Links
=====

Documentation
-------------

Release v0.2.0
^^^^^^^^^^^^^^

https://nfsinkhole.readthedocs.io/en/v0.2.0

GitHub master
^^^^^^^^^^^^^

https://nfsinkhole.readthedocs.io/en/latest

GitHub dev
^^^^^^^^^^

https://nfsinkhole.readthedocs.io/en/dev

Examples
--------

Pending

Github
------

https://github.com/secynic/nfsinkhole

Pypi
----

https://pypi.python.org/pypi/nfsinkhole

Changes
-------

https://nfsinkhole.readthedocs.io/en/latest/CHANGES.html

Dependencies
============

OS::

    iptables (likely already included in base OS)
    tcpdump (optional - likely already included in base OS)

Python 2.6::

    argparse

Python 2.7, 3.3+::

    None!

Installing
==========

.. attention::

    The nfsinkhole service, iptables rules, and tcpdump must run as root.
    You can still use user/virtualenv Python environments, for the library,
    but ultimately, the core sinkhole will be run as root.

.. note::

    Replace any below occurence of <INTERFACE> with the name of your
    sinkhole network interface name.

Base OS (pip) -- RECOMMENDED
----------------------------

If pip is not installed, you will first need to add the EPEL repo and install::

    sudo yum install epel-release
    sudo yum install python-pip

RHEL/CentOS 6/7
^^^^^^^^^^^^^^^

Basic::

    pip install --user --upgrade nfsinkhole
    python ~/.local/bin/nfsinkhole-setup.py --interface <INTERFACE> --install --pcap

virtualenv::

    pip install virtualenv
    virtualenv nfsinkhole
    source nfsinkhole/bin/activate
    nfsinkhole/bin/pip install nfsinkhole
    nfsinkhole/bin/python nfsinkhole/bin/nfsinkhole-setup.py --interface <INTERFACE> --install --pcap

Base OS (no pip)
----------------

RHEL/CentOS 6
^^^^^^^^^^^^^

GitHub - Stable::

    wget -O argparse.tar.gz https://github.com/ThomasWaldmann/argparse/tarball/master
    tar -C argparse -zxvf argparse.tar.gz
    cd argparse
    python setup.py install --user prefix=
    cd ..
    rm -Rf argparse
    wget -O nfsinkhole.tar.gz https://github.com/secynic/nfsinkhole/tarball/master
    tar -C nfsinkhole -zxvf nfsinkhole.tar.gz
    cd nfsinkhole
    python setup.py install --user prefix=
    cd ..
    rm -Rf nfsinkhole
    python ~/.local/bin/nfsinkhole-setup.py --interface <INTERFACE> --install --pcap

RHEL/CentOS 7
^^^^^^^^^^^^^

GitHub - Stable::

    wget -O nfsinkhole.tar.gz https://github.com/secynic/nfsinkhole/tarball/master
    tar -C nfsinkhole -zxvf nfsinkhole.tar.gz
    cd nfsinkhole
    python setup.py install --user prefix=
    cd ..
    rm -Rf nfsinkhole
    python ~/.local/bin/nfsinkhole-setup.py --interface <INTERFACE> --install --pcap

Service
=======

Once installed you need to start the nfsinkhole service.

RHEL/CentOS 6
-------------

::

    sudo service nfsinkhole start

RHEL/CentOS 7
-------------

::

    sudo systemctl start nfsinkhole.service

API
===

AppArmor
--------

AppArmor documentation:

https://nfsinkhole.readthedocs.io/en/latest/apparmor.html

iptables
--------

iptables documentation:

https://nfsinkhole.readthedocs.io/en/latest/iptables.html

rsyslog
-------

rsyslog documentation:

https://nfsinkhole.readthedocs.io/en/latest/rsyslog.html

SELinux
-------

SELinux documentation:

https://nfsinkhole.readthedocs.io/en/latest/selinux.html

Service
-------

Service (systemd/init.d) documentation:

https://nfsinkhole.readthedocs.io/en/latest/service.html

syslog-ng
---------

syslog-ng documentation:

https://nfsinkhole.readthedocs.io/en/latest/syslog_ng.html

tcpdump
-------

tcpdump documentation:

https://nfsinkhole.readthedocs.io/en/latest/tcpdump.html

Utilities
---------

Utilities documentation:

https://nfsinkhole.readthedocs.io/en/latest/utils.html

Contributing
============

https://nfsinkhole.readthedocs.io/en/latest/CONTRIBUTING.html

Special Thanks
==============

Thank you JetBrains for the `PyCharm <https://www.jetbrains.com/pycharm/>`_
open source support!
