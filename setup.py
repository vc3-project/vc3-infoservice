#!/usr/bin/env python
#
# Setup prog for autopyfactory
#
#
# Since script is in package "certify" we can know what to add to path

import commands
import os
import re
import sys

from vc3 import infoservice
release_version=infoservice.__version__

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

# Python version check. 
major, minor, release, st, num = sys.version_info
if major == 2:
    if not minor >= 4:
        print("Autopyfactory requires Python >= 2.4. Exitting.")
        sys.exit(0)

# ===========================================================
#                D A T A     F I L E S 
# ===========================================================

libexec_files = ['libexec/%s' %file for file in os.listdir('libexec') if os.path.isfile('libexec/%s' %file)]

systemd_files = [ 'etc/vc3-service-info.service'
                 ]

etc_files = ['etc/vc3-infoservice.conf',
             ]

sysconfig_files = [
             'etc/sysconfig/vc3-infoservice',

]

logrotate_files = ['etc/logrotate/vc3-info-service',]

#initd_files = ['/vc3-info-service.init',
#               ]

# NOTES: the docs are actually handled by setup.cfg. They are moved directory under /usr/share/doc/autopyfactory-<version>/
#docs_files = ['docs/%s' %file for file in os.listdir('docs') if os.path.isfile('docs/%s' %file)]


# -----------------------------------------------------------

rpm_data_files=[('/usr/libexec', libexec_files),
                ('/etc/vc3', etc_files),
                ('/etc/sysconfig', sysconfig_files),
                ('/etc/logrotate.d', logrotate_files),                                        
#                ('/etc/init.d', initd_files),
                ('/usr/lib/systemd/system', systemd_files),
                #('/usr/share/doc/autopyfactory', docs_files),                                        
               ]


home_data_files=[('etc', libexec_files),
                 ('etc', etc_files),
#                 ('etc', initd_files),
                 ('etc', sysconfig_files),
                ]

# -----------------------------------------------------------

def choose_data_files():
    rpminstall = True
    userinstall = False
     
    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True
                
    if rpminstall:
        return rpm_data_files
    elif userinstall:
        return home_data_files
    else:
        # Something probably went wrong, so punt
        return rpm_data_files
       
# ===========================================================

# setup for distutils
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
    packages=['vc3',
              'vc3.plugins',
              ],
    scripts = [ # Utilities and main script
               'scripts/vc3-info-service',
              ],
    
    data_files = choose_data_files()
)
