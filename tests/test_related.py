from fbsearch.related import RelatedEntities

def test_connect_names():
    related = RelatedEntities()
    results = related.connect_names(['fb:en.france'], ['Paris'])
    print results
    assert results

def test_connect_multiple_names():
    related = RelatedEntities()
    results = related.connect_names(['fb:en.france'], ['Pouris', 'Lille'])
    print results
    assert results
