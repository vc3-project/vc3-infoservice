#!/bin/env python
#
# Test harness fo experimentation with low-level operations. 
#
#

import logging
import pprint

class InfoHandler(object):
    '''
    Handles low-level operations and persistence of information 
    from service using back-end plugin.
    
    Data at this level is converted to/from native Python objects for storage/retrieval
     
    '''
    def __init__(self):
        self.log = logging.getLogger()
        self.log.debug("Initializing Info Handler...")
        #self.log.debug("Done initting InfoHandler")
    
    def oldmerge(self, source, destination):
        """
        merges nested python dictionaries| lists | strings
        run me with nosetests --with-doctest file.py
    
        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
        >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
        True
        
        
        """
        self.log.debug("source is type %s" % type(source))
        self.log.debug("destination is type %s" % type(destination))
        for key, value in source.items():
            self.log.debug("processing node %s" % key)
            if isinstance(value, dict):
                "%s is dict" % value
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge(value, node)
            else:
                destination[key] = value
        return destination

    def merge(self, a, b):
        ''' 
        Merges b into a and return merged result
        Lists are appended.
        Dictionaries are merged. 
        Values overwritten. 
        NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen'''
        key = None
        # ## debug output
        # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
        try:
            if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
                # border case for first run or if a is a primitive
                a = b
            elif isinstance(a, list):
                # lists can be only appended
                if isinstance(b, list):
                    # merge lists
                    a.extend(b)
                else:
                    # append to list
                    a.append(b)
            elif isinstance(a, dict):
                # dicts must be merged
                if isinstance(b, dict):
                    for key in b:
                        if key in a:
                            a[key] = self.merge(a[key], b[key])
                        else:
                            a[key] = b[key]
                else:
                    raise Exception('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
            else:
                raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
        except TypeError, e:
            raise Exception('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
        return a



    def mergetest(self):
        '''
    
        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
        >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
        True
        
        '''
        print("*************************Test 1**********************")
        src = { 'first' : { 'all_rows' : { 'animal' : 'dog', 
                                          'number' : '1' } 
                           },
               }
        print("Source = %s " % src)
        des = { 'first' : { 'all_rows' : { 'animal' : 'cat', 
                                          'number' : '5' } 
                           } 
               }
        print("Dest = %s" % des)
        out = self.merge(src, des)
        pprint.pprint(out)
    
        print("*************************Test 2**********************")
        src = { 'first' : { 'all_rows' : { 'animal' : 'dog', 
                                          'number' : '5' } 
                           },
               }
        print("Source = %s " % src)
        des = { 'first' : { 'all_rows' : { 'animal' : 'cat', 
                                          'number' : '1' } 
                           } 
               }
        print("Dest = %s" % des)
        out = self.merge(src, des)
        pprint.pprint(out)
    
if __name__ == '__main__':
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    ih = InfoHandler()
    ih.mergetest()
    
    