#!/bin/env python

__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import logging
import random
import string

class InfoConnectionFailure(Exception):
    '''
    Network connection failure exception. 
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)   

class InfoMissingPairingException(Exception):
    '''
    Exception thrown when a pairing code is invalid, either because it never existed
    or the pairing has already been retrieved. 
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

class InfoEntityExistsException(Exception):
    '''
    Exception thrown when an attempt to create an entity with a 
    name that already exists. Old entity must be deleted first. 
     
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

class InfoEntityMissingException(Exception):
    '''
    Exception thrown when an attempt to get a non-existent entity is made.
    Entity must be created before it can be updated.  
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)  

class InfoEntityUpdateMissingException(Exception):
    '''
    Exception thrown when an attempt to *update* a non-existent entity is made.
    Entity must be created before it can be updated.  
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 

class InfoAttributeFacade(object):
    '''
    Intercepts __setattr__ one level down for InfoEntities. 
   
    '''
    def __init__(self, parent, attrname):
        log = logging.getLogger()  
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_attrname', attrname)
        log.debug("Facade made for attribute %s parent %s" % (attrname, parent))

    def __setattr__(self, name, value):
        '''
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
            log.debug('infoattribute %s incremented to %s' % ( name, diffmap[name] ) )            
        else:
            log.debug('non-infoattribute %s' % name)
        object.__setattr__(self, name, value)

    def __getattr__(self, attrname):
        return object.__getattr__(self, name)
    



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
        else:
            log.debug('non-infoattribute %s' % name)
        object.__setattr__(self, name, value)

    #def __getattr__(self, name):
    #    '''
    #    To be on the safe side, we track attributes that have been retrieved. 
    #    Client may alter an object that is the value of the attribute. 
    #    '''
    #    log = logging.getLogger()        
    #    if name in self.__class__.infoattributes:
    #        try:
    #            diffmap = self._diffmap
    #        except AttributeError:
    #            diffmap = {}
    #            for at in self.__class__.infoattributes:
    #                diffmap[at] = 0
    #            object.__setattr__(self,'_diffmap', diffmap)
    #        diffmap[name] += 1
    #        log.debug('infoattribute %s' % name)            
    #    else:
    #        log.debug('non-infoattribute %s' % name)
    #    object.__getattr__(self, name)


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

    def makeDictObject(self, newonly=False):
        '''
        Converts this Python object to attribute dictionary suitable for addition to existing dict 
        intended to be converted back to JSON. Uses <obj>.name as key:
        '''
        d = {}
        d[self.name] = {}
        if newonly:
            # only copy in values that have been re-set after initialization
            self.log.debug("newonly set, getting diff info...")
            difflist = self.getDiffInfo()
            for attrname in difflist:
                d[self.name][attrname] = getattr(self, attrname)
        else:
            # copy in all infoattribute values
            self.log.debug("newonly not set, doing all values...")
            for attrname in self.infoattributes:
                d[self.name][attrname] = getattr(self, attrname)
        self.log.debug("Returning dict: %s" % d)
        return d    

    def setState(self, newstate):
        self.log.debug("%s object name=%s %s ->%s" % (self.__class__.__name__, self.name, self.state, newstate) )
        self.state = newstate
    

    def store(self, infoclient):
        '''
        Updates this Info Entity in store behind given infoclient. 
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
        if hasattr(self, 'storenew'):
            entdict = self.makeDictObject(newonly=False)
            self.log.debug("Dict obj: %s" % entdict)
            infoclient._storeentitydict(keystr, entdict )
        else:
            entdict = self.makeDictObject(newonly=True)
            self.log.debug("Dict obj: %s" % entdict)
            infoclient._mergeentitydict(keystr, entdict )
        self.log.debug("Stored entity %s in key %s" % (self.name, keystr))

    def addAcl(self, aclstring):
        pass    

    def removeAcl(self, aclstring):
        pass

    def getClone(self, newname = None):
        '''
        Make new identical object with new name attribute. 
        '''
        self.log.debug("making clone of %s object name=%s " % (self.__class__.__name__, self.name) )
        dictobject = self.makeDictObject()  # has name as index of attribute dict
        dict = dictobject[self.name]
        
        if newname is not None:
            dict['name'] = newname
        else:
            dict['name'] = self.generateName()
        self.log.debug('new dict is %s' % dict)    
        newobj = self.__class__.objectFromDict(dict)
        newobj.storenew = True
        self.log.debug('new object is %s' % newobj)
        return newobj
    
    
    def generateName(self, length=16):
        '''
        Make new name attribute appropriate to this object. 
        For parent InfoEntity, just generate a random string...
        '''
        randomstr = InfoEntity.randomChars(self, length)
        return randomstr
    

    @classmethod
    def objectFromDict(cls, dict):
        '''
        Returns an initialized Entity object from dictionary. 
        Input: Dict:
            {
                "name" : "<name>",
                "att1" : "<val1>"  
            }

        '''
        log = logging.getLogger()
        log.debug("Making object from dictionary...")
        #name = dict.keys()[0]
        #d = dict[name]
        d = dict
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
    
    @classmethod
    def randomChars(self, length=5):
        randomstr = ''.join([random.choice(string.ascii_lowercase) for n in xrange(length)])
        return randomstr
        

class InfoPersistencePlugin(object):

    def __init__(self, parent, config, section ):
        self.log = logging.getLogger()
        self.lock = MockLock()
        self.parent = parent
        self.config = config
        self.section = section

class MockLock(object):
    '''
    Provided as a convenience for persistence back ends that don't require atomic operations. 
    ''' 
    
    def acquire(self):
        pass
        
    def release(self):
        pass
        



