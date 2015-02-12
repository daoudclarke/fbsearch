from fbsearch.oracle import OracleSystem
from fbsearch.connect import Connector

from operator import itemgetter
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
        logger.info("Converting features to list")
        features = []
        values = []

        oracle = self.oracle_class(train_set)
        all_query_tokens = []
        all_connections = []
        for query, target in train_set:
            _, connection = oracle.get_best_results_and_connection(query)
            if connection is None:
                continue

            all_connections.append(connection)
            query_tokens = self.get_sentence_features(query)
            all_query_tokens.append(query_tokens)
            logger.debug("Query tokens: %r, connection: %r", query_tokens, connection)

        self.possible_connections = list(set(all_connections))

        # Positive features
        features = self.make_features(all_query_tokens, all_connections)
        
        # Negative features
        duplicates = 1
        for i in range(duplicates):
            random.shuffle(all_connections)
            features += self.make_features(all_query_tokens, all_connections)

        values = [1]*len(all_query_tokens) + [0]*(len(all_query_tokens)*duplicates)

        logger.info("Training - building vectors with %d features", len(features))
        self.vectorizer = DictVectorizer()
        vectors = self.vectorizer.fit_transform(features)


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
        return [self.get_query_connection_features(query_tokens, connection)
                for query_tokens, connection in zip(all_query_tokens, all_connections)]

    def execute(self, query):
        logger.debug("Executing query: %r", query)
        query_features = self.get_sentence_features(query)
        logger.debug("Query features: %r", query_features)
        all_features = [self.get_query_connection_features(query_features, connection)
                        for connection in self.possible_connections]
        vectors = self.vectorizer.transform(all_features)
        predictions = self.classifier.decision_function(vectors)
        best_indices =  np.argsort(predictions)[::-1]

        for i in best_indices:
            connection = self.possible_connections[i]
            logger.debug("Score: %f for connection %r", predictions[i], connection)
            result = self.connector.apply_connection(
                query, connection)
            logger.debug("Searching for best connection, index: %d, connection: %r, result: %r",
                         i, connection, result)
            if len(result) > 0:
                return result
        return set()

    def get_query_connection_features(self, query, connection):
        return self.get_tensor_features(query, [':'.join(connection)])

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
