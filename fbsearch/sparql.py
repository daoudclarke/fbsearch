from SPARQLWrapper import SPARQLWrapper, JSON

from log import logger

class SPARQLStore(object):
    def __init__(self):
        self.endpoint = SPARQLWrapper("http://localhost:3093/sparql")
        self.endpoint.setTimeout(60)

    def query(self, sparql):
        self.endpoint.setQuery(sparql)
        self.endpoint.setReturnFormat(JSON)
        results = self.endpoint.query().convert()
        vars_ = results['head']['vars']
        #logger.debug("Sparql raw result: %r", results)
        return [tuple(result[v]['value'] for v in vars_)
                for result in results['results']['bindings']]


if __name__ == "__main__":
    store = SPARQLStore()
    results = store.query("""
            prefix fb: <http://rdf.freebase.com/ns/>
            SELECT *
            WHERE
            {
                fb:en.north_american_eastern_time_zone ?r ?o .
            }
    """)
    print results
