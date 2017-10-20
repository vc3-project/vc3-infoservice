
import logging
from vc3infoservice.core import InfoPersistencePlugin

class SQLite(InfoPersistencePlugin):
    
    def __init__(self, parent, config, section ):
        super(Memory, self).__init__(parent, config, section)

        self.log.debug("SQLite persistence plugin initialized...")
        
    def storedocument(self, key, doc):
        self.log.debug("Storing doc for key %s..." % key)

        
        
    def getdocument(self, key):
        self.log.debug("Getting doc for key %s..." % key)

        
