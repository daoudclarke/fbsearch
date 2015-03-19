from fbsearch.oracle import OracleSystem
from fbsearch.connect import Connector

from operator import itemgetter
from collections import Counter
import random

import numpy as np

from gensim.utils import simple_preprocess as tokenize
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV

from log import logger

STOPWORDS = {'what', 'is', 'the', 'of', 'to'}
    

class TensorSystem(object):
    def __init__(self, oracle_class=OracleSystem):
        self.random = random.Random(1)
        self.connector = Connector()
        self.possible_connections = None
        self.oracle_class = oracle_class

    def train(self, train_set):
        logger.info("Training tensor based classifier")
        features = []
        values = []

        oracle = self.oracle_class(train_set)
        query_expressions = {}
        for query, target in train_set:
            _, expressions = oracle.get_best_results_and_expressions(query)
            if len(expressions) == 0:
                continue
            query_expressions[query] = expressions
        logger.info("Obtained %d items from oracle", len(query_expressions))

        all_expressions = Counter()
        for expressions in query_expressions.values():
            all_expressions.update(expressions)
        logger.info("Found %d unique expressions", len(all_expressions))
        frequent = all_expressions.most_common(1500)
        logger.info("Frequency of first and last frequent expression: %d",
                    frequent[0][1], frequent[-1][1])
        self.frequent_expressions = set(expression for expression, _ in frequent)

        all_features = []
        values = []
        for query, correct_expressions in query_expressions.iteritems():
            logger.debug("Building features for query %r, %d correct expressions",
                         query, len(correct_expressions))
            expression_counts = {expression: all_expressions[expression]
                                 for expression in correct_expressions}
            best_expressions = sorted(expression_counts.items(), key=itemgetter(1),
                                      reverse=True)
            logger.info("Best expressions: %r", best_expressions[:3])
            best_expressions = set(expression for expression, _ in best_expressions)
            query_tokens = self.get_sentence_features(query)

            for expression in best_expressions & self.frequent_expressions:
                features = self.get_query_expression_features(query_tokens, expression)
                all_features.append(features)
                values.append(1)

            for expression in self.frequent_expressions - correct_expressions:
                features = self.get_query_expression_features(query_tokens, expression)
                all_features.append(features)
                values.append(0)
        self.all_expressions = list(all_expressions)

        logger.info("Training - building vectors with %d features", len(all_features))
        self.vectorizer = DictVectorizer()
        vectors = self.vectorizer.fit_transform(all_features)


        logger.info("Training classifier")
        #svm = LinearSVC(random_state=1, tol=1e-5)
        svm = LinearSVC(tol=1e-6)

        parameters = {'C': [0.1, 1.0, 10.0, 100.0]}
        self.classifier = GridSearchCV(svm, parameters, scoring='f1')

        self.classifier.fit(vectors, values)
        logger.info("Best score in cross validation: %f", self.classifier.best_score_)

        self.classifier = self.classifier.best_estimator_

        logger.info("SVM classes: %r", self.classifier.classes_)

        self.feature_scores = self.vectorizer.inverse_transform(self.classifier.coef_)[0]
        best_features = sorted(self.feature_scores.iteritems(), key=itemgetter(1), reverse=True)        
        logger.debug("Top SVM parameters: %r", best_features[:100])
        logger.debug("Top negative SVM parameters: %r", best_features[::-1][:100])

        logger.info("Finished training")
        
    def make_features(self, all_query_tokens, all_connections):
        return [self.get_query_expression_features(query_tokens, connection)
                for query_tokens, connection in zip(all_query_tokens, all_connections)]

    def get_best_expressions(self, query):
        query_features = self.get_sentence_features(query)
        logger.debug("Query features: %r", query_features)
        all_features = [self.get_query_expression_features(query_features, expression)
                        for expression in self.frequent_expressions]
        vectors = self.vectorizer.transform(all_features)
        predictions = self.classifier.decision_function(vectors)
        best_indices =  np.argsort(predictions)[::-1]
        best_expressions = [self.all_expressions[i] for i in best_indices]
        return best_expressions
        
        # random_expressions = list(self.all_expressions)
        # random.shuffle(random_expressions)
        # return random_expressions


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

    def get_query_expression_features(self, query, expression):
        try:
            connections = [expression.connection]
        except AttributeError:
            connections = [expression.expression1.connection,
                           expression.expression2.connection]
        return self.get_tensor_features(query, [repr(connection) for connection in connections])

    def get_tensor_features(self, source_tokens, target_tokens):
        features = []
        for source in source_tokens:
            for target in target_tokens:
                features.append(source + ':' + target)
        return {f: 1.0 for f in features}

    def get_sentence_features(self, sentence):
        tokens = tokenize(sentence)
        return [token for token in tokens if token not in STOPWORDS]

    def __repr__(self):
        return type(self).__name__
