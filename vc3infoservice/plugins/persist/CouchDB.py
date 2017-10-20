'''

For CouchDB our config entity categories map nicely onto the JSON document databases. 
Use them directly...

'''


import logging
from vc3infoservice.core import InfoPersistencePlugin

class CouchDB(InfoPersistencePlugin):
    
    def __init__(self, parent, config, section ):


        self.log.debug("CouchDB persistence plugin initialized...")
        
    def storedocument(self, key, doc):
        self.log.debug("Storing doc for key %s..." % key)
        
        
        
    def getdocument(self, key):
        self.log.debug("Getting doc for key %s..." % key)
        

        