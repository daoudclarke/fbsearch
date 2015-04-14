"""
Generate a dataset consisting of relations classified as "interesting"
or "uninteresting". Interesting ones are any that are used by the
oracle at all. Uninteresting relations are a sample of those generated
by a search of depth 2 starting from entities in the training set.
"""

from fbsearch.connect import Connector
from fbsearch.related import RelatedEntities
from fbsearch.cachedoracle import CachedOracleSystem
from fbsearch.dataset import get_dataset
from fbsearch import settings

from collections import defaultdict
from random import Random
import json

def get_positive_relations(dataset):
    oracle = CachedOracleSystem(dataset)
    positive_relations = set()
    for query, target_entities in dataset:
        _, oracle_expressions = oracle.get_best_results_and_expressions(query)
        for expression in oracle_expressions:
            connections = expression.get_connections()
            for connection in connections:
                positive_relations |= set(connection)
    return positive_relations

def get_neutral_relations(dataset):
    connector = Connector()
    neutral_relations = defaultdict(int)
    random = Random(1)
    for query, target_entities in dataset[:10]:
        entities = connector.get_query_entities(query)
        relations = connector.related.search(entities)
        for relation, values in relations.items():
            for r in relation:
                neutral_relations[r] += len(values)
    return neutral_relations
                

def create_dataset():
    # Restrict to development set
    random = Random(2)

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    random.shuffle(dataset)

    dataset = dataset[:2500]

    positive_relations = get_positive_relations(dataset)
    neutral_relations = get_neutral_relations(dataset)
    negative_relations = {relation: count for relation, count in neutral_relations.items()
                          if relation not in positive_relations}
    dataset = [{'relation': relation, 'useful': True}
               for relation in positive_relations]
    dataset += [{'relation': relation, 'useful': False, 'count': count}
                for relation, count in negative_relations.items()]
    return dataset

def save_dataset(dataset):
    output_file = open(settings.RELATION_DATASET_PATH, 'w')
    json.dump(dataset, output_file, indent=4)

if __name__ == "__main__":
    dataset = create_dataset()
    save_dataset(dataset)