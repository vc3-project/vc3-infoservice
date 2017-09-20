import errno
import json
import logging
import os
import time
import tempfile

class DiskDump(object):
    
    def __init__(self, parent, config, section ):
        self.log = logging.getLogger()
        self.parent = parent
        self.config = config
        self.section = section
        self.documents = {}

        try:
            self.dbname = os.path.expanduser(self.config.get('plugin-diskdump', 'filename', '~/var/infoservice.diskdump'))
        except Exception, e:
            raise e

        self.load_db()
        self.log.debug("DiskDump persistence plugin initialized...")
        
    def storedocument(self, key, doc):
        self.log.debug("Storing doc for key %s..." % key)
        self.documents[key] = doc

        self.store_db()
        return self.documents[key]

    def getdocument(self, key):
        self.log.debug("Getting doc for key %s..." % key)
        try:
            s = self.documents[key]
        except KeyError, e:
            s = {}
        return s

    def deletesubtree(self, path):
        self.log.debug("Deleting path %s..." % str(path))

        if len(path) < 1:
            return None

        last_dict = self.documents

        for key in path[0 : -1]:
            last_dict = last_dict[key]

        value = last_dict[path[-1]]
        del last_dict[path[-1]]

        self.store_db()
        return value

    def store_db(self):

        tmpfile = None
        try:
            tmpfile = tempfile.NamedTemporaryFile(mode = 'w', prefix = self.dbname, delete = False)
        except IOError, e:
            self.log.warn('Diskdump could not be performed. Could not open temporary file. (%s)', e)

        try:
            dump    = json.dumps(self.documents, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8')
            tmpfile.write(dump)
            tmpfile.flush()
            tmpfile.close()

            towrite = len(dump)
            written = os.stat(tmpfile.name).st_size

            if towrite == written:
                self.log.debug('renaming Diskdump %s to %s' % (tmpfile.name, self.dbname))
                os.rename(tmpfile.name, self.dbname)
            else:
                self.log.warn('Diskdump could not be performed. Could not write the whole file. (%d != %d)', towrite, written)
        except Exception, e:
                self.log.warn('Diskdump could not be performed. (%s)', e)


    def load_db(self):
        try:
            with open(self.dbname, 'r') as infile:
                self.documents = json.load(infile)
        except IOError, e:
            if e.errno == errno.ENOENT:
                self.log.warn("Could not load db file %s" % self.dbname)
            else:
                raise e
        except ValueError, e:
            self.log.error("Could not load db file %s. (%s)" % (self.dbname, e))
            os.rename(self.dbname, self.dbname + '.invalid.' + time.strftime('%Y%m%d.%H%M%S'))
            os.remove(self.dbname)

