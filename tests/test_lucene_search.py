
from fbsearch.lucenesearch import LuceneSearcher
from fbsearch import settings

def test_finds_single_named_entity():
    searcher = LuceneSearcher(settings.LUCENE_PATH)
    results = searcher.query_search('what time zone am i in cleveland ohio?')
    for result in results:
        print result
    ids = [result[1]['id'] for result in results]
    print ids
    assert 'fb:en.cleveland_ohio' in ids[:50]

def test_search_query_single_word_entity():
    searcher = LuceneSearcher(settings.LUCENE_PATH)
    results = searcher.query_search('where is mallorca?')
    assert len(results) > 0

def test_finds_entity_associated_with_single_term():
    searcher = LuceneSearcher(settings.LUCENE_PATH)
    query = 'what are the major cities in france?'
    results = searcher.query_search(query)
    print results
    ids = set(result[1]['id'] for result in results)
    assert 'fb:en.france' in ids
