from fbsearch.connect import Connector

def test_connect_construction():
    connector = Connector()



def test_connect_examples():
    example = ('what time zone am i in cleveland ohio?', 'North American Eastern Time Zone')
    connector = Connector()
    results = connector.search(*example)
    print results
    assert len(results) > 0

def test_apply_connections():
    query, target = 'what is the name of justin bieber brother?', 'Jazmyn Bieber'
    connector = Connector()
    connections = connector.search(query, target)
    print connections
    results = connector.apply_connection(query, connections[1])
    assert target in results
