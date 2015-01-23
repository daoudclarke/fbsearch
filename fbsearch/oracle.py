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
        targets = self.query_targets[query]
        all_connections = set()
        for target in targets:
            connections = self.connector.search(query, target)
            all_connections |= set(connections)

        best_score = 0.0
        best_results = []
        for connection in connections:
            logger.debug("Querying connection: %s", connection)
            results = self.connector.apply_connection(query, connection)
            score = get_f1_score(targets, results)
            logger.debug("Target: %s, connection: %s, score: %f",
                         target, connection, score)
            if score > best_score:
                best_score = score
                best_results = results
        return best_results
