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

class InfoEntity(object):
    '''
    Template for Information entities. Common functions. 
    Classes that inherit from InfoEntity must set class variables to describe handling. 

    '''
    infokey = 'unset'
    infoattributes = []
    validvalues = {}
        
    def __repr__(self):
        s = "%s(" % self.__class__.__name__
        for a in self.__class__.infoattributes:
            val = getattr(self, a, None)
            if val is not None:
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
        Stores this Infoentity in the provided infoclient info tree. 
        '''
        keystr = self.__class__.infokey
        validvalues = self.__class__.validvalues
        for keyattr in validvalues.keys():
            validlist = validvalues[keyattr]
            attrval = getattr(self, keyattr) 
            if attrval not in validlist:
                self.log.warning("Info Entity has invalid value '%s' for attribute '%s' " % (attrval, keyattr) )
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
            args[key] = d[key]
        eo = cls(**args)
        log.debug("Successfully made object from dictionary, returning...")
        return eo