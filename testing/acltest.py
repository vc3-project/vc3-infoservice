#!/usr/bin/env python
import os
import sys
import logging

from ConfigParser import ConfigParser
from vc3infoservice import infoclient
from vc3infoservice.core import InfoEntity
from vc3infoservice.core import  InfoMissingPairingException, InfoConnectionFailure, InfoEntityExistsException, InfoEntityMissingException

from miracle.acl import Acl

class User(InfoEntity):
    '''
    Represents a VC3 instance user account.
    As policy, name, email, and organization must be set.  
    
    '''
    infoattributes = ['name',
                     'state',
                     'acl',
                     'first',
                     'last',
                     'email',
                     'organization',
                     'identity_id',
                     'description',
                     'displayname',
                     'url',
                     'docurl'                  
                     ] 
    infokey = 'user'
    validvalues = {}
    intattributes = []
    
    def __init__(self,
                   name,
                   state,
                   acl,
                   first,
                   last,
                   email,
                   organization,
                   identity_id=None,
                   description=None,
                   displayname=None,
                   url=None,
                   docurl=None
                ):
        '''
        Defines a new User object. 
              
        :param str name: The unique VC3 username of this user
        :param str first: User's first name
        :param str last: User's last name
        :param str email: User's email address
        :param str organization: User's institutional affiliation or employer
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity.          
        :return: User:  A valid User object      
        :rtype: User
        
        '''
        self.log = logging.getLogger()
        self.state = state
        self.acl = acl
        self.name = name
        self.first = first
        self.last = last
        self.email = email
        self.organization = organization
        self.identity_id = identity_id
        self.allocations = []
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.log.debug("Entity created: %s" % self)


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
    log.setLevel(logging.DEBUG)
    log.info("Starting test...")
    
    cp = ConfigParser()
    cp.read(os.path.expanduser("~/git/vc3-infoservice/etc/vc3-infoclient.conf"))
    capi = AppClientAPI(cp)

    u = capi.defineUser( name = 'useronename',
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

    aclone = Acl()
    
    aclone.add_resource('useronename')
    log.debug(aclone.get_resources())
    
    
    
    
    