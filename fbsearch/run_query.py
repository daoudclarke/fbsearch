from fbsearch.connect import Connector

example = ('what time zone cleveland?', 'North American Eastern Time Zone')
connector = Connector()
results = connector.search(*example)
print results


