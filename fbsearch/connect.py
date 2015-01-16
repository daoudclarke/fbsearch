# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""


from lucenesearch import LuceneSearcher
from related import RelatedEntities

from log import logger

import sys
import json
import sexpdata

class Connector(object):
    def __init__(self):
        self.related = RelatedEntities()
        self.searcher = LuceneSearcher('/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/')

    def search(self, query, target):
        query_entities = [result['id'] for result in self.searcher.search(query)[:50]]
        query_names = [self.related.get_names(e) for e in query_entities]
        logger.debug("Query entities: %r", zip(query_entities, query_names))

        target_entities = self.searcher.search(target, 400)
        target_entities = [entity['id'] for entity in target_entities if entity['text'] == target.lower()]
        logger.debug("Target entities: %r", target_entities)
        return self.related.connect(query_entities, target_entities)


def symbol_to_string(symbol):
    try:
        return symbol.value()
    except AttributeError:
        return symbol

if __name__ == "__main__":
    connector = Connector()
    # justin = 'fb:en.justin_bieber'
    # jaxon = 'fb:m.0gxnnwq'

    data_file = open('/home/dc/Experiments/sempre/lib/data/webquestions/dataset_11/webquestions.examples.train.json')
    examples = json.load(data_file)
    num_found = 0
    for example in examples[11:100]:
        query = example['utterance']
        target_data = sexpdata.loads(example['targetValue'])
        targets = [symbol_to_string(description[1]) for description in target_data[1:]]
        found = False
        for target in targets:
            print query, target
            results = connector.search(query, target)
            print results
            if results:
                found = True
        if found:
            num_found += 1
        else:
            break
        print "Number found: ", num_found
