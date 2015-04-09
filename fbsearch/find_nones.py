from fbsearch.analyse import analyse
from fbsearch import convertingjson
from fbsearch.evaluate import get_target_and_predicted_values, save


if __name__ == "__main__":
    from fbsearch import settings
    from fbsearch.oracle import OracleSystem
    from fbsearch.tensor import TensorSystem
    from fbsearch.dataset import get_dataset
    from fbsearch import settings
    from random import Random
    from log import logger

    random = Random(1)

    nones = set(open('nones.txt').read().split('\n'))

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)

    # logger.info("Training")
    # train_set = dataset[:2500]
    # system = TensorSystem(CachedOracleSystem)
    # system.train(train_set)

    dataset = dataset[:100]
    system = OracleSystem(dataset)

    logger.info("Testing")
    # test_set = dataset[2500:]
    results = get_target_and_predicted_values(dataset, system)
    with open('nones.json', 'w') as nones_file:
        for data, result in zip(dataset, results):
            if len(result['predicted']) == 0:
                nones_file.write(convertingjson.dumps(data) + '\n')

