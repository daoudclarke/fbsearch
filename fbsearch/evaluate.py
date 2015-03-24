from fbsearch.analyse import analyse, analyse_ranks, analyse_system_best
from fbsearch import convertingjson
from fbsearch.cachedoracle import CachedOracleSystem
from fbsearch import settings
from fbsearch.oracle import OracleSystem
from fbsearch.tensor import TensorSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch.knn import NNSystem
from random import Random
from log import logger

import cPickle as pickle

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

def evaluate_cached_oracle():
    random = Random(1)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    random.shuffle(dataset)

    system = CachedOracleSystem(dataset)

    dataset = [item for item in dataset if item[0] in system.queries]

    logger.info("Testing on %d items", len(dataset))
    results = get_target_and_predicted_values(dataset, system)
    save(results, settings.RESULTS_PATH)
    analyse()

def evaluate_tensor():
    random = Random(1)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    random.shuffle(dataset)

    logger.info("Training")
    train_set = dataset[:100] #2500]
    system = TensorSystem(CachedOracleSystem)
    system.train(train_set)

    test_set = dataset[2500:2510]
    logger.info("Testing on %d items", len(test_set))
    results = get_target_and_predicted_values(test_set, system)
    save(results, settings.RESULTS_PATH)
    system.connector.save_cache()
    analyse()

def get_rank(system_expressions, oracle_expressions, worst_possible_rank):
    if len(oracle_expressions) > 0:
        if len(set(system_expressions) & oracle_expressions) == 0:
            return worst_possible_rank
        else:
            rank = 0
            found_rank = None
            for expression in system_expressions:
                if expression in oracle_expressions:
                    return rank
                rank += 1
    else:
        return -1

def get_ranks(dataset, system):
    """
    Return the rank of the first correct answer returned by the
    system.
    """

    results = []
    oracle = CachedOracleSystem(dataset)
    all_expressions = set()
    for _, expressions in oracle.queries.values():
        all_expressions |= set(expressions)
    # all_expression_sets = [expressions for expressions in oracle.queries.values()]
    # all_possible_expressions = reduce(set.__or__, all_expression_sets)
    worst_possible_rank = len(all_expressions)
    logger.info("Number of possible expressions: %d", worst_possible_rank)
    for query, target_entities in dataset:
        logger.debug("Evaluating query %r", query)
        system_expressions = system.get_best_expressions(query)
        _, oracle_expressions = oracle.get_best_results_and_expressions(query)
        found_rank = get_rank(system_expressions, oracle_expressions, worst_possible_rank)
        logger.debug("Found rank: %r", found_rank)
        results.append({'query': query,
                        'target': target_entities,
                        'rank': found_rank})
    return results

def get_system_best(dataset, system):
    """
    Find the proportion of items for which the system returns a
    correct answer in its top 10 results.
    """

    results = []
    oracle = CachedOracleSystem(dataset)
    for query, target_entities in dataset:
        logger.debug("Evaluating query %r", query)
        system_expressions = system.get_best_expressions(query)
        _, oracle_expressions = oracle.get_best_results_and_expressions(query)
        results.append({'query': query,
                        'oracle': oracle_expressions,
                        'system': system_expressions})
    return results
    

def evaluate_quickly():
    output_path = 'system-best.json'

    random = Random(2)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    random.shuffle(dataset)

    logger.info("Training")
    train_set = dataset[:2500]
    #system = TensorSystem(CachedOracleSystem)
    system = NNSystem(CachedOracleSystem)
    system.train(train_set)

    test_set = dataset[2500:]
    logger.info("Testing on %d items", len(test_set))
    results = get_system_best(test_set, system)
    with open(output_path, 'w') as output_file:
        pickle.dump(results, output_file)
    system.connector.save_cache()
    print analyse_system_best(output_path)

if __name__ == "__main__":
    evaluate_quickly()
