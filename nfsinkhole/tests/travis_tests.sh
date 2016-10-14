#!/bin/bash
export PS4='\033[32m+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }\033[0m'
set -eo xtrace

if [ "${TRAVIS_PYTHON_VERSION}" = "2.7" ]; then
    sudo docker pull centos:7
    sudo docker network create --driver=bridge sinknet --subnet=172.19.0.0/24
    sudo docker run -d -e "container=docker" -v /sys/fs/cgroup:/sys/fs/cgroup --privileged --name nfsinkholevm -t centos:7 /usr/sbin/init
    sudo docker network connect sinknet nfsinkholevm
    sudo docker ps -a | grep nfsinkholevm
    sudo docker network ls
    sudo docker cp ${TRAVIS_BUILD_DIR} nfsinkholevm:/root/nfsinkhole
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install net-tools"
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install iptables"
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install tcpdump"
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install rsyslog"
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install epel-release && yum clean all"
    sudo docker exec nfsinkholevm /bin/sh -c "yum -y -q install python-pip && yum clean all"
    sudo docker exec nfsinkholevm /bin/sh -c "pip install nose"
    sudo docker exec nfsinkholevm /bin/sh -c "ifconfig"
    sudo docker exec nfsinkholevm /bin/sh -c "ls -al /root/nfsinkhole"
    sudo docker exec nfsinkholevm /bin/sh -c "cd /root/nfsinkhole/ && python setup.py install"
    sudo docker exec nfsinkholevm /bin/sh -c "nosetests -v -w /root/nfsinkhole/nfsinkhole --include=docker --with-coverage --cover-package=nfsinkhole"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --install --pcap --loglevel debug"
    sudo docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "systemctl start nfsinkhole.service"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service"
    sudo docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    sudo docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "systemctl stop nfsinkhole.service"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "systemctl status nfsinkhole.service || true"
    sudo docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-service.log && rm /var/log/nfsinkhole-service.log"
    sudo docker exec nfsinkholevm /bin/sh -c "ps aux | grep /usr/sbin/tcpdump"
    sudo docker exec --privileged nfsinkholevm /bin/sh -c "python /usr/bin/nfsinkhole-setup.py --interface eth1 --uninstall --loglevel debug"
    sudo docker exec nfsinkholevm /bin/sh -c "cat /var/log/nfsinkhole-setup.log && rm /var/log/nfsinkhole-setup.log"
    sudo docker exec nfsinkholevm /bin/sh -c "find / -name \\\'*.coverage\\\'"
    sudo docker cp nfsinkholevm:/root/nfsinkhole/*.coverage .
    coveralls --rcfile=.coveragerc
fi