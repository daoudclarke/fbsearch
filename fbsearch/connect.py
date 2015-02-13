# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""

from fbsearch import settings
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch.related import RelatedEntities
from fbsearch.analyse import get_f1_score

from log import logger

import sys
import json
import sexpdata

class Connector(object):
    def __init__(self):
        self.related = RelatedEntities()
        self.searcher = LuceneSearcher(settings.LUCENE_PATH)
        try:
            with open(settings.CONNECTION_CACHE_PATH) as cache_file:
                self.connection_cache = json.load(cache_file)
        except IOError:
            self.connection_cache = {}

    def get_query_entities(self, query):
        return [result[1]['id'] for result in self.searcher.query_search(query)[:50]]

    def search(self, query, target):
        query_entities = self.get_query_entities(query)
        query_names = [self.related.get_names(e) for e in query_entities]
        logger.debug("Query entities: %r", zip(query_entities, query_names))

        target_entities = self.related.search_exact(target)
        logger.debug("Target entities: %r", target_entities)
        return self.related.connect(query_entities, target_entities)

    def search_all(self, query, targets):
        all_connections = set()
        for target in targets:
            connections = self.search(query, target)
            all_connections |= set(connections)
        return all_connections

    def apply_connection(self, query, connection):
        results = self.connection_cache.get(get_cache_key(query, connection))
        if results is not None:
            logger.debug("Found %d results in cache", len(results))
            return set(results)
        query_entities = self.get_query_entities(query)
        if len(query_entities) == 0:
            return set()
        result_ids = self.related.apply_connection(query_entities, connection)
        results = set(self.related.get_names(result) for result in result_ids)
        logger.debug("Found %d results, caching", len(results))
        self.connection_cache[get_cache_key(query, connection)] = list(results)
        return results

    def save_cache(self):
        with open(settings.CONNECTION_CACHE_PATH, 'w') as cache_file:
            json.dump(self.connection_cache, cache_file, indent=4)

def symbol_to_string(symbol):
    try:
        return symbol.value()
    except AttributeError:
        return symbol

def get_cache_key(query, connection):
    return '___'.join([query, '|'.join(connection)])

if __name__ == "__main__":
    connector = Connector()
    # justin = 'fb:en.justin_bieber'
    # jaxon = 'fb:m.0gxnnwq'

    data_file = open(settings.DATASET_PATH)
    examples = json.load(data_file)
    f1_scores = []
    related_entities = RelatedEntities()
    for example in examples[100:200]:
        query = example['utterance']
        target_data = sexpdata.loads(example['targetValue'])
        targets = [symbol_to_string(description[1]) for description in target_data[1:]]
        best_score = 0.0
        for target in targets:
            print query, target
            result_ids = connector.search(query, target)
            print result_ids
            results = [related_entities.get_names(e[0]) for e in result_ids]
            print results
            score = get_f1_score(targets, results)
            if score > best_score:
                best_score = score
        f1_scores.append(best_score)
        print "F1 scores:", f1_scores
