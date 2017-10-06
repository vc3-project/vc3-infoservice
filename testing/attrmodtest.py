#!/bin/env python
import logging

class InfoEntity(object):
    '''
    Template for Information entities. Common functions. 
    Classes that inherit from InfoEntity must set class variables to describe handling. 
    

    '''
    infokey = 'unset'
    infoattributes = []
    intattributes = []
    validvalues = {}
    
   
    def __setattr__(self, name, value):
        '''
        _difflist   List of (info)attributes that have been changed (not just 
                    initialized once.  
        '''
        log = logging.getLogger()        
        if name in self.__class__.infoattributes:
            try:
                diffmap = self._diffmap
            except AttributeError:
                diffmap = {}
                for at in self.__class__.infoattributes:
                    diffmap[at] = 0
                object.__setattr__(self,'_diffmap', diffmap)
            diffmap[name] += 1
            log.debug('infoattribute %s' % name)            
        else:
            log.debug('non-infoattribute %s' % name)
        object.__setattr__(self, name, value)


    def getDiffInfo(self):
        '''
        Return a list of info attributes which have been set > 1 time. 
        '''
        retlist = []
        try:
            diffmap = self._diffmap
        except AttributeError:
            pass
        for a in diffmap.keys():
            if diffmap[a] > 1:
                retlist.append(a)
        return retlist
            
    
    def __repr__(self):
        s = "%s( " % self.__class__.__name__
        for a in self.__class__.infoattributes:
            val = getattr(self, a, None)
            if isinstance(val, str) or isinstance(val, unicode):
                if len(val) > 80:
                    s+="%s=%s... " % (a, val[:25] )
                else:
                    s+="%s=%s " % (a, val )
            else:
                s+="%s=%s " % (a, val )
        s += ")"
        return s    


    def makeDictObject(self):
        '''
        Converts this Python object to attribute dictionary suitable for addition to existing dict 
        intended to be converted back to JSON. Uses <obj>.name as key:
        '''
        d = {}
        d[self.name] = {}
        for attrname in self.infoattributes:
            d[self.name][attrname] = getattr(self, attrname)
        self.log.debug("Returning dict: %s" % d)
        return d    

    def setState(self, newstate):
        self.log.debug("%s object name=%s %s ->%s" % (self.__class__.__name__, self.name, self.state, newstate) )
        self.state = newstate
    
    def store(self, infoclient):
        '''
        Stores this Info Entity in the provided infoclient info tree. 
        '''
        keystr = self.__class__.infokey
        validvalues = self.__class__.validvalues
        for keyattr in validvalues.keys():
            validlist = validvalues[keyattr]
            attrval = getattr(self, keyattr) 
            if attrval not in validlist:
                self.log.warning("%s entity has invalid value '%s' for attribute '%s' " % (self.__class__.__name__,
                                                                                           attrval,                                                                                            keyattr) )
        #resources = infoclient.getdocumentobject(key=keystr)
        da = self.makeDictObject()
        self.log.debug("Dict obj: %s" % da)
        infoclient.storedocumentobject(da, key=keystr)

    def addAcl(self, aclstring):
        pass    

    def removeAcl(self, aclstring):
        pass

    @classmethod
    def objectFromDict(cls, dict):
        '''
        Returns an initialized Entity object from dictionary. 
        Input: Dict:
        { <name> : 
            {
                "name" : "<name>",
                "att1" : "<val1>"  
            }
        }
        '''
        log = logging.getLogger()
        log.debug("Making object from dictionary...")
        name = dict.keys()[0]
        d = dict[name]
        args = {}
        for key in cls.infoattributes:
            try:
                args[key] = d[key]
            except KeyError, e:
                args[key] = None
                log.warning("Document object does not have a '%s' key" % e.args[0])
        for key in cls.intattributes:
            try:
                if args[key] is not None:
                    args[key] = int(args[key])
            except KeyError, e:
                log.warning("Document object does not have a '%s' key" % e.args[0])
        eo = cls(**args)
        log.debug("Successfully made object from dictionary, returning...")
        return eo


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
                     'allocations',
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
        


    def addAllocation(self, allocation):
        '''
            Adds provided allocation (string label) to this allocation.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Adding allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.allocations.append(allocation)
        self.log.debug("Allocations now %s" % self.allocations)
        

    def removeAllocation(self, allocation):
        '''
            Removes provided allocation (string label) to this project.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Removing allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.log.debug("Allocation %s did not belong to project")
        else:
            self.allocations.remove(allocation)
            self.log.debug("Allocations now %s" % self.allocations)


