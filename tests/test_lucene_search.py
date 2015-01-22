from fbsearch.lucenesearch import LuceneSearcher

def test_finds_single_named_entity():
    searcher = LuceneSearcher('/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/')
    results = searcher.query_search('what time zone am i in cleveland ohio?')
    for result in results:
        print result
    ids = [result[1]['id'] for result in results]
    print ids
    assert 'fb:en.cleveland_ohio' in ids[:50]