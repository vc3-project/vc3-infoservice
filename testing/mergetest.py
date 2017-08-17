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

    def merge(self, src, dest):
            ''' 
            Merges src into dest and returns merged result
            Lists are appended.
            Dictionaries are merged. 
            Primitive values are overwritten. 
            NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen
            https://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge/15836901
            '''
            key = None
            # ## debug output
            # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
            self.log.debug("Handling merging %s into %s " % (src, dest))
            try:
                if dest is None or isinstance(dest, str) or isinstance(dest, unicode) or isinstance(dest, int) \
                             or isinstance(dest, long) or isinstance(dest, float):
                    # border case for first run or if a is a primitive
                    dest = src
                elif isinstance(dest, list):
                    # lists can be only appended
                    if isinstance(src, list):
                        # merge lists
                        dest.extend(src)
                    else:
                        # append to list
                        dest.append(src)
                elif isinstance(dest, dict):
                    # dicts must be merged
                    if isinstance(src, dict):
                        for key in src:
                            if key in dest:
                                dest[key] = self.merge(src[key], dest[key])
                            else:
                                dest[key] = src[key]
                    elif src is None:
                        dest = None
                    else:
                        self.log.warning("Cannot merge non-dict %s into dict %s" % (src, dest))
                else:
                    raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (src, dest))
            except TypeError, e:
                raise Exception('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, src, dest))
            return dest


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

        print("*************************Test 3**********************")
        src = { 'first' : { 'all_rows' : { 'animal' : 'dog', 
                                          'number' : '5' } 
                           },
               }
        print("Source = %s " % src)
        des = { 'first' : None
               }
        print("Dest = %s" % des)
        out = self.merge(src, des)
        pprint.pprint(out)

        print("*************************Test 4**********************")
        src = { 'first' : { 'all_rows' : { 'animal' : 'dog', 
                                          'number' : '5' } 
                           },
                'second' : None
               }
        print("Source = %s " % src)
        des = { 'first' : { 'all_rows' : { 'animal' : 'cat', 
                                          'number' : '1' } 
                           },
               'second' : { 'all_rows' : { 'plane' : 'jet',
                                          'number' : '2' }} 
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
    
    