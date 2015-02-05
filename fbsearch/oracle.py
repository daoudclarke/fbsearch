"""
Query answering system that is allowed to cheat, providing an upper
bound on performance.
"""

from fbsearch.connect import Connector
from fbsearch.related import RelatedEntities
from fbsearch.analyse import get_f1_score
from fbsearch.log import logger

class OracleSystem(object):
    def __init__(self, dataset):
        self.query_targets = dict(dataset)
        self.connector = Connector()
        self.related = RelatedEntities()

    def execute(self, query):
        results, _ = self.get_best_results_and_connection(
            query)
        return results

    def get_best_results_and_connection(self, query):
        targets = self.query_targets[query]
        connections = self.connector.search_all(query, targets)

        best_score = 0.0
        best_results = []
        best_connection = None
        for connection in connections:
            logger.debug("Querying connection: %s", connection)
            results = self.connector.apply_connection(query, connection)
            score = get_f1_score(targets, results)
            logger.debug("Target: %s, connection: %s, score: %f",
                         targets, connection, score)
            if score > best_score:
                best_score = score
                best_results = results
                best_connection = connection
        return best_results, best_connection
