"""
Acts like an oracle but uses a file containing cached oracle analysis.
"""

from fbsearch.oracle import OracleSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch import convertingjson

class CachedOracleSystem(object):
    def __init__(self, dataset):
        self.query_targets = dict(dataset)
        self.connector = Connector()
        self.related = RelatedEntities()

    def execute(self, query):
        results, _ = self.get_best_results_and_connection(
            query)
        return results

    #def get_best_results_and_connection(self, query):



def get_cache_oracle_data(dataset):
    oracle = OracleSystem(dataset)

    oracle_results = []
    for query, target_entities in dataset:
        results, connection = oracle.get_best_results_and_connection(query)
        oracle_results.append({
                'query': query,
                'results': results,
                'connection': connection,
                })
    return oracle_results


def save_oracle_data(oracle_results):
    with open(settings.ORACLE_CACHE_PATH, 'w') as cache_file:
        convertingjson.dump(oracle_results, cache_file, indent=4)


if __name__ == "__main__":
    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)[:2]
    oracle_data = get_cache_oracle_data(dataset)
    save_oracle_data(oracle_data)
    
