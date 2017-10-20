#!/usr/bin/env python
#
#    make entity, store
#    retrieve entity, store   
#    retrieve entity, alter, store
#

import os
import sys
import logging

from ConfigParser import ConfigParser
from vc3infoservice import infoclient
from vc3infoservice.core import  InfoMissingPairingException, InfoConnectionFailure, InfoEntityExistsException, InfoEntityMissingException

from testentities import User


class AppClientAPI(object):
    '''
    Client application programming interface. 
    
    -- DefineX() methods return object. CreateX() stores it to infoservice. The two steps will allow 
    some manipulation of the object by the client, or calling user. 
    
    -- Oriented toward exposing only valid operations to external
    user (portal, resource tool, or admin CLI client). 
    
    -- Direct manipulations of stored information in the infoservice is only done by Entity objects, not
    client user.
        
    -- Store method (inside of storeX methods) takes infoclient arg in order to allow multiple infoservice instances in the future. 
        
    '''
    
    def __init__(self, config):
        self.config = config
        self.ic = infoclient.InfoClient(self.config)
        self.log = logging.getLogger('vc3client') 


    ################################################################################
    #                           User-related calls
    ################################################################################
    def defineUser(self,   
                   name,
                   first,
                   last,
                   email,
                   organization,
                   identity_id = None,
                   description = None,
                   displayname = None,
                   url = None,
                   docurl = None,
                   ):           
        '''
       Defines a new User object for usage elsewhere in the API. 
              
       :param str name: The unique VC3 username of this user
       :param str first: User's first name
       :param str last: User's last name
       :param str email: User's email address
       :param str organization: User's institutional affiliation or employer
       :return: User  A valid User object
       
       :rtype: User        
        '''
        u = User( name=name, 
                  state='new', 
                  acl=None, 
                  first=first, 
                  last=last, 
                  email=email, 
                  organization=organization,
                  identity_id=identity_id,
                  description = description,
                  displayname = displayname,
                  url = url,
                  docurl = docurl
                  )
        # This must be set explicitly for newly-created entities, so entire map will be sent.
        #*************************************************
        u.storenew = True
        self.log.debug("Creating user object: %s " % u)
        return u
    
    def storeUser(self, user):
        '''
        Stores the provided user in the infoservice. 
        :param User u:  User to add. 
        :return: None
        '''
        user.store(self.ic)
    
    def updateUser(self, user):
        '''
        Updates the provided user in the infoservice. 
        :param User u:  User to add. 
        :return: None
        '''
        user.store(self.ic)
          

    def listUsers(self):
        '''
        Returns list of all valid users as a list of User objects. 

        :return: return description
        :rtype: List of User objects. 
        
        '''
        return self.ic.listentities(User)
       
    def getUser(self, username):
        return self.ic.getentity( User , username)

    def deleteUser(self, username):
        self.ic.deleteentity( User, username)



if __name__ == '__main__':
    import random
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    
    cp = ConfigParser()
    cp.read(os.path.expanduser("~/git/vc3-infoservice/etc/vc3-infoclient.conf"))
    capi = AppClientAPI(cp)
    log.debug("Making user...")   


    u = capi.defineUser( name = 'username',
                         first = 'First',
                         last = 'Last',
                         email = 'flast@somewhere.org',
                         organization = "somewhere.org",
                         identity_id = None,
                         description = 'A short description', 
                         displayname = 'First Last', 
                         url = "http://www.somewhere.org/flast", 
                         docurl = "http://www.somewhere.org/docs"                                  
                         )
    log.debug("User is %s" % u)
    log.debug('Storing user "username"')
    try:
        capi.storeUser(u)
    except InfoEntityExistsException, e:
        log.debug("Got EntityExistsException...")    
    log.debug("Stored user ")


    for i in range(0,10):
        uname = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(16))
    #for uname in ['username', 'username2', 'username3']:
        u = capi.defineUser( name = uname,
                             first = 'First',
                             last = 'Last',
                             email = 'flast@somewhere.org',
                             organization = "somewhere.org",
                             identity_id = None,
                             description = 'A short description', 
                             displayname = 'First Last', 
                             url = "http://www.somewhere.org/flast", 
                             docurl = "http://www.somewhere.org/docs"                                  
                             )
        log.debug("User is %s" % u)
        log.debug('Storing user "username"')
        try:
            capi.storeUser(u)
        except InfoEntityExistsException, e:
            log.debug("Got EntityExistsException...")    
        log.info("Stored user ")

    log.info("Getting user..")
    try:
        u = capi.getUser('username')
        u.email = 'newflastemail@somewhere.org'
        capi.updateUser(u)
        log.info("User updated.")
    except InfoEntityMissingException:
        log.info("No such user.")    
    
    # Get particular user 1
    log.info("Getting user..")
    try:
        u = capi.getUser('username')
        log.info("User state: %s" % u)
    except InfoEntityMissingException:
        log.info("No such user.")

    # Get non-exisent user user
    log.info("Getting user..")
    try:
        u = capi.getUser('username2')
        log.info("User state: %s" % u)
    
    except InfoEntityMissingException:
        log.info("No such user.")
    
      
    # Print all users...
    log.info("Getting users...")        
    ulist = capi.listUsers()
    for u in ulist:
        print(u)
    
    #if len(ulist) > 2:
    #    for u in ulist[2:]:
    #        log.info("Deleting user %s" % u.name)
    #        capi.deleteUser(u.name)
    
    
    
    
