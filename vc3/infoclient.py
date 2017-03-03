#! /usr/bin/env python

import json
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

urllib3.disable_warnings()
logging.captureWarnings(True)


TESTKEY='testkey'
TESTDOC='''{"uchicago_rcc" : {
            "base" : {
                "distribution" : "redhat",
                "release" : "6.7",
                "architecture" : "x86_64"}
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

    def storedocument(self, key, doc):
        #doc = urllib.quote_plus(doc)
        
        u = "https://%s:%s/info?key=%s" % (self.infohost, 
                            self.httpsport,
                            key
                            )
        self.log.debug("Trying to store document %s at %s" % (doc, u))
        try:
            r = requests.post(u, verify=self.chainfile, cert=(self.certfile, self.keyfile), params={'data' : doc})
            self.log.debug(r.status_code)
        
        except requests.exceptions.ConnectionError, ce:
            print('Connection failure. %s' % ce)

    def getdocument(self, key):
        u = "https://%s:%s/info?key=%s" % (self.infohost, 
                            self.httpsport,
                            key
                            )
        try:
            r = requests.get(u, verify=self.chainfile, cert=(self.certfile, self.keyfile))
            out = self.stripquotes(r.text)
            parsed = json.loads(out)
            pretty = json.dumps(parsed, indent=4, sort_keys=True)
            self.log.debug(pretty)
            self.log.debug(r.status_code)
            return r.text
        
        except requests.exceptions.ConnectionError, ce:
            print('Connection failure. %s' % ce)
    
    def mergedocument(self, key, doc):
                
        u = "https://%s:%s/info?key=%s" % (self.infohost, 
                            self.httpsport,
                            key
                            )
        self.log.debug("Trying to merge document %s at %s" % (doc, u))
        try:
            r = requests.put(u, verify=self.chainfile, cert=(self.certfile, self.keyfile), params={'data' : doc})
            self.log.debug(r.status_code)
        
        except requests.exceptions.ConnectionError, ce:
            print('Connection failure. %s' % ce)
    
    def deletedocument(self, key):
        pass
        
    def testquery(self):
        self.log.info("Testing storedocument. Doc = %s" % TESTDOC)
        self.storedocument(key=TESTKEY,doc=TESTDOC)
        
        self.log.info("Testing getdocument...")
        self.getdocument(key=TESTKEY)
        self.log.info("Done.")


    def stripquotes(self,s):
        rs = s.replace("'","")
        return rs

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
                          default="stdout", 
                          metavar="LOGFILE", 
                          action="store", 
                          help="Send logging output to LOGFILE or SYSLOG or stdout [default <syslog>]")
        parser.add_option("--add", dest="addfiles", 
                          action="store", 
                          metavar="FILE1[,FILE2,FILE3]", 
                          help="Merge info into store from JSON files with key as top-level tag.")        
        parser.add_option("--getkey", dest="getkey", 
                          action="store", 
                          metavar="[resource|account|cluster|...]", 
                          help="Get info from store with provided key.")        


        (self.options, self.args) = parser.parse_args()
        self.options.confFiles = self.options.confFiles.split(',')

    def __setuplogging(self):
        """ 
        Setup logging 
        """
        self.log = logging.getLogger()
        if self.options.logfile == "stdout":
            logStream = logging.StreamHandler()
        else:
            lf = self.options.logfile
            logdir = os.path.dirname(lf)
            if not os.path.exists(logdir):
                os.makedirs(logdir)
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
        
        #self.config.add_section('cli')
        #self.config.set("cli", "addfiles", self.options.confFiles)

    def doquery(self):
        self.ic = InfoClient(self.config)
        if self.options.addfiles:
            flist = self.options.addfiles.split(',')
            for fn in flist:
                fname = fn.strip()
                self.log.debug("Adding contents of file %s" % fname)
                jdoc = open(fname).read()
                data = json.loads(jdoc)
                pretty = json.dumps(data, indent=4, sort_keys=True)
                self.log.debug(pretty)
                k = data.keys()[0]
                self.log.debug("key is %s" % k)
                self.ic.mergedocument(k,jdoc)
        
        if self.options.getkey:
            qkey = self.options.getkey.lower().strip()
            self.log.debug("Getkey is %s, doing query" % qkey )
            out = self.ic.getdocument(qkey)
            print(out)

    def testquery(self):
        self.ic = InfoClient(self.config)
        self.ic.testquery()
        


if __name__ == '__main__':
    logging.info("Running from .py file...")
    iccli = InfoClientCLI()
    iccli.doquery()
    #iccli.testquery()