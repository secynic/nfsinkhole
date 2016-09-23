# Filename: setup.py

from distutils.core import setup
import io

NAME = 'nfsinkhole'
VERSION = '0.1.0'
AUTHOR = 'Philip Hane'
AUTHOR_EMAIL = 'secynic AT gmail DOT com'
DESCRIPTION = ('nfsinkhole is a Python library and scripts for setting up a '
               'Unix server as a sinkhole (monitor, log/capture, and drop all '
               'traffic to a secondary interface).')
KEYWORDS = [
    'Python'
]

README = io.open(file='README.rst', mode='r', encoding='utf-8').read()
CHANGES = io.open(file='CHANGES.rst', mode='r', encoding='utf-8').read()
LONG_DESCRIPTION = '\n\n'.join([README, CHANGES])
LICENSE = io.open(file='LICENSE.txt', mode='r', encoding='utf-8').read()

URL = 'https://github.com/secynic/nfsinkhole'
DOWNLOAD_URL = 'https://github.com/secynic/nfsinkhole/tarball/master'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Unix Shell',
    'Topic :: Internet',
    'Topic :: Security',
    'Topic :: System :: Networking',
    'Topic :: System :: Monitoring',
]

PACKAGES = ['nfsinkhole']

PACKAGE_DATA = {'nfsinkhole': []}

INSTALL_REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    keywords=KEYWORDS,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    scripts=['nfsinkhole/scripts/nfsinkhole-service.py',
             'nfsinkhole/scripts/nfsinkhole-setup.py']
)
