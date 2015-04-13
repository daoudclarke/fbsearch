"""
Get info on relations to build up relation dataset.
"""

from fbsearch import settings
from fbsearch.related import RelatedEntities

import json


def get_dataset_info(dataset):
    related = RelatedEntities()
    for item in dataset:
        relation = item['relation']
        info = dict(item)
        info['name'] = related.get_names(relation)
        yield info

if __name__ == "__main__":
    dataset_file = open(settings.RELATION_DATASET_PATH)
    dataset = json.load(dataset_file)
    dataset = dataset[:20] + dataset[-20:]
    dataset_info = get_dataset_info(dataset)
    for info in dataset_info:
        print info
