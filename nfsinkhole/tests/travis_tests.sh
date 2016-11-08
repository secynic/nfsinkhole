#!/bin/bash
export PS4='\033[32m+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }\033[0m'
set -eo xtrace

if [ "${TRAVIS_PYTHON_VERSION}" = "2.6" ]; then

    docker pull centos:6
    docker network create --driver=bridge sinknet --subnet=172.19.0.0/24
    docker run -d -e "container=docker" -v /sys/fs/cgroup:/sys/fs/cgroup --privileged --name nfsinkholevm -t centos:6 /usr/sbin/init
    docker network connect sinknet nfsinkholevm
    docker ps -a | grep nfsinkholevm
    docker network ls

    # Use the same directory structure as Travis host. This is to avoid path issues with .coverage
    docker exec nfsinkholevm /bin/sh -c "mkdir /home/travis && mkdir /home/travis/build && mkdir /home/travis/build/secynic"

    docker cp ${TRAVIS_BUILD_DIR} nfsinkholevm:/home/travis/build/secynic/nfsinkhole
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install net-tools"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install iptables"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install tcpdump"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install rsyslog"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install epel-release && yum clean all"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install python-pip && yum clean all"
    docker exec nfsinkholevm /bin/sh -c "pip install coverage"
    docker exec nfsinkholevm /bin/sh -c "pip install nose"
    docker exec nfsinkholevm /bin/sh -c "ifconfig"
    docker exec nfsinkholevm /bin/sh -c "ls -al /home/travis/build/secynic/nfsinkhole"
    docker exec nfsinkholevm /bin/sh -c "cd /home/travis/build/secynic/nfsinkhole/ && python setup.py install"
    docker exec nfsinkholevm /bin/sh -c "cd /home/travis/build/secynic/nfsinkhole/ && nosetests -v -w /home/travis/build/secynic/nfsinkhole/nfsinkhole --include=docker --with-coverage --cover-package=nfsinkhole"
    docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --install --pcap --loglevel debug"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl start nfsinkhole.service"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl stop nfsinkhole.service"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service || true"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --uninstall --loglevel debug"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    docker cp nfsinkholevm:/home/travis/build/secynic/nfsinkhole/.coverage /home/travis/build/secynic/nfsinkhole
    coveralls --rcfile=.coveragerc

elif [ "${TRAVIS_PYTHON_VERSION}" = "2.7" ]; then

    docker pull centos:7
    docker network create --driver=bridge sinknet --subnet=172.19.0.0/24
    docker run -d -e "container=docker" -v /sys/fs/cgroup:/sys/fs/cgroup --privileged --name nfsinkholevm -t centos:7 /usr/sbin/init
    docker network connect sinknet nfsinkholevm
    docker ps -a | grep nfsinkholevm
    docker network ls

    # Use the same directory structure as Travis host. This is to avoid path issues with .coverage
    docker exec nfsinkholevm /bin/sh -c "mkdir /home/travis && mkdir /home/travis/build && mkdir /home/travis/build/secynic"

    docker cp ${TRAVIS_BUILD_DIR} nfsinkholevm:/home/travis/build/secynic/nfsinkhole
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install net-tools"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install iptables"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install tcpdump"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install rsyslog"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install epel-release && yum clean all"
    docker exec nfsinkholevm /bin/sh -c "yum -y -q install python-pip && yum clean all"
    docker exec nfsinkholevm /bin/sh -c "pip install coverage"
    docker exec nfsinkholevm /bin/sh -c "pip install nose"
    docker exec nfsinkholevm /bin/sh -c "ifconfig"
    docker exec nfsinkholevm /bin/sh -c "ls -al /home/travis/build/secynic/nfsinkhole"
    docker exec nfsinkholevm /bin/sh -c "cd /home/travis/build/secynic/nfsinkhole/ && python setup.py install"
    docker exec nfsinkholevm /bin/sh -c "cd /home/travis/build/secynic/nfsinkhole/ && nosetests -v -w /home/travis/build/secynic/nfsinkhole/nfsinkhole --include=docker --with-coverage --cover-package=nfsinkhole"
    docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --install --pcap --loglevel debug"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl start nfsinkhole.service"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl stop nfsinkhole.service"
    docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service || true"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --uninstall --loglevel debug"
    docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    docker cp nfsinkholevm:/home/travis/build/secynic/nfsinkhole/.coverage /home/travis/build/secynic/nfsinkhole
    coveralls --rcfile=.coveragerc
fi