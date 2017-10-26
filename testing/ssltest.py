#!/bin/env python
'''
Simple echo server, using nonblocking I/O
'''
import argparse
import logging
import os
import select
import socket
import sys
import traceback

from ConfigParser import ConfigParser
from OpenSSL import SSL, crypto


class SSLTestClient(object):
    '''
    Simple SSL client, using blocking I/O
    '''
    def __init__(self, config):
        self.log = logging.getLogger()
        self.log.debug('Test client init...')
        self.config = config
        self.certfile  = os.path.expanduser(config.get('netcomm','certfile'))
        self.keyfile   = os.path.expanduser(config.get('netcomm', 'keyfile'))
        self.chainfile = os.path.expanduser(config.get('netcomm','chainfile'))
        self.httpsport = int(config.get('netcomm','httpsport'))
        self.infohost  = config.get('netcomm','infohost')
        self.log.debug("certfile=%s" % self.certfile)
        self.log.debug("keyfile=%s" % self.keyfile)
        self.log.debug("chainfile=%s" % self.chainfile)
        self.log.debug("host=%s:%s" %  (self.infohost, self.httpsport))
        
        
    def verify_cb(self, conn, cert, errnum, depth, ok):
        certsubject = crypto.X509Name(cert.get_subject())
        commonname = certsubject.commonName
        print('Got certificate: ' + commonname)
        return ok

    def run(self):       
        # Initialize context
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.set_options(SSL.OP_NO_SSLv2)
        ctx.set_options(SSL.OP_NO_SSLv3)
        ctx.set_verify(SSL.VERIFY_PEER, self.verify_cb)  # Demand a certificate
        ctx.use_privatekey_file(self.keyfile)
        ctx.use_certificate_file(self.certfile)
        ctx.load_verify_locations(self.chainfile)
        
        # Set up client
        sock = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        sock.connect((self.infohost, int(self.httpsport)))
        
        while 1:
            line = sys.stdin.readline()
            if line == '':
                break
            try:
                sock.send(line)
                sys.stdout.write(sock.recv(1024).decode('utf-8'))
                sys.stdout.flush()
            except SSL.Error:
                print('Connection died unexpectedly')
                break
        
        
        sock.shutdown()
        sock.close()



class SSLTestServer(object):

    def __init__(self, config):
        self.log = logging.getLogger()
        self.log.debug('Test server init...')
        self.config = config
        self.certfile = os.path.expanduser(config.get('netcomm','certfile'))
        self.keyfile = os.path.expanduser(config.get('netcomm', 'keyfile'))
        self.chainfile = os.path.expanduser(config.get('netcomm','chainfile'))
        self.httpsport = int(config.get('netcomm','httpsport'))
        self.sslmodule = config.get('netcomm','sslmodule')
        
        self.log.debug("certfile=%s" % self.certfile)
        self.log.debug("keyfile=%s" % self.keyfile)
        self.log.debug("chainfile=%s" % self.chainfile)
        self.clients = {}
        self.writers = {}



    def verify_cb(self, conn, cert, errnum, depth, ok):
        # This obviously has to be updated
        self.log.info('Got certificate: %s' % cert.get_subject())
        return ok
    
    def dropClient(self, cli, errors=None):
        if errors:
            print 'Client %s left unexpectedly:' % (self.clients[cli],)
            print '  ', errors
        else:
            print 'Client %s left politely' % (self.clients[cli],)
        del self.clients[cli]
        if self.writers.has_key(cli):
            del self.self.writers[cli]
        if not errors:
            cli.shutdown()
        cli.close()
    
    
    def run(self):
        self.log.debug("In Server...")
        
        # Initialize context
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.set_options(SSL.OP_NO_SSLv2)
        ctx.set_verify(SSL.VERIFY_PEER|SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verify_cb) # Demand a certificate
        ctx.use_privatekey_file(self.keyfile)
        ctx.use_certificate_file(self.certfile)
        ctx.load_verify_locations(self.chainfile)
        
        # Set up server
        server = SSL.Connection(ctx, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        server.bind(('', int(self.httpsport)))
        server.listen(3) 
        server.setblocking(0)
        

    
        while 1:
            try:
                r,w,_ = select.select([server]+self.clients.keys(), self.writers.keys(), [])
            except:
                break
        
            for cli in r:
                if cli == server:
                    cli,addr = server.accept()
                    print 'Connection from %s' % (addr,)
                    self.clients[cli] = addr
                    self.log.debug("cli is %s" % cli)
                    self.log.debug("client cert is %s" % cli.get_peer_certificate())
        
                else:
                    try:
                        ret = cli.recv(1024)
                    except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError):
                        pass
                    except SSL.ZeroReturnError:
                        self.dropClient(cli)
                    except SSL.Error, errors:
                        self.dropClient(cli, errors)
                    else:
                        if not self.writers.has_key(cli):
                            self.writers[cli] = ''
                        self.writers[cli] = self.writers[cli] + ret
        
            for cli in w:
                try:
                    ret = cli.send(self.writers[cli])
                except (SSL.WantReadError, SSL.WantWriteError, SSL.WantX509LookupError):
                    pass
                except SSL.ZeroReturnError:
                    self.dropClient(cli)
                except SSL.Error, errors:
                    self.dropClient(cli, errors)
                else:
                    self.writers[cli] = self.writers[cli][ret:]
                    if self.writers[cli] == '':
                        del self.writers[cli]
        
        for cli in self.clients.keys():
            cli.close()
        server.close()

class SSLTestCLI(object):
    
    def __init__(self):
        
        self.results = None
        self.log = None
        self.config = None
        
        self.parseopts()
        self.setuplogging()
        self.log = logging.getLogger()
        self.log.info("CLI...")


    def setuplogging(self):
        self.log = logging.getLogger()
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        #formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.StreamHandler()
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
    
        self.log.setLevel(logging.WARN)
        if self.results.debug:
            self.log.setLevel(logging.DEBUG)
        if self.results.verbose:
            self.log.setLevel(logging.INFO)
        self.log.info('Logging initialized.')


    def parseopts(self):
        
       
        
        parser = argparse.ArgumentParser()
        
        parser.add_argument('-d', '--debug', 
                            action="store_true", 
                            dest='debug', 
                            help='debug logging')        

        parser.add_argument('-v', '--verbose', 
                            action="store_true", 
                            dest='verbose', 
                            help='verbose/info logging')            

        subparsers = parser.add_subparsers( dest="subcommand")

        # Client
        parser_client = subparsers.add_parser('client', 
                                                help='run client ')

        defaultcliconfig = os.path.expanduser('~/git/vc3-infoservice/etc/vc3-infoclient.conf')
        parser_client.add_argument('-c', '--config', 
                            action="store", 
                            dest='cliconfigpath', 
                            default = defaultcliconfig , 
                            help='client configuration file path.')
     
        # Server
        parser_server = subparsers.add_parser('server', 
                                                help='run client')

        defaultsrvconfig = os.path.expanduser('~/git/vc3-infoservice/etc/vc3-infoservice.conf') 
        parser_server.add_argument('-c', '--config', 
                            action="store", 
                            dest='srvconfigpath', 
                            default = defaultsrvconfig , 
                            help='server configuration file path.')
        
        self.results= parser.parse_args()

    def run(self):
       
        cp = ConfigParser()
        ns = self.results

        try:
        
            if ns.subcommand == 'client':
                self.log.info("Config string is %s" % ns.cliconfigpath)
                readfiles = cp.read(ns.cliconfigpath)
                self.log.info('Read config files %s' % readfiles)
                self.log.debug("Running client...")
                sslclient = SSLTestClient(cp)
                sslclient.run()
                
            if ns.subcommand == 'server':
                self.log.info("Config string is %s" % ns.srvconfigpath)
                readfiles = cp.read(ns.srvconfigpath)
                self.log.info('Read config files %s' % readfiles)
                self.log.debug("Running server...")
                sslserver = SSLTestServer(cp)
                sslserver.run()

        except Exception, e:
            self.log.error("Error: Got unexpected exception %s"% e)
            self.log.error(traceback.format_exc(None))
            print(traceback.format_exc(None))
            sys.exit(1)          


if __name__ == '__main__':
    testcli = SSLTestCLI()
    testcli.run()
    
    
    
