#!/usr/bin/env python
#
# Setup prog for infoservice

import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from vc3infoservice import infoservice
release_version = infoservice.__version__

systemd_files = ['etc/vc3-infoservice.service']

etc_files = ['etc/vc3-infoservice.conf',
             'etc/vc3-infoclient.conf',]

sysconfig_files = ['etc/sysconfig/vc3-infoservice', ]

logrotate_files = ['etc/logrotate/vc3-infoservice', ]

initd_files = ['etc/vc3-infoservice.init', ]

rpm_data_files = [('/etc/vc3', etc_files),
                  ('/etc/sysconfig', sysconfig_files),
                  ('/etc/logrotate.d', logrotate_files),
                  ('/etc/init.d', initd_files),
                  ('/usr/lib/systemd/system', systemd_files), ]


home_data_files = [('etc', etc_files),
                   ('etc', initd_files),
                   ('etc', sysconfig_files), ]


def choose_data_file_locations():
    rpm_install = True

    if 'bdist_rpm' in sys.argv:
        rpm_install = True

    elif '--user' in sys.argv:
        rpm_install = False

    elif any( [ re.match('--home(=|\s)', arg) for arg in sys.argv] ):
        rpm_install = False

    if rpm_install:
        return rpm_data_files
    else:
        return home_data_files

# ===========================================================

setup(
    name="vc3-info-service",
    version=release_version,
    description='vc3-info-service package',
    long_description='''This package contains the VC3 Information Service''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    maintainer='John Hover',
    maintainer_email='jhover@bnl.gov',
    url='https://github.com/vc3-project',
    packages=['vc3infoservice',
              'vc3infoservice.plugins',
              'vc3infoservice.plugins.persist'
              ],
    scripts=['scripts/vc3-info-service',
             'scripts/vc3-info-client',
             ],
    data_files=choose_data_file_locations(),
    install_requires=['cherrypy','pyopenssl']
)
