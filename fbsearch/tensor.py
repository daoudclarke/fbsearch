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
        self.expression_features = {}

    def set_best_expression_set(self, train_set):
        expression_counts = Counter()
        for expressions in self.query_expressions.values():
            expression_counts.update(expressions)
        logger.info("Found %d unique expressions", len(expression_counts))
        self.frequent_expressions = set()
        covered = 0
        uncovered_set = train_set
        while len(uncovered_set) > 0:
            frequent = expression_counts.most_common(1)[0][0]
            self.frequent_expressions.add(frequent)
            logger.info("Most frequent expression: %r", frequent)

            covered = 0
            removed = Counter()
            new_uncovered_set = []
            new_expression_counts = Counter()
            for query, target in uncovered_set:
                _, oracle_expressions = self.oracle.get_best_results_and_expressions(query)
                oracle_expressions = set(oracle_expressions)
                if frequent not in oracle_expressions and len(oracle_expressions) > 0:
                    new_uncovered_set.append((query, target))
                    new_expression_counts.update(oracle_expressions)
            uncovered_set = new_uncovered_set
            expression_counts = new_expression_counts
            logger.info("Frequent expressions: %d, uncovered: %d, expressions_remaining: %d",
                        len(self.frequent_expressions),
                        len(uncovered_set),
                        len(expression_counts))
        

    def train(self, train_set):
        logger.info("Training tensor based classifier")
        
        self.oracle = self.oracle_class(train_set)
        self.query_expressions = {}
        for query, target in train_set:
            _, expressions = self.oracle.get_best_results_and_expressions(query)
            if len(expressions) == 0:
                continue
            self.query_expressions[query] = expressions
        logger.info("Obtained %d items from oracle", len(self.query_expressions))

        features = []
        values = []

        self.set_best_expression_set(train_set)

        all_features = []
        values = []
        for query, correct_expressions in self.query_expressions.iteritems():
            logger.debug("Building features for query %r, %d correct expressions",
                         query, len(correct_expressions))
            query_tokens = self.get_sentence_features(query)

            for expression in correct_expressions & self.frequent_expressions:
                features = self.get_query_expression_features(query_tokens, expression)
                all_features.append(features)
                values.append(1)

            for expression in self.frequent_expressions - correct_expressions:
                features = self.get_query_expression_features(query_tokens, expression)
                all_features.append(features)
                values.append(0)

        self.frequent_expressions = list(self.frequent_expressions)

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
        best_expressions = [self.frequent_expressions[i] for i in best_indices]
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

    def get_expression_features(self, expression):
        if expression in self.expression_features:
            return self.expression_features[expression]
        try:
            connections = [expression.connection]
        except AttributeError:
            connections = [expression.expression1.connection,
                           expression.expression2.connection]
        relations = reduce(list.__add__, [list(c) for c in connections])
        connection_names= [self.connector.related.get_names(relation) for relation in relations]
        logger.info("Connections: %r, Connection names: %s", connections, connection_names)
        pseudo_sentence = ' '.join(connection_names)
        features = self.get_sentence_features(pseudo_sentence)
        logger.debug("Connection features: %r", features)
        self.expression_features[expression] = features
        return features

    def get_query_expression_features(self, query, expression):
        expression_features = self.get_expression_features(expression)
        return self.get_tensor_features(query, expression_features)

    def get_tensor_features(self, source_tokens, target_tokens):
        features = []
        for source in source_tokens:
            for target in target_tokens:
                features.append(source + ':' + target)
        return {f: 1.0 for f in features}

    def get_sentence_features(self, sentence):
        tokens = set(tokenize(sentence))
        return [token for token in tokens if token not in STOPWORDS]

    def __repr__(self):
        return type(self).__name__
