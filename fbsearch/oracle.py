"""
Query answering system that is allowed to cheat, providing an upper
bound on performance.
"""

from fbsearch.connect import Connector
from fbsearch.analyse import get_f1_score
from fbsearch.log import logger
from expression import ConnectionExpression, ConjunctionExpression

from itertools import combinations

class OracleSystem(object):
    def __init__(self, dataset):
        self.query_targets = dict(dataset)
        self.connector = Connector()

    def execute(self, query):
        results, _ = self.get_best_results_and_expressions(
            query)
        return results

    def get_best_results_and_expressions(self, query):
        logger.info("Getting best results for query: %r", query)
        targets = self.query_targets[query]
        connections = self.connector.search_all(query, targets)
        logger.info("Found connections: %r", connections)

        # connection_results = {}
        # for connection in connections:
        #     logger.debug("Querying connection: %s", connection)
        #     results = self.connector.apply_connection(query, connection)
        #     connection_results[connection] = results

        connection_expressions = [ConnectionExpression(connection)
                                  for connection in connections]
        conjunction_expressions = [ConjunctionExpression(connection1, connection2)
                                   for connection1, connection2 in
                                   combinations(connection_expressions, 2)]
        expressions = connection_expressions + conjunction_expressions
        logger.debug("Applying expressions: %r", expressions)

        query_entities = self.connector.get_query_entities(query)
            
        best_score = 0.0
        best_results = []
        best_expressions = []
        for expression in expressions:
            result_ids = expression.apply(query_entities, self.connector.related)
            result_names = set(self.connector.related.get_names(result) for result in result_ids)

            score = get_f1_score(targets, result_names)
            logger.debug("Target: %s, expression: %r, score: %f, result %r",
                         targets, connection, score, result_names)
            if score > best_score:
                logger.debug("Found new best expression: %r, results: %r", expression, result_names)
                best_score = score
                best_results = result_names
                best_expressions = [expression]
            elif score == best_score:
                logger.debug("Found equally good expression: %r, results: %r", expression, result_names)                
                best_expressions.append(expression)

        logger.info("Best score: %f, best expressions: %r", best_score, best_expressions)
        return best_results, set(best_expressions)
