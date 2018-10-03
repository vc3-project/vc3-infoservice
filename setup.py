#!/usr/bin/env python
#
# Setup prog for infoservice

import sys
import re
import time
from setuptools import setup


def choose_data_file_locations():
    local_install = False

    if '--user' in sys.argv:
        local_install = True
    elif any([re.match('--home(=|\s)', arg) for arg in sys.argv]):
        local_install = True
    elif any([re.match('--prefix(=|\s)', arg) for arg in sys.argv]):
        local_install = True

    if local_install:
        return home_data_files
    else:
        return rpm_data_files

current_time = time.gmtime()
#release_version = "{0}.{1:0>2}.{2:0>2}".format(current_time.tm_year, current_time.tm_mon, current_time.tm_mday)
release_version = '1.1.0'

systemd_files = ['etc/vc3-infoservice.service']

etc_files = ['etc/vc3-infoservice.conf',
             'etc/vc3-infoclient.conf',]

sysconfig_files = ['etc/sysconfig/vc3-infoservice', ]

logrotate_files = ['etc/logrotate/vc3-infoservice', ]

initd_files = ['etc/vc3-infoservice.init.DONTUSE', ]

rpm_data_files = [('/etc/vc3', etc_files),
                  ('/etc/sysconfig', sysconfig_files),
                  ('/etc/logrotate.d', logrotate_files),
                  ('/etc/init.d', initd_files),
                  ('/usr/lib/systemd/system', systemd_files), ]

home_data_files = [('etc', etc_files),
                   ('etc', initd_files),
                   ('etc', sysconfig_files), ]

data_files = choose_data_file_locations()

# ===========================================================

setup(
    name="vc3-infoservice",
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
    scripts=['scripts/vc3-infoservice',
             'scripts/vc3-infoclient',
             ],
    data_files=data_files,
    install_requires=['cherrypy','pyopenssl','pluginmanager']
)

