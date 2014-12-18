# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""


from lucenesearch import LuceneSearcher
from sparql import SPARQLStore

from log import logger

import sys

class Connector(object):
    def __init__(self):
        self.store = SPARQLStore()
        self.searcher = LuceneSearcher('/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/')

    def search(self, query, target):
        query_entities = [result['id'] for result in self.searcher.search(query)[:10]]
        logger.debug("Query entities: %r", query_entities)

        target_entities = self.searcher.search(target)
        target_entities = [entity['id'] for entity in target_entities if entity['text'] == target]

        assert len(target_entities) == 1
        target_entity = target_entities[0]
        logger.debug("Target entities: %r", target_entities)

        entities = self.store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT ?r1, ?o1, ?r2 
            WHERE
            {
                ?s ?r1 ?o1 .
                ?o1 ?r2 %s .
                FILTER(?s IN (%s)) .
            }
            """ % (target_entity, ','.join(query_entities)))
        return entities


if __name__ == "__main__":
    connector = Connector()
    # justin = 'fb:en.justin_bieber'
    # jaxon = 'fb:m.0gxnnwq'
    query = sys.argv[1]
    target = sys.argv[2]
    print connector.search(query, target)
    
