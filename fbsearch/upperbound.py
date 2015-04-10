from fbsearch.oracle import OracleSystem
from fbsearch.log import logger


class UpperBoundSystem(object):
    def __init__(self, test_oracle, oracle_class):
        self.test_oracle = test_oracle
        self.oracle_class = oracle_class

    def train(self, train_set):
        logger.info("Performing pre-computation for KNN classifier")

        train_oracle = self.oracle_class(train_set)
        self.known_expressions = set()
        for query, target in train_set:
            _, expressions = train_oracle.get_best_results_and_expressions(query)
            self.known_expressions.update(expressions)

    def get_best_expressions(self, query):
        _, expressions = self.test_oracle.get_best_results_and_expressions(query)
        return [expression for expression in expressions if expression in self.known_expressions]

    def execute(self, query):
        logger.debug("Executing query: %r", query)
        best_expressions = self.get_best_expressions(query)

        entities = self.connector.get_query_entities(query)
        for expression in best_expressions:
            try:
                result_ids = expression.apply(entities, self.connector.related)
            except Exception:
                logger.exception("Exception applying expression")
                result_ids = []
            result = set(self.connector.related.get_names(result) for result in result_ids)
            logger.debug("Searching for best expression, expression: %r, result: %r",
                         expression, result)
            if len(result) > 0:
                return result
        return set()

    def get_sentence_features(self, sentence):
        tokens = tokenize(sentence)
        return {token: 1.0 for token in tokens if token not in STOPWORDS}

    def __repr__(self):
        return type(self).__name__
