from fbsearch.analyse import analyse
from fbsearch import convertingjson
from fbsearch.evaluate import get_target_and_predicted_values, save
from fbsearch.log import logger

import json

if __name__ == "__main__":
    from fbsearch import settings
    from fbsearch.oracle import OracleSystem
    from fbsearch.tensor import TensorSystem
    from fbsearch.dataset import get_dataset
    from fbsearch import settings
    from random import Random
    # from log import logger

    random = Random(1)

    with open('nones.json') as nones_file:
        dataset = [json.loads(row) for row in nones_file]

    # nones = set(open('nones.txt').read().split('\n'))

    # dataset_file = open(settings.DATASET_PATH)
    # dataset = get_dataset(dataset_file)
    # dataset = [row for row in dataset if row[0] in nones]
    print dataset

    # logger.info("Training")
    # train_set = dataset[:2500]
    # system = TensorSystem(CachedOracleSystem)
    # system.train(train_set)

    dataset = dataset[:100]
    system = OracleSystem(dataset)

    #logger.info("Testing")
    # test_set = dataset[2500:]
    results = get_target_and_predicted_values(dataset, system)
    save(results, 'nones-output.json')
    analyse('nones-output.json')
