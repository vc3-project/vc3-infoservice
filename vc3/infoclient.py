#!/bin/env python

import logging
import logging.handlers
import requests
import urllib
import urllib3
import os
import platform
#import pwd
#import random
#import string
#import socket
import requests
import sys
#import threading
import time
import traceback

from optparse import OptionParser
from ConfigParser import ConfigParser



logging.captureWarnings(True)

TESTKEY='testkey'
TESTDOC='''{
    "uchicago_rcc": {
        "base" : {
            "distribution": "redhat",
            "release": "6.7",
            "architecture": "x86_64"
        }
    }
}'''

class InfoClient(object):
    def __init__(self, config):
        self.log = logging.getLogger()
        self.log.debug('InfoClient class init...')
        self.config = config
        self.certfile = os.path.expanduser(config.get('netcomm','certfile'))
        self.keyfile = os.path.expanduser(config.get('netcomm', 'keyfile'))
        self.chainfile = os.path.expanduser(config.get('netcomm','chainfile'))
        self.httpport = int(config.get('netcomm','httpport'))
        self.httpsport = int(config.get('netcomm','httpsport'))
        self.infohost = os.path.expanduser(config.get('netcomm','infohost'))
      
        self.log.debug("Client initialized.")

    # test storedocument?key=X,doc=y, 
    # test getdocument?key=X
    def storedocument(self, key, doc):
        doc = urllib.quote_plus(doc)
        
        u = "https://%s:%s/storedocument?key=%s&doc='%s'" % (self.infohost, 
                            self.httpsport,
                            key,
                            doc
                            )
        try:
            r = requests.get(u, verify=self.chainfile)
            print(r.text)
            print(r.status_code)
        
        except requests.exceptions.ConnectionError, ce:
            print('Connection failure. %s' % ce)

    def getdocument(self, key):
        u = "https://%s:%s/getdocument?key=%s" % (self.infohost, 
                            self.httpsport,
                            key
                            )
        try:
            r = requests.get(u, verify=self.chainfile)
            print(r.text)
            print(r.status_code)
        
        except requests.exceptions.ConnectionError, ce:
            print('Connection failure. %s' % ce)
        
    def testquery(self):
        self.log.info("Testing storedocument. Doc = %s" % TESTDOC)
        self.storedocument(key=TESTKEY,doc=TESTDOC)
        
        self.log.info("Testing getdocument...")
        self.getdocument(key=TESTKEY)
        self.log.info("Done.")

class InfoClientCLI(object):
    """class to handle the command line invocation of APF. 
       parse the input options,
       setup everything, and run Factory class
    """
    def __init__(self):
        self.options = None 
        self.args = None
        self.log = None
        self.config = None

        self.__presetups()
        self.__parseopts()
        self.__setuplogging()
        self.__platforminfo()
        self.__createconfig()
        
    def __presetups(self):
        '''
        we put here some preliminary steps that 
        for one reason or another 
        must be done before anything else
        '''
    
    def __parseopts(self):
        parser = OptionParser(usage='''%prog [OPTIONS]
vc3-info-client is a client for the information store for VC3

This program is licenced under the GPL, as set out in LICENSE file.

Author(s):
John Hover <jhover@bnl.gov>
''', version="%prog $Id: infocliente.py 1-31-17 23:58:06Z jhover $" )

        parser.add_option("-d", "--debug", 
                          dest="logLevel", 
                          default=logging.WARNING,
                          action="store_const", 
                          const=logging.DEBUG, 
                          help="Set logging level to DEBUG [default WARNING]")
        parser.add_option("-v", "--info", 
                          dest="logLevel", 
                          default=logging.WARNING,
                          action="store_const", 
                          const=logging.INFO, 
                          help="Set logging level to INFO [default WARNING]")
        parser.add_option("--console", 
                          dest="console", 
                          default=False,
                          action="store_true", 
                          help="Forces debug and info messages to be sent to the console")
        parser.add_option("--quiet", dest="logLevel", 
                          default=logging.WARNING,
                          action="store_const", 
                          const=logging.WARNING, 
                          help="Set logging level to WARNING [default]")
        parser.add_option("--conf", dest="confFiles", 
                          default="~/etc/vc3/vc3-infoclient.conf",
                          action="store", 
                          metavar="FILE1[,FILE2,FILE3]", 
                          help="Load configuration from FILEs (comma separated list)")
        parser.add_option("--log", dest="logfile", 
                          default="syslog", 
                          metavar="LOGFILE", 
                          action="store", 
                          help="Send logging output to LOGFILE or SYSLOG or stdout [default <syslog>]")
        (self.options, self.args) = parser.parse_args()
        self.options.confFiles = self.options.confFiles.split(',')

    def __setuplogging(self):
        """ 
        Setup logging 
        """
        self.log = logging.getLogger()
        if self.options.logfile == "stdout":
            logStream = logging.StreamHandler()
        elif self.options.logfile == 'syslog':
            logStream = logging.handlers.SysLogHandler('/dev/log')
        else:
            lf = self.options.logfile
            logdir = os.path.dirname(lf)
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            runuid = pwd.getpwnam(self.options.runAs).pw_uid
            rungid = pwd.getpwnam(self.options.runAs).pw_gid                  
            os.chown(logdir, runuid, rungid)
            logStream = logging.FileHandler(filename=lf)    

        # Check python version 
        major, minor, release, st, num = sys.version_info
        if major == 2 and minor == 4:
            FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d : %(message)s'
        else:
            FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)

        # adding a new Handler for the console, 
        # to be used only for DEBUG and INFO modes. 
        if self.options.logLevel in [logging.DEBUG, logging.INFO]:
            if self.options.console:
                console = logging.StreamHandler(sys.stdout)
                console.setFormatter(formatter)
                console.setLevel(self.options.logLevel)
                self.log.addHandler(console)
        self.log.setLevel(self.options.logLevel)
        self.log.info('Logging initialized.')


    def _printenv(self):

        envmsg = ''        
        for k in sorted(os.environ.keys()):
            envmsg += '\n%s=%s' %(k, os.environ[k])
        self.log.debug('Environment : %s' %envmsg)


    def __platforminfo(self):
        '''
        display basic info about the platform, for debugging purposes 
        '''
        self.log.info('platform: uname = %s %s %s %s %s %s' %platform.uname())
        self.log.info('platform: platform = %s' %platform.platform())
        self.log.info('platform: python version = %s' %platform.python_version())
        self._printenv()

    
    def __createconfig(self):
        """Create config, add in options...
        """
        if self.options.confFiles != None:
            try:
                self.config = ConfigParser()
                self.config.read(self.options.confFiles)
            except Exception, e:
                self.log.error('Config failure')
                sys.exit(1)
        
        #self.config.set("global", "configfiles", self.options.confFiles)

    def run(self):
        self.ic = InfoClient(self.config)
        self.ic.testquery()



if __name__ == '__main__':
    logging.info("Running from .py file...")
    iccli = InfoClientCLI()
    iccli.run()