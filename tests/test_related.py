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


def test_connect_finds_jamaican_dollar():
    related = RelatedEntities()
    results = related.connect_names(['fb:en.jamaica'], ["Jamaican dollar"])
    print results
    assert results


def test_chinese_language():
    related = RelatedEntities()
    results = related.search_exact(u"Chinese language")
    print results
    assert results

def test_entity_score():
    related = RelatedEntities()
    france_score = related.get_entity_score('fb:en.france')
    random_score = related.get_entity_score('fb:m.0hndhfh')
    print "France:", france_score, "other:", random_score
    assert france_score > random_score
