from fbsearch.related import RelatedEntities


def test_finds_aliases():
    related = RelatedEntities()
    results = related.search_exact('North American Eastern Time Zone')
    name = related.get_names(results[0])
    assert name == "Eastern Time Zone"
