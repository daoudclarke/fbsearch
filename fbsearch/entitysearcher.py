# Bismillahi-r-Rahmani-r-Rahim
"""
Search for entities in a query. Find those that match the longest
string in a query, but also some matching shorter substrings.
"""

import json

class EntitySearcher(object):
    def __init__(self, db_searcher):
        self.searcher = db_searcher

    def search(self, query):
        return self.searcher.search(query)


if __name__ == "__main__":
    import lucenesearch
    from lucenesearch import LuceneSearcher

    path = '/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/'
    db_searcher = LuceneSearcher(path)

    searcher = EntitySearcher(db_searcher)

    data_file = open('/home/dc/Experiments/sempre/lib/data/webquestions/dataset_11/webquestions.examples.train.json')
    examples = json.load(data_file)
    for example in examples:
        #print example, [d['text'] for d in searcher.search(example['utterance'])]
        print example, searcher.search(example['utterance'])
