from fbsearch import settings
from entitysearcher import EntitySearcher
import lucenesearch
from lucenesearch import LuceneSearcher
from related import RelatedEntities

import json

if __name__ == "__main__":
    path = settings.LUCENE_PATH
    db_searcher = LuceneSearcher(path)

    searcher = EntitySearcher(db_searcher)
    related = RelatedEntities()

    data_file = open('/home/dc/Experiments/sempre/lib/data/webquestions/dataset_11/webquestions.examples.train.json')
    examples = json.load(data_file)
    for example in examples:
        #print example, [d['text'] for d in searcher.search(example['utterance'])]
        entities = searcher.search(example['utterance'])
        for entity in entities:
            print "Entity: ", entity
            triples = related.recurse(entity['id'])
            for s, r, o in triples:
                names = related.get_names(o)
                print s, r, o, names
