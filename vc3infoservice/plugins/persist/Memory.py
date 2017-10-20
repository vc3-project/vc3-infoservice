import logging
import threading
from vc3infoservice.core import InfoPersistencePlugin

class Memory(InfoPersistencePlugin):
    '''
    Memory persistence plugin. Takes inbound Python primitive documents and simply keeps them in memory. 
    '''
    def __init__(self, parent, config, section ):
        super(Memory, self).__init__(parent, config, section)
        self.lock = threading.Lock()
        self.documents = {}
        self.log.debug("Memory persistence plugin initialized...")
        
    def storedocument(self, key, doc):
        self.log.debug("Storing doc for key %s..." % key)
        self.documents[key] = doc

    def getdocument(self, key):
        self.log.debug("Getting doc for key %s..." % key)
        try:
            s = self.documents[key]
        except KeyError, e:
            s = {}
        return s

    def _deletesubtree(self, path):
        self.log.debug("Deleting path %s..." % str(path))

        if len(path) < 1:
            return None

        last_dict = self.documents

        for key in path[0 : -1]:
            last_dict = last_dict[key]

        value = last_dict[path[-1]]
        del last_dict[path[-1]]

        return value        
       
