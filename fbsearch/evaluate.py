from fbsearch.analyse import analyse
from fbsearch import convertingjson
from fbsearch.cachedoracle import CachedOracleSystem
#from log import logger

import pytest


def get_target_and_predicted_values(dataset, system):
    target_predicted_results = []
    for query, target_entities in dataset:
        #logger.info("Evaluating query %r", query)
        system_entities = system.execute(query)
        target_predicted_results.append({'target': target_entities,
                                         'predicted': system_entities})
    return target_predicted_results


def save(results, path):
    with open(path, 'w') as output_file:
        convertingjson.dump(results, output_file, indent=4)

if __name__ == "__main__":
    from fbsearch import settings
    from fbsearch.oracle import OracleSystem
    from fbsearch.tensor import TensorSystem
    from fbsearch.dataset import get_dataset
    from fbsearch import settings
    from random import Random
    from log import logger

    random = Random(1)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    random.shuffle(dataset)

    # logger.info("Training")
    # train_set = dataset[:2500]
    # system = TensorSystem(CachedOracleSystem)
    # system.train(train_set)

    dataset = dataset[:100]
    system = OracleSystem(dataset)

    logger.info("Testing")
    # test_set = dataset[2500:]
    results = get_target_and_predicted_values(dataset, system)
    save(results, settings.RESULTS_PATH)
    system.connector.searcher.save_cache()
    system.connector.save_cache()
    analyse()
