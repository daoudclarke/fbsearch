"""
Acts like an oracle but uses a file containing cached oracle analysis.
"""

from fbsearch.connect import Connector, load_results_cache, save_results_cache
from fbsearch.oracle import OracleSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch.log import logger

import cPickle as pickle    

def get_cache_results(dataset):
    connector = Connector()

    i = 0
    for query, target_entities in dataset:
        results = connector.get_all_results_and_expressions(query)
        yield query, results
        i += 1
        logger.info("Completed: %d", i)

        if i % 10 == 0:
            logger.info("Saving caches")
            connector.save_cache()
            logger.info("Saving complete")


if __name__ == "__main__":
    load_results_cache()
    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    results = get_cache_results(dataset)
    save_results_cache(results)
    
