# Bismillahi-r-Rahmani-r-Rahim

"""
Attempt to find connections between two freebase entities.
"""

from fbsearch import settings
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch.related import RelatedEntities
from fbsearch.evaluate import f1_score

from log import logger

import sys
import json
import sexpdata

class Connector(object):
    def __init__(self):
        self.related = RelatedEntities()
        self.searcher = LuceneSearcher('/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/')

    def search(self, query, target):
        query_entities = [result[1]['id'] for result in self.searcher.query_search(query)[:50]]
        query_names = [self.related.get_names(e) for e in query_entities]
        logger.debug("Query entities: %r", zip(query_entities, query_names))

        target_entities = self.related.search_exact(target)
        #target_entities = self.searcher.search(target, 400)
        #target_entities = [entity['id'] for entity in target_entities if entity['text'] == target.lower()]
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

    data_file = open(settings.DATASET_PATH)
    examples = json.load(data_file)
    f1_scores = []
    related_entities = RelatedEntities()
    for example in examples[100:200]:
        query = example['utterance']
        target_data = sexpdata.loads(example['targetValue'])
        targets = [symbol_to_string(description[1]) for description in target_data[1:]]
        best_score = 0.0
        for target in targets:
            print query, target
            result_ids = connector.search(query, target)
            print result_ids
            results = [related_entities.get_names(e[0]) for e in result_ids]
            print results
            score = f1_score(targets, results)
            if score > best_score:
                best_score = score
        f1_scores.append(best_score)
        print "F1 scores:", f1_scores