class Project(InfoEntity):
    '''
    Represents a VC3 Project.
    
    '''
    infokey = 'project'
    infoattributes = ['name',
                     'state',
                     'acl',
                     'owner',
                     'members', 
                     'allocations',
                     'blueprints',
                     'description',
                     'displayname',
                     'url',
                     'docurl',
                     'organization', 
                     ]
    validvalues = {}
    intattributes = []    
    
    def __init__(self, 
                   name,
                   state,
                   acl,
                   owner,
                   members,   # list
                   allocations=[],  # list of names 
                   blueprints=[],
                   description=None,
                   displayname=None,
                   url=None,
                   docurl=None, 
                   organization = None,
                   ):  # list of names
        '''
        Defines a new Project object. 
              
        :param str name: The unique VC3 name of this project
        :param str owner: VC3 username of project owner. 
        :param str members: List of vc3 usernames
        :param str allocations: List of allocation names. 
        :param str blueprints:  List of blueprint names. 
        :param str description: Long-form description
        :param str displayname: Pretty human-readable name/short description
        :param str url: High-level URL reference for this entity. 
        :param str docurl: Link to how-to/usage documentation for this entity. 
        :param str organization: Name of experiment or institution for this project. 
        :return: Project:  A valid Project objext. 
        :rtype: Project
        
        '''  
        self.log = logging.getLogger()
        self.name = name
        self.state = state
        self.acl = acl
        self.owner = owner
        self.members = []
        for m in members:
            if m not in self.members:
                self.members.append(m)
        self.allocations = allocations
        self.blueprints = blueprints
        self.description = description
        self.displayname = displayname
        self.url = url
        self.docurl = docurl
        self.organization = organization
        self.log.debug("Entity created: %s" % self)
 
    def addUser(self, user):
        '''
            Adds provided user (string label) to this project.
        '''

        if self.members is None:
            self.members = []

        self.log.debug("Adding user %s to project" % user)
        if user not in self.members:
            self.members.append(user)
        self.log.debug("Members now %s" % self.members)
        

    def removeUser(self, user):
        '''
            Removes provided user (string label) from this project.
        '''

        if self.members is None:
            self.members = []

        self.log.debug("Removing user %s to project" % user)
        if user not in self.members:
            self.log.debug("User %s did not belong to project")
        else:
            self.members.remove(user)
            self.log.debug("Members now %s" % self.members)

    def addAllocation(self, allocation):
        '''
            Adds provided allocation (string label) to this project.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Adding allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.allocations.append(allocation)
        self.log.debug("Allocations now %s" % self.allocations)
        

    def removeAllocation(self, allocation):
        '''
            Removes provided allocation (string label) from this project.
        '''

        if self.allocations is None:
            self.allocations = []

        self.log.debug("Removing allocation %s to project" % allocation)
        if allocation not in self.allocations:
            self.log.debug("Allocation %s did not belong to project")
        else:
            self.allocations.remove(allocation)
            self.log.debug("Allocations now %s" % self.allocations)
            

if __name__ == "__main__":

    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    nu = User( name='uname', 
               state = "new",
               acl = "XXX",
               first = "First",
               last = "Last",
               email = "flast@someplace.org",
               organization = 'Someplace',
               )
    
    log.debug("diffinfo: %s" % nu.getDiffInfo() )
    nu.first = "NewFirst"
    nu.last  = "NewLast"
    nu.email = "newflast@someplacenew.edu"
    log.debug("diffinfo: %s" % nu.getDiffInfo() )
    

