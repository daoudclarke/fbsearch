# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""

from fbsearch import settings
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch.related import RelatedEntities
from fbsearch.analyse import get_f1_score

from log import logger

import Levenshtein

import sys
import json
import sexpdata

STOPWORDS = set("""
  a an and are as at be but by for if in into is it
  no not of on or such that the their then there these
  they this to was will with who what where
""".split())


class Connector(object):
    def __init__(self):
        self.related = RelatedEntities()
        self.searcher = LuceneSearcher(settings.LUCENE_PATH)
        try:
            with open(settings.CONNECTION_CACHE_PATH) as cache_file:
                self.connection_cache = json.load(cache_file)
        except IOError:
            self.connection_cache = {}
        try:
            with open(settings.QUERY_ENTITY_CACHE_PATH) as cache_file:
                self.query_entity_cache = json.load(cache_file)
        except IOError:
            self.query_entity_cache = {}

    def get_query_entities(self, query):
        query_entities = [result[1]['id'] for result in self.query_search(query)]
        logger.debug("Query entities: %r", query_entities)
        return query_entities

    def query_search(self, query):
        """
        Find entities that are contained as substrings in the query.
        """
        result = self.query_entity_cache.get(query)
        if result is not None:
            logger.debug("Found entities in query cache")
            return result
        query_terms = [term for term in query.split() if term not in STOPWORDS]
        logger.debug("Getting query entities for query terms: %r", query_terms)
        all_entities = []
        subqueries = []
        for i in range(len(query_terms) - 1):
            subqueries.append(' '.join(query_terms[i:i+2]))

        subqueries += query_terms
        for subquery in subqueries:
            logger.debug("Applying subquery %r", subquery)
            docs = self.searcher.search(subquery)
            filtered_docs = [doc for doc in docs
                             if Levenshtein.ratio(doc['text'], unicode(subquery)) > 0.75]
            logger.debug("Filtered to %d of %d docs", len(filtered_docs), len(docs))
            scores_docs = [(self.related.get_entity_score(doc['id']), doc) for doc in filtered_docs]
            sorted_scores_docs = sorted(scores_docs, reverse=True)
            logger.debug("Sorted scores and docs: %r", sorted_scores_docs)
            all_entities += sorted_scores_docs[:10]
        logger.debug("Found %d entities, caching", len(all_entities))
        result = sorted(all_entities, reverse=True)
        logger.debug("Top entities: %r", result[:10])
        self.query_entity_cache[query] = result
        return result

    def score_doc(doc):
        entity = doc['id']
        

    def search(self, query, target):
        query_entities = self.get_query_entities(query)
        return self.related.connect_names(query_entities, [target])

    def search_all(self, query, targets):
        query_entities = self.get_query_entities(query)
        return self.related.connect_names(query_entities, targets)

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
        with open(settings.QUERY_ENTITY_CACHE_PATH, 'w') as cache_file:
            json.dump(self.query_entity_cache, cache_file, indent=4)
        self.related.save_cache()

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
