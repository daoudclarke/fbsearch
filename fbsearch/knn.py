from fbsearch.oracle import OracleSystem
from fbsearch.connect import Connector

from operator import itemgetter
from collections import Counter, defaultdict
import random
import math

import numpy as np

from gensim.utils import simple_preprocess as tokenize
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.grid_search import GridSearchCV

from log import logger

STOPWORDS = {'what', 'is', 'the', 'of', 'to'}


def cosine(u, v):
    return np.dot(u,v)/math.sqrt(np.dot(u,u)*np.dot(v,v))

class NNSystem(object):
    k = 10
    
    def __init__(self, oracle_class=OracleSystem):
        self.random = random.Random(1)
        self.connector = Connector()
        self.possible_connections = None
        self.oracle_class = oracle_class
        self.expression_features = {}

    def train(self, train_set):
        logger.info("Performing pre-computation for KNN classifier")

        self.oracle = self.oracle_class(train_set)

        self.query_expressions = {}
        for query, target in train_set:
            _, expressions = self.oracle.get_best_results_and_expressions(query)
            if len(expressions) == 0:
                continue
            self.query_expressions[query] = expressions
        logger.info("Obtained %d items from oracle", len(self.query_expressions))

        # expression_counts = Counter()
        # for expressions in self.query_expressions.values():
        #     expression_counts.update(expressions)
        # logger.info("Found %d unique expressions", len(expression_counts))        

        features = []
        self.expressions = []
        self.queries = []
        self.expression_queries = defaultdict(list)
        for query, correct_expressions in self.query_expressions.iteritems():
            query_features = self.get_sentence_features(query)
            # correct_expression_counts = [(expression_counts[expression], expression)
            #                              for expression in correct_expressions]
            # sorted_counts = sorted(correct_expression_counts, reverse=True)
            # best_expression = sorted_counts[0][1]
            features.append(query_features)
            self.expressions.append(correct_expressions)
            self.queries.append(query)
            for expression in correct_expressions:
                self.expression_queries[expression].append(query)

        self.vectorizer = DictVectorizer()
        self.vectors = self.vectorizer.fit_transform(features)

        logger.debug("Expression queries: %r", self.expression_queries.items()[:5])
        logger.debug("Vectors: %r", self.vectors)
        logger.info("Finished precomputation")        


    def get_queries_for_expression(self, expression):
        return set(self.expression_queries[expression])

    def get_best_expressions(self, query):
        logger.info("Getting expressions for query: %r", query)
        query_features = self.get_sentence_features(query)
        logger.debug("Query features: %r", query_features)
        query_vector = self.vectorizer.transform([query_features])[0].toarray()[0]
        logger.debug("Query vector: %r", query_vector)
        cosines = []
        for i in range(len(self.expressions)):
            vector = self.vectors[i,:].toarray()[0]
            #logger.debug("Vector: %r", vector)
            c = cosine(query_vector, vector)
            cosines.append(c)
        best_indices = np.argsort(cosines)[::-1]
        logger.info("Best matching queries: %r",
                    [self.queries[i] for i in best_indices[:3]])
        matching_expression_sets = [self.expressions[i] for i in best_indices]
        expression_counts = Counter()
        discount = 1.0
        for expression_set in matching_expression_sets[:self.k]:
            set_counts = Counter(expression_set)
            expression_counts.update({k:discount*v for k, v in set_counts.items()})
            discount *= 0.95
        best_expressions = expression_counts.most_common()
        logger.info("Best expressions: %r", best_expressions[:10])
        return [expression for expression, _ in best_expressions]

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
