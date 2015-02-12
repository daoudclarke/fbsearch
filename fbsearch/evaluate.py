from fbsearch.analyse import analyse
from fbsearch import convertingjson
from fbsearch.cachedoracle import CachedOracleSystem

import pytest


def get_target_and_predicted_values(dataset, system):
    target_predicted_results = []
    for query, target_entities in dataset:
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
    cached_oracle = CachedOracleSystem(dataset)
    dataset = [(query, targets) for query, targets in dataset
               if query in cached_oracle.queries]
    random.shuffle(dataset)

    logger.info("Training")
    train_set = dataset[:2500]
    system = TensorSystem(CachedOracleSystem)
    system.train(train_set)

    logger.info("Testing")
    test_set = dataset[2500:3000]
    results = get_target_and_predicted_values(test_set, system)
    save(results, settings.RESULTS_PATH)    
    analyse()
