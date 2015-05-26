# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""

from fbsearch import settings
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch.related import RelatedEntities
from fbsearch.analyse import get_f1_score
from expression import ConnectionExpression, ConjunctionExpression, SetExpression

from log import logger

import Levenshtein

from collections import defaultdict
from itertools import islice
import cPickle as pickle
import sys
import json
import re
import sexpdata

STOPWORDS = set("""
  a an and are as at be but by for if in into is it
  no not of on or such that the their then there these
  they this to was will with who what where
""".split())

ALLOWED_CHARS_PATTERN = re.compile('[\W_]+', re.UNICODE)

def get_results_cache():
    with open(settings.RESULTS_CACHE_PATH) as cache_file:
        logger.debug("Loading queries")
        queries = []
        while True:
            try:
                query, results = pickle.load(cache_file)
                logger.debug("Loaded query: %r", query)
                yield query, results
            except EOFError:
                break

def save_results_cache(items):
    with open(settings.RESULTS_CACHE_PATH, 'w') as cache_file:
        for query, result in items:
            pickle.dump((query, result), cache_file)
            cache_file.flush()


results_cache = {}
def load_results_cache():
    global results_cache
    if not results_cache:
        try:
            cache = get_results_cache()
            #cache = islice(cache, 0, 10)
            results_cache = dict(cache)
        except IOError:
            results_cache = {}
    return results_cache

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
            logger.info("Found %d entities in query cache", len(result))
            return result
        normalised_query = ALLOWED_CHARS_PATTERN.sub(' ', query)
        query_terms = [term for term in normalised_query.split() if term not in STOPWORDS]
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
                             if Levenshtein.ratio(doc['text'].lower(), unicode(subquery)) > 0.8]
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

    def get_all_results_and_expressions(self, query):
        if query in results_cache:
            return results_cache[query]

        logger.info("Getting best results for query: %r", query)
        query_entities = self.get_query_entities(query)
        relations = self.related.search(query_entities)

        logger.info("Building expressions from %d relations", len(relations))

        connection_expressions = {ConnectionExpression(relation): values
                                  for relation, values in relations.items()}
        connection_expression_items = connection_expressions.items()

        logger.info("Getting entity types")
        all_entities = set()
        for values in connection_expressions.values():
            all_entities |= values
        logger.debug("All entities: %r", all_entities)
        type_entities = defaultdict(set)
        for entity in all_entities:
            entity_types = self.related.get_types(entity)
            for t in entity_types:
                type_entities[t].add(entity)

        logger.debug("Entity types: %r", type_entities)

        type_expressions = {SetExpression((t,), entities): entities
                            for t, entities in type_entities.items()}

        expressions = connection_expressions
        expressions.update(type_expressions)

        # conjunction_expressions = {}
        # for i in range(len(connection_expression_items)):
        #     expression1, values1 = connection_expression_items[i]
        #     for j in range(i + 1, len(connection_expression_items)):
        #         expression2, values2 = connection_expression_items[j]
        #         values = values1 & values2
        #         if not values:
        #             continue
        #         expression = ConjunctionExpression(expression1, expression2)
        #         conjunction_expressions[expression] = values

        # expressions = connection_expressions
        # expressions.update(conjunction_expressions)

        logger.info("Computing results from %d expressions", len(expressions))

        results = []
        for expression, result_ids in expressions.items():
            result_names = set(self.related.get_names(result) for result in result_ids)
            logger.debug("Expression: %r, result %r",
                         expression, result_names)
            result = {
                'expression': expression,
                'results': result_names,
                }

            results.append(result)
        results_cache[query] = results
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
