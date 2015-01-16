from fbsearch.connect import Connector

def test_connect_construction():
    connector = Connector()



def test_connect_examples():
    example = ('what time zone am i in cleveland ohio?', 'North American Eastern Time Zone')
    connector = Connector()
    results = connector.search(*example)
    print results
    assert len(results) > 0

