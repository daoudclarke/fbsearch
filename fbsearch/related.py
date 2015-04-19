# from rdflib.store import Store
# from rdflib.plugin import get as plugin
# from rdflib import URIRef
# #from rdflib.namespace import RDF
# from rdflib.term import Literal
# from rdflib import BNode

from sparql import SPARQLStore

#from rdflib.plugins.stores.regexmatching import REGEXTerm

from fbsearch import settings

from collections import defaultdict
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
            logger.info("Loaded %d entity scores in cache", len(self.entity_scores))
        except IOError:
            self.entity_scores = {}
        try:
            cache_file = open(settings.ENTITY_NAME_CACHE_PATH)
            self.entity_names = json.load(cache_file)
            logger.info("Loaded %d entity names in cache", len(self.entity_scores))
        except IOError:
            self.entity_names = {}
            

    def save_cache(self):
        logger.info("Saving entity score cache")
        with open(settings.ENTITY_SCORE_CACHE_PATH, 'w') as cache_file:
            json.dump(self.entity_scores, cache_file)
        with open(settings.ENTITY_NAME_CACHE_PATH, 'w') as cache_file:
            json.dump(self.entity_names, cache_file)

    def get_names(self, entity):
        entity = ensure_prefixed(entity)
        if entity in self.entity_names:
            return self.entity_names[entity]

        names = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT *
            WHERE
            {
                %s fb:type.object.name ?o .
            }
            """ % entity)
        assert len(names) <= 1
        name = names[0][0] if len(names) > 0 else None
        self.entity_names[entity] = name
        return name

    def search(self, entities):
        """
        Find entities related to the given one
        """
        #assert type(entity) == unicode, "Expected unicode, got %r" % type(entity)
        
        #uri = ensure_prefixed(entity)
        #logger.debug("Getting triples for %s", uri)
        try:
            connections = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT DISTINCT ?r
                WHERE
                {
                    ?s ?r ?o .
                    ?r fb:type.property.schema ?schema .
                    FILTER(?s IN (%s)) .
                    FILTER(isURI(?o)) .
                    FILTER(!regex(?r, ".*type.*")) .
                }
                """ % ','.join(entities))

            logger.info("Got %d results", len(connections))
        except timeout:
            logger.exception("Timeout getting simple connections")
            connections = []

        try:
            second_order = self.store.query("""
                prefix fb: <http://rdf.freebase.com/ns/>
                SELECT DISTINCT ?r1 ?r2
                WHERE
                {
                    ?s ?r1 ?o1 .
                    ?o1 ?r2 ?o2 .
                    ?r1 fb:type.property.schema ?schema1 .
                    ?r2 fb:type.property.schema ?schema2 .
                    FILTER(?s IN (%s)) .
                    FILTER(isURI(?o2)) .
                    FILTER(!regex(?r1, ".*type.*")) .
                    FILTER(!regex(?r2, ".*type.*")) .
                }
                """ % ','.join(entities))
        except timeout:
            logger.info("Timeout getting second order connections")
            second_order = []

        logger.info("Got %d second order relations", len(second_order))
        connections += second_order

        relations = {}
        for connection in connections:
            results = self.apply_connection(entities, connection)
            relations[connection] = set(results)

        return relations

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
            try:
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
            except timeout:
                logger.exception("Timeout applying secondary connection.")
                results = []
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

    def get_types(self, entity):
        entity = ensure_prefixed(entity)
        entity_types = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT ?o
            WHERE
            {
                %s fb:type.object.type ?o .
            }
            """ % entity)
        logger.debug("Found entity type: %r", entity_types)
        return set(x[0] for x in entity_types)


    def get_schema(self, relation):
        relation = ensure_prefixed(relation)
        schema = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT ?o
            WHERE
            {
                %s fb:type.property.schema ?o .
            }
            """ % relation)
        assert len(schema) <= 1
        logger.debug("Found schema: %r", schema)
        return schema[0][0] if schema else None


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
        
