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
        info['type'] = list(related.get_types(relation))
        info['schema'] = related.get_schema(relation)
        yield info

def save_info(dataset):
    dataset = list(dataset)
    with open(settings.RELATION_INFO_PATH, 'w') as dataset_file:
        json.dump(dataset, dataset_file, indent=4)


if __name__ == "__main__":
    dataset_file = open(settings.RELATION_DATASET_PATH)
    dataset = json.load(dataset_file)
    #dataset = dataset[:20] + dataset[-20:]
    dataset_info = list(get_dataset_info(dataset))
    for info in dataset_info[:100]:
        print info
    save_info(dataset_info)
