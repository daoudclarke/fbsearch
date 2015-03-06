from fbsearch.oracle import OracleSystem

oracle = None

def test_oracle_connects_france_and_paris():
    query = 'what are the major cities in france?'
    target = [u'Paris']
    dataset = [(query, target)]

    oracle = OracleSystem(dataset)
    result = oracle.execute(query)
    oracle.connector.related.save_cache()
    assert list(result) == target

def test_oracle_finds_chinese_language():
    query = "what is the official language of china 2010?"
    target = [u"Chinese language"]
    dataset = [(query, target)]

    oracle = OracleSystem(dataset)
    result = oracle.execute(query)
    oracle.connector.related.save_cache()
    assert len(set(result) & set(target)) > 0

def test_oracle_finds_jamaican_dollar():
    query = "what kind of money should i take to jamaica?"
    target = [u"Jamaican dollar"]

    dataset = [(query, target)]

    oracle = OracleSystem(dataset)
    result = oracle.execute(query)
    oracle.connector.related.save_cache()
    assert list(result) == target

