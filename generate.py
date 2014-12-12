from entitysearcher import EntitySearcher
import lucenesearch
from lucenesearch import LuceneSearcher
from related import RelatedEntities

import json

if __name__ == "__main__":
    path = '/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/'
    db_searcher = LuceneSearcher(path)

    searcher = EntitySearcher(db_searcher)
    related = RelatedEntities()

    data_file = open('/home/dc/Experiments/sempre/lib/data/webquestions/dataset_11/webquestions.examples.train.json')
    examples = json.load(data_file)
    for example in examples:
        #print example, [d['text'] for d in searcher.search(example['utterance'])]
        entities = searcher.search(example['utterance'])
        for entity in entities:
            print entity['id'], related.search(entity['id'])
