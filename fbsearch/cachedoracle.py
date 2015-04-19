"""
Acts like an oracle but uses a file containing cached oracle analysis.
"""

from fbsearch.oracle import OracleSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch.log import logger

import cPickle as pickle

class CachedOracleSystem(OracleSystem):
    def __init__(self, dataset):
        with open(settings.ORACLE_CACHE_PATH) as cache_file:
            valid_queries = set(query for query, _ in dataset)

            queries = []
            while True:
                try:
                    query = pickle.load(cache_file)
                    queries.append(query)
                except EOFError:
                    break
            self.queries = { item['query']: item['expressions']
                             for item in queries if item['query'] in valid_queries }

    def get_all_results_and_expressions(self, query):
        logger.info("Getting best results from cache for query: %r", query)
        return self.queries[query]


def get_cache_oracle_data(dataset):
    oracle = OracleSystem(dataset)

    i = 0
    for query, target_entities in dataset:
        expressions = oracle.get_all_results_and_expressions(query)
        yield {
                'query': query,
                'target': target_entities,
                'expressions': expressions,
                }
        i += 1
        logger.info("Completed: %d", i)

        if i % 10 == 0:
            logger.info("Saving caches")
            oracle.connector.save_cache()
            logger.info("Saving complete")


def save_oracle_data(oracle_results):
    with open(settings.ORACLE_CACHE_PATH, 'w') as cache_file:
        for result in oracle_results:
            pickle.dump(result, cache_file)
            cache_file.flush()

if __name__ == "__main__":
    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    oracle_data = get_cache_oracle_data(dataset)
    save_oracle_data(oracle_data)
    
