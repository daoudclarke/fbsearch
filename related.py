from rdflib.store import Store
from rdflib.plugin import get as plugin
from rdflib import URIRef
#from rdflib.namespace import RDF
from rdflib.term import Literal
#from rdflib.plugins.stores.regexmatching import REGEXTerm

import sys
import logging
#import virtuoso

logger = logging.getLogger('virtuoso.vstore')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


Virtuoso = plugin("Virtuoso", Store)
store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y;Host=localhost:13093")

name_uri = URIRef('http://rdf.freebase.com/ns/type.object.name')
alias_uri = URIRef('http://rdf.freebase.com/ns/common.topic.alias')

STOPWORDS = {'the', 'of', 'it', 'a', 'and', 'but'}

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
