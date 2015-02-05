from fbsearch.analyse import analyse_results

import pytest
import json




def get_target_and_predicted_values(dataset, system):
    target_predicted_results = []
    for query, target_entities in dataset:
        system_entities = system.execute(query)
        target_predicted_results.append({'target': target_entities,
                                         'predicted': system_entities})
    return target_predicted_results


class ConvertingJSONEncoder(json.JSONEncoder):
    """
    Automatically convert sets etc to lists.
    """
    def default(self, input_object):
        if isinstance(input_object, set):
           return list(input_object)
        return JSONEncoder.default(self, o)


def save(results, path):
    output_file = open(path, 'w')
    encoder = ConvertingJSONEncoder()
    json.dump(results, output_file,
              cls=ConvertingJSONEncoder,
              indent=4)


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
    train_set = dataset[:500]
    system = TensorSystem()
    system.train(train_set)

    logger.info("Testing")
    test_set = dataset[500:1000]
    results = get_target_and_predicted_values(test_set, system)
    save(results, settings.RESULTS_PATH)

    mean, error = analyse_results(results)
    print "F1 average: %f +/- %f" % (mean, error)
