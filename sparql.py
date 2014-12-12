from SPARQLWrapper import SPARQLWrapper, JSON

from log import logger

class SPARQLStore(object):
    def __init__(self):
        self.endpoint = SPARQLWrapper("http://localhost:3093/sparql")

    def query(self, sparql):
        self.endpoint.setQuery(sparql)
        self.endpoint.setReturnFormat(JSON)
        results = self.endpoint.query().convert()
        vars_ = results['head']['vars']
        #logger.debug("Sparql raw result: %r", results)
        return [tuple(result[v]['value'] for v in vars_)
                for result in results['results']['bindings']]
