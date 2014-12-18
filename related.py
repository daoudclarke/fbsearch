# from rdflib.store import Store
# from rdflib.plugin import get as plugin
# from rdflib import URIRef
# #from rdflib.namespace import RDF
# from rdflib.term import Literal
# from rdflib import BNode

from sparql import SPARQLStore

#from rdflib.plugins.stores.regexmatching import REGEXTerm

import sys
import logging
#import virtuoso

virtuoso_logger = logging.getLogger('virtuoso.vstore')
virtuoso_logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
virtuoso_logger.addHandler(ch)


from log import logger

# NAME_URI = URIRef('http://rdf.freebase.com/ns/type.object.name')
# DESCRIPTION = URIRef('http://rdf.freebase.com/ns/common.topic.description')

class RelatedEntities(object):
    def __init__(self):
        # Virtuoso = plugin("Virtuoso", Store)
        # self.store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y;Host=localhost:13093")
        self.store = SPARQLStore()

    def get_names(self, entity):
        #return [t[0][2].value for t in self.store.triples((uri, NAME_URI, None))]
        if entity.startswith('http'):
            uri = entity.replace('http://rdf.freebase.com/ns/', 'fb:')
        else:
            uri = entity
        names = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT *
            WHERE
            {
                %s fb:type.object.name ?o .
            }
            """ % uri)
        assert len(names) <= 1
        if len(names) > 0:
            return names[0][0]

    def search(self, entity):
        """
        Find entities related to the given one
        """
        assert type(entity) == unicode, "Expected unicode, got %r" % type(entity)
        if entity.startswith('http'):
            uri = entity.replace('http://rdf.freebase.com/ns/', 'fb:')
        else:
            uri = entity
        #uri = entity
        #print entity, uri
        #ref = URIRef(uri)
        #print "REF: %r" % ref
        logger.debug("Getting triples for %s", uri)
        triples = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT *
            WHERE
            {
                %s ?r ?o .
                FILTER(isURI(?o)) .
                FILTER(!regex(?r, ".*type.*")) .
            }
            LIMIT 150
            """ % uri)

        #triples = self.store.triples((ref, None, BNode()))
        logger.debug("Got triples")
        #print triples
        return [(uri, r, o) for r, o in triples]
        # results = []
        # for t in triples:
        #     print t
        #     results.append(t[0])
        # return results

    def recurse(self, entity, depth=1, seen_entities=None):
        logger.debug("Recursing at depth %d", depth)
        if seen_entities is None:
            seen_entities = set()
        triples = self.search(entity)
        #logger.debug("Related: %r", triples)
        related_entities = set(unicode(o) for s, r, o in triples)
        #if isinstance(o, URIRef))
        unseen = related_entities - seen_entities
        if depth > 0:
            for entity in unseen:
                #print "NAME 2: %r" % name2
                related2 = self.recurse(entity, depth - 1, seen_entities | unseen)
                #new_names = [self.get_name(x) for x in related2]
                #print "NEW NAMES", new_names
                triples += related2
        return triples

        #uris = [t[0][0] for t in store.triples((None, name_uri, literal))]
        
        

# # alias_uri = URIRef('http://rdf.freebase.com/ns/common.topic.alias')

# # STOPWORDS = {'the', 'of', 'it', 'a', 'and', 'but'}

# def capitalise(input_string):
#     """
#     Capitalise a string to make it more likely to find a corresponding
#     freebase entity.
#     """
#     words = input_string.lower().split()
#     cap_words = [word.capitalize() if word not in STOPWORDS else word
#                  for word in words]
#     return ' '.join(cap_words)

# def search(name):
#     """
#     Find entities matching a given name
#     """
#     literal = Literal(unicode(name), lang='en')

#     uris = [t[0][0] for t in store.triples((None, name_uri, literal))]
#     uris += [t[0][0] for t in store.triples((None, alias_uri, literal))]
#     return uris

# def get_names(uris):
#     for uri in uris:
#         for t in store.triples((uri, alias_uri, None)):
#             print uri, t[0][2]

if __name__ == "__main__":
    # name = capitalise(sys.argv[1])
    # print "Capitalised: ", name
    # uris = search(name)
    # get_names(uris)
    #uri = u'http://rdf.freebase.com/ns/m.0kl73m'
    #uri = u'http://rdf.freebase.com/ns/m.07y2h64'
    #uri = u'http://rdf.freebase.com/ns/en.creative_commons_by'
    #uri = u'fb:en.creative_commons_by'
    #uri = u'fb:m.07y2h64'
    uri = u'fb:en.justin_bieber'
    related = RelatedEntities()
    related_triples = related.recurse(uri, depth=2)
    for triple in related_triples:
        s, r, o = triple
        name = related.get_names(o)
        print "TRIPLE", triple, repr(name)

