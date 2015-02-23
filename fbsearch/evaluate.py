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
    from fbsearch.analyse import get_f1_score
    from random import Random
    from log import logger
    import json

    random = Random(1)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    cached_oracle = CachedOracleSystem(dataset)
    #random.shuffle(dataset)

    logger.info("Training")
    train_set = dataset[:2500]
    system = cached_oracle
    # system = OracleSystem(dataset)
    #system.train(train_set)

    logger.info("Testing")
    test_set = dataset
    results = get_target_and_predicted_values(test_set, system)

    # with open(settings.DATASET_PATH) as dataset_file:
    #     original_dataset = json.load(dataset_file)
    # hard_dataset = []
    # for item, result in zip(original_dataset, results):
    #     f1_score = get_f1_score(result['target'], result['predicted'])
    #     print f1_score
    #     if f1_score < 0.5:
    #         hard_dataset.append(item)
    # save(hard_dataset, 'oracle_errors.json')

    save(results, settings.RESULTS_PATH)
    # system.connector.searcher.save_cache()
    # system.connector.save_cache()
    analyse()
