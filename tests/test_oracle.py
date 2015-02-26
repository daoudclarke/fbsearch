from fbsearch.oracle import OracleSystem

def test_tensor_system_can_learn():
    query = 'what are the major cities in france?'
    target = [u'Paris']
    dataset = [(query, target)]

    oracle = OracleSystem(dataset)
    result = oracle.execute(query)
    assert list(result) == target
