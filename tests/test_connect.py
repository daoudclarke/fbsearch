from fbsearch.connect import Connector

connector = None

def setup_module():
    global connector
    connector = Connector()

def test_connect_examples():
    example = ('what time zone am i in cleveland ohio?', 'North American Eastern Time Zone')
    results = connector.search(*example)
    print results
    assert len(results) > 0

def test_connect_jamaican_dollar():
    example = ("what kind of money should i take to jamaica?", "Jamaican dollar")
    results = connector.search(*example)
    print results
    assert len(results) > 0

def test_apply_connection_query_has_no_entities():
    query =  'where is?'
    connection = (u'http://rdf.freebase.com/ns/book.written_work.author', u'http://rdf.freebase.com/ns/people.person.place_of_birth')
    results = connector.apply_connection(query, connection)
    print results
    assert len(results) == 0

def test_apply_connections():
    query, target = 'what is the name of justin bieber brother?', 'Jazmyn Bieber'
    connection = (u'http://rdf.freebase.com/ns/people.person.sibling_s', u'http://rdf.freebase.com/ns/people.sibling_relationship.sibling')
    results = connector.apply_connection(query, connection)
    assert target in results

def test_get_query_entities():
    query = 'what are the major cities in france?'
    ids = connector.get_query_entities(query)
    assert 'fb:en.france' in ids

def test_query_search_finds_china():
    query = "of china 2010?"
    results = connector.query_search(query)
    print results
    assert results[0][1]['id'] == 'fb:en.china'

def test_long_query_search_finds_china():
    query = "what is the official language of china 2010?"
    results = connector.query_search(query)
    print results
    ids = set(result[1]['id'] for result in results)
    assert 'fb:en.china' in ids

def teardown_module():
    connector.related.save_cache()
