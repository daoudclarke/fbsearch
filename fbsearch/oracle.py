"""
Query answering system that is allowed to cheat, providing an upper
bound on performance.
"""

from fbsearch.connect import Connector
from fbsearch.analyse import get_f1_score
from fbsearch.log import logger

from itertools import combinations

class OracleSystem(object):
    def __init__(self, dataset):
        self.query_targets = dict(dataset)
        self.connector = Connector()

    def train(self, dataset):
        pass

    def execute(self, query):
        results, _ = self.get_best_results_and_expressions(
            query)
        return results

    def get_best_results_and_expressions(self, query):
        logger.info("Getting best results from oracle for query: %r", query)

        targets = self.query_targets[query]
        results = self.connector.get_all_results_and_expressions(query)

        best_score = 0.0
        best_results = []
        best_expressions = []
        for result in results:
            expression = result['expression']
            results = result['results']
            score = get_f1_score(targets, results)
            if score == 0.0:
                continue
            if score > best_score:
                logger.debug("Found new best expression: %r, results: %r", expression, results)
                best_score = score
                best_results = results
                best_expressions = [expression]
            elif score == best_score:
                logger.debug("Found equally good expression: %r, results: %r", expression, results)
                best_expressions.append(expression)

        logger.info("Best score: %f, best expressions: %r", best_score, best_expressions)
        return best_results, set(best_expressions)


    def get_best_expressions(self, query):
        results, expressions = self.get_best_results_and_expressions(query)
        return list(expressions)
