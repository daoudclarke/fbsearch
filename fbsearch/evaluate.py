from fbsearch.analyse import analyse_results
from fbsearch import convertingjson

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
    random.shuffle(dataset)

    logger.info("Training")
    train_set = dataset[:10]
    system = TensorSystem()
    system.train(train_set)

    logger.info("Testing")
    test_set = dataset[50:100]
    results = get_target_and_predicted_values(test_set, system)
    save(results, settings.RESULTS_PATH)

    mean, error = analyse_results(results)
    print "F1 average: %f +/- %f" % (mean, error)
