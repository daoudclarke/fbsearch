from rdflib.store import Store
from rdflib.plugin import get as plugin
from rdflib import URIRef
#from rdflib.namespace import RDF
from rdflib.term import Literal
#from rdflib.plugins.stores.regexmatching import REGEXTerm

import sys
import logging
#import virtuoso

from log import logger

name_uri = URIRef('http://rdf.freebase.com/ns/type.object.name')

class RelatedEntities(object):
    def __init__(self):
        Virtuoso = plugin("Virtuoso", Store)
        self.store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y;Host=localhost:13093")

    def search(self, entity):
        """
        Find entities related to the given one
        """
        uri = entity.replace('fb:', 'http://rdf.freebase.com/ns/')
        print entity, uri
        ref = URIRef(uri)
        related = self.store.triples((ref, None, None))
        return list(related)

        #uris = [t[0][0] for t in store.triples((None, name_uri, literal))]
        
        

# alias_uri = URIRef('http://rdf.freebase.com/ns/common.topic.alias')

# STOPWORDS = {'the', 'of', 'it', 'a', 'and', 'but'}

def capitalise(input_string):
    """
    Capitalise a string to make it more likely to find a corresponding
    freebase entity.
    """
    words = input_string.lower().split()
    cap_words = [word.capitalize() if word not in STOPWORDS else word
                 for word in words]
    return ' '.join(cap_words)

def search(name):
    """
    Find entities matching a given name
    """
    literal = Literal(unicode(name), lang='en')

    uris = [t[0][0] for t in store.triples((None, name_uri, literal))]
    uris += [t[0][0] for t in store.triples((None, alias_uri, literal))]
    return uris

def get_names(uris):
    for uri in uris:
        for t in store.triples((uri, alias_uri, None)):
            print uri, t[0][2]

if __name__ == "__main__":
    name = capitalise(sys.argv[1])
    print "Capitalised: ", name
    uris = search(name)
    get_names(uris)
