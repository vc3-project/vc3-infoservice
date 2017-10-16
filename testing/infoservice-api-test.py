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
from vc3infoservice.core import InfoEntity
from vc3infoservice import infoclient
from vc3infoservice.infoclient import  InfoMissingPairingException, InfoConnectionFailure

   
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
        self.log.debug("Creating user object: %s " % u)
        return u
    
        
    def storeUser(self, user):
        '''
        Stores the provided user in the infoservice. 
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
        return self._listEntities('User')
       
    def getUser(self, username):
        return self._getEntity('User', username)

    def _listEntities(self, entityclass ):
        m = sys.modules[__name__] 
        klass = getattr(m, entityclass)
        infokey = klass.infokey
        self.log.debug("Listing class %s with infokey %s " % (entityclass, infokey))     
        docobj = self.ic.getdocumentobject(infokey)
        self.log.debug("Got document object: %s " % docobj)
        olist = []
        try:
            for oname in docobj[infokey].keys():
                    self.log.debug("Getting objectname %s" % oname)
                    #s = "{ '%s' : %s }" % (oname, docobj[infokey][oname] )
                    nd = {}
                    nd[oname] = docobj[infokey][oname]
                    eo = klass.objectFromDict(nd)
                    self.log.debug("Appending eo %s" % eo)
                    olist.append(eo)
        except KeyError, e:
            self.log.warning("Document has no key '%s'", e.args[0])
        except TypeError, e:
            self.log.warning("Document object empty.")
        return olist


    def _getEntity(self, entityclass, objectname):
        eolist = self._listEntities(entityclass)
        self.log.debug("Got list of %d entity objects, matching entityclass %s..." % (len(eolist), 
                                                                                     entityclass))
        for eo in eolist:
            if eo.name == objectname:
                self.log.debug("Found object of correct name %s" % objectname)
                return eo
        self.log.debug("Didn't find desired objectname %s" % objectname)

    


if __name__ == '__main__':
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    
    
    
    cp = ConfigParser()
    cp.read(os.path.expanduser("~/git/vc3-info-service/etc/vc3-infoclient.conf"))
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
    log.debug('Storing user...')
    capi.storeUser(u)

    log.debug("Getting users...")        
    ulist = capi.listUsers()
    for u in ulist:
        print(u)
    
    
    
