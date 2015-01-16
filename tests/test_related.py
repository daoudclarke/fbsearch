from fbsearch.related import RelatedEntities

def test_exact_search_finds_names():
    related = RelatedEntities()
    results = related.search_exact('Eastern Time Zone')
    name = related.get_names(results[0])
    assert name == "Eastern Time Zone"


def test_exact_search_finds_aliases():
    related = RelatedEntities()
    results = related.search_exact('North American Eastern Time Zone')
    name = related.get_names(results[0])
    assert name == "Eastern Time Zone"
