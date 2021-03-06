# from rdflib.store import Store
# from rdflib.plugin import get as plugin
# from rdflib import URIRef
# #from rdflib.namespace import RDF
# from rdflib.term import Literal
# from rdflib import BNode

from sparql import SPARQLStore

#from rdflib.plugins.stores.regexmatching import REGEXTerm

from fbsearch import settings

from socket import timeout
import sys
import logging
#import virtuoso
import json

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
        try:
            cache_file = open(settings.ENTITY_SCORE_CACHE_PATH)
            self.entity_scores = json.load(cache_file)
            logger.info("Loaded %d entities in cache", len(self.entity_scores))
        except IOError:
            self.entity_scores = {}

    def save_cache(self):
        logger.info("Saving entity score cache")
        with open(settings.ENTITY_SCORE_CACHE_PATH, 'w') as cache_file:
            json.dump(self.entity_scores, cache_file)

    def get_names(self, entity):
        entity = ensure_prefixed(entity)
        names = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT *
            WHERE
            {
                %s fb:type.object.name ?o .
            }
            """ % entity)
        assert len(names) <= 1
        if len(names) > 0:
            return names[0][0]

    def search(self, entity):
        """
        Find entities related to the given one
        """
        assert type(entity) == unicode, "Expected unicode, got %r" % type(entity)
        uri = ensure_prefixed(entity)
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

    def connect_names(self, query_entities, target_names):
        if len(query_entities) == 0:
            return []

        name_query_string = (','.join(['"%s"@en']*len(target_names)) %
                             tuple(target_names))
        logger.debug("Name query string: %r", name_query_string)
        try:
            all_entities = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT ?r1 
                WHERE
                {
                    {
                        ?s ?r1 ?e .
                        ?e fb:type.object.name ?n .
                        FILTER(?n IN (%s)) .
                        FILTER(?s IN (%s)) .
                    } UNION {
                        ?s ?r1 ?e .
                        ?e fb:common.topic.alias ?n .
                        FILTER(?n IN (%s)) .
                        FILTER(?s IN (%s)) .
                    }
                }
                """ % (name_query_string, ','.join(query_entities),
                       name_query_string, ','.join(query_entities)))
        except timeout:
            logger.exception("Timeout looking for simple connection")
            all_entities = []
        logger.debug("Performing complex search")
        logger.info("Found %d simple connections", len(all_entities))
        for target_name in target_names:
            try:
                entities = self.store.query("""
                    prefix fb: <http://rdf.freebase.com/ns/>
                    SELECT ?r1, ?r2
                    WHERE
                    {
                        {
                            ?s ?r1 ?o .
                            ?o ?r2 ?e .
                            ?e fb:type.object.name "%s"@en .
                            FILTER(?s IN (%s)) .
                        } UNION {
                            ?s ?r1 ?o .
                            ?o ?r2 ?e .
                            ?e fb:common.topic.alias "%s"@en .
                            FILTER(?s IN (%s)) .
                        }
                    }
                    """ % (target_name, ','.join(query_entities),
                           target_name, ','.join(query_entities)))
                logger.debug("Search for complex connection: %r", entities)
                all_entities += entities
            except timeout:
                logger.exception("Timeout looking for complex connection with target: %s",
                                 target_name)
        return set(all_entities)


    def connect(self, query_entities, target_entities):
        all_entities = []
        for target_entity in target_entities:
            logger.debug("Target entity: %s", target_entity)
            target_uri = ensure_prefixed(target_entity)
            entities = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT ?r1 
                WHERE
                {
                    ?s ?r1 %s .
                    FILTER(?s IN (%s)) .
                }
                """ % (target_uri, ','.join(query_entities)))
            if entities:
                logger.debug("Found simple connection: %r", entities)
                all_entities += entities
                continue

            # # Reverse relationship direction
            # entities = self.store.query("""
            #     prefix fb: <http://rdf.freebase.com/ns/>
            #     SELECT ?s, ?r1 
            #     WHERE
            #     {
            #         %s ?r1 ?s .
            #         FILTER(?s IN (%s)) .
            #     }
            #     """ % (target_entity, ','.join(query_entities)))
            # if entities:
            #     all_entities += entities
            #     continue

            entities = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT ?r1, ?r2 
                WHERE
                {
                    ?s ?r1 ?o1 .
                    ?o1 ?r2 %s .
                    FILTER(?s IN (%s)) .
                }
                """ % (target_uri, ','.join(query_entities)))
            if entities:
                logger.debug("Found level 2 connection: %r", entities)
            all_entities += entities
        return all_entities

    def search_exact(self, name):
        entities = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT ?e
            WHERE
            {
                {
                    ?e fb:type.object.name "%s"@en .
                }
            }
            """ % (name,))
        # entities = self.store.query("""
        #     prefix fb: <http://rdf.freebase.com/ns/>
        #     SELECT ?e
        #     WHERE
        #     {
        #         {
        #             ?e fb:common.topic.alias "%s"@en .
        #         } UNION {
        #             ?e fb:type.object.name "%s"@en .
        #         }
        #     }
        #     """ % (name, name))
        return [e[0] for e in entities]

    def apply_connection(self, entities, connection):
        logger.debug("Applying connection %r to entities %r",
                     connection, entities)
        connection = [ensure_prefixed(part) for part in connection]
        if len(connection) == 1:
            results = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT ?o
                WHERE
                {
                    ?s %s ?o .
                    FILTER(?s IN (%s)) .
                }
                LIMIT 100
                """ % (connection[0], ','.join(entities)))
        elif len(connection) == 2:
            results = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT ?o2
                WHERE
                {
                    ?s %s ?o1 .
                    ?o1 %s ?o2
                    FILTER(?s IN (%s)) .
                }
                LIMIT 100
                """ % (connection[0], connection[1], ','.join(entities)))
        else:
            raise ValueError("Unexpected number of parts to connection")
        return [result[0] for result in results]

    def get_entity_score(self, entity):
        """
        Use the number of relations as a measure of importance.
        """
        entity = ensure_prefixed(entity)

        value = self.entity_scores.get(entity)
        if value:
            return value

        #assert False
        logger.debug("Entity %s not found in cache", entity)
        try:
            result = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT COUNT(*)
                WHERE
                {
                    %s ?r ?o .
                }
                """ % entity)
            score = int(result[0][0])
        except timeout:
            logger.exception("Timeout attempting to get count for entity: %s", entity)
            score = 0
        self.entity_scores[entity] = score
        return score

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


def ensure_prefixed(entity):
    if entity.startswith('http'):
        return entity.replace('http://rdf.freebase.com/ns/', 'fb:')
    return entity
        
