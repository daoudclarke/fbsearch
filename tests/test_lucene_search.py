
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch import settings

def test_simple_search_finds_china():
    searcher = LuceneSearcher(settings.LUCENE_PATH)
    query = "china"
    results = searcher.search(query)
    print results
    ids = set(result['id'] for result in results)
    for i in sorted(ids):
        print i
    assert 'fb:en.china' in ids or 'fb:m.0d05w3' in ids
