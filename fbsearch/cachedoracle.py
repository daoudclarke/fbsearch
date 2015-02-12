"""
Acts like an oracle but uses a file containing cached oracle analysis.
"""

from fbsearch.oracle import OracleSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch import convertingjson
from fbsearch.log import logger

import json

class CachedOracleSystem(object):
    def __init__(self, dataset):
        with open(settings.ORACLE_CACHE_PATH) as cache_file:
            valid_queries = set(query for query, _ in dataset)

            queries = [json.loads(row) for row in cache_file]
            self.queries = { item['query']: (item['results'], item['connection'] and tuple(item['connection']))
                             for item in queries if item['query'] in valid_queries }

    def execute(self, query):
        results, _ = self.get_best_results_and_connection(
            query)
        return results

    def get_best_results_and_connection(self, query):
        return self.queries[query]


def get_cache_oracle_data(dataset):
    oracle = OracleSystem(dataset)

    i = 0
    for query, target_entities in dataset:
        results, connection = oracle.get_best_results_and_connection(query)
        yield {
                'query': query,
                'results': results,
                'connection': connection,
                'target': target_entities,
                }
        i += 1
        logger.info("Completed: %d", i)


def save_oracle_data(oracle_results):
    with open(settings.ORACLE_CACHE_PATH, 'w') as cache_file:
        for result in oracle_results:
            serialised = convertingjson.dumps(result, cache_file)
            cache_file.write(serialised + '\n')
            cache_file.flush()

if __name__ == "__main__":
    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    oracle_data = get_cache_oracle_data(dataset)
    save_oracle_data(oracle_data)
    
