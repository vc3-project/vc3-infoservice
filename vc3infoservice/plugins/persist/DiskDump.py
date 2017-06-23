import logging
import os
import json

class DiskDump(object):
    
    def __init__(self, parent, config, section ):
        self.log = logging.getLogger()
        self.parent = parent
        self.config = config
        self.section = section
        self.documents = {}
        self.log.debug("DiskDump persistence plugin initialized...")

        try:
            self.dbname = os.path.expanduser(self.config.get('plugin-diskdump', 'filename', '~/var/infoservice.diskdump'))
        except Exception, e:
            raise e

        self.load_db()
        
    def storedocument(self, key, doc):
        self.log.debug("Storing doc for key %s..." % key)
        self.documents[key] = doc

        self.store_db()
        return self.documents[key]

    def getdocument(self, key):
        self.load_db()

        self.log.debug("Getting doc for key %s..." % key)
        try:
            s = self.documents[key]
        except KeyError, e:
            s = {}
        return s

    def store_db(self):
        with open(self.dbname, 'w') as outfile:
            outfile.write(json.dumps(self.documents))

    def load_db(self):
	try:
            with open(self.dbname, 'r') as infile:
                self.documents = json.load(infile)
        except IOError:
                pass

