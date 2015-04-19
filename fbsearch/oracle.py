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

    def train(self, dataset):
        pass

    def execute(self, query):
        results, _ = self.get_best_results_and_expressions(
            query)
        return results

    def get_best_results_and_expressions(self, query):
        logger.info("Getting best results from oracle for query: %r", query)
        results = self.get_all_results_and_expressions(query)

        best_score = 0.0
        best_results = []
        best_expressions = []
        for result in results:
            score = result['score']
            expression = result['expression']
            results = result['results']
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


    def get_all_results_and_expressions(self, query):
        logger.info("Getting best results for query: %r", query)
        targets = self.query_targets[query]
        query_entities = self.connector.get_query_entities(query)
        relations = self.connector.related.search(query_entities)

        # all_values = reduce(set.__or__, relations.values())
        # names = {self.connector.related.get_names(x) for x in all_values}
        # if all_names & set(targets) == set():
        #     logger.info("No values in common: %r, %r", targets, all_names)

        logger.info("Building expressions from %d relations", len(relations))

        connection_expressions = {ConnectionExpression(relation): values
                                  for relation, values in relations.items()}
        connection_expression_items = connection_expressions.items()

        conjunction_expressions = {}
        for i in range(len(connection_expression_items)):
            expression1, values1 = connection_expression_items[i]
            for j in range(i + 1, len(connection_expression_items)):
                expression2, values2 = connection_expression_items[j]
                values = values1 & values2
                if not values:
                    continue
                expression = ConjunctionExpression(expression1, expression2)
                conjunction_expressions[expression] = values

        expressions = connection_expressions
        expressions.update(conjunction_expressions)

        logger.info("Computing results from %d expressions", len(expressions))

        results = []
        for expression, result_ids in expressions.items():
            result_names = set(self.connector.related.get_names(result) for result in result_ids)

            score = get_f1_score(targets, result_names)
            logger.debug("Target: %s, expression: %r, score: %f, result %r",
                         targets, expression, score, result_names)
            result = {
                'expression': expression,
                'results': result_names,
                'score': score,
                'target': targets,
                }

            results.append(result)
        return results

    def get_best_expressions(self, query):
        results, expressions = self.get_best_results_and_expressions(query)
        return list(expressions)
