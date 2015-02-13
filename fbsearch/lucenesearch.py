#!/usr/bin/env python

from fbsearch import settings
from log import logger

import lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

import Levenshtein

import json
import sys
import re


STOPWORDS = set("""
  a an and are as at be but by for if in into is it
  no not of on or such that the their then there these
  they this to was will with who what where
""".split())

VALID_CHARS_PATTERN = re.compile('[\W_]+')

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

OP_VALUES = {
    'delete': 0.2,
    'insert': 1.0,
    'replace': 1.2,
    }

def edit_distance(entity, query):
    ops = Levenshtein.editops(query, entity)
    #logger.debug("Entity: %r, ops: %r", entity, ops)
    return sum(OP_VALUES[operation_type] for operation_type, _, _ in ops)

class LuceneSearcher(object):
    fields = ['id', 'text', 'types']

    def __init__(self, db_path):
        directory = SimpleFSDirectory(File(db_path))
        reader = DirectoryReader.open(directory)
        self.searcher = IndexSearcher(reader)
        self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        logger.info("Loaded DB from %s with %d documents: ",
                    db_path, reader.numDocs())
        try:
            with open(settings.QUERY_ENTITY_CACHE_PATH) as cache_file:
                self.query_entity_cache = json.load(cache_file)
        except IOError:
            self.query_entity_cache = {}

    def query_search(self, query):
        """
        Find entities that are contained as substrings in the query.
        """
        result = self.query_entity_cache.get(query)
        if result is not None:
            logger.debug("Found entities in query cache")
            return result
        logger.debug("Getting query entities")
        query_terms = [term for term in query.split() if term not in STOPWORDS]
        if len(query_terms) == 1:
            query_terms.append('')
        all_entities = []
        for i in range(len(query_terms) - 1):
            subquery = ' '.join(query_terms[i:i+2])
            logger.debug("Applying subquery %r", subquery)
            docs = self.search(subquery)
            distances = [(edit_distance(doc['text'], unicode(query)), doc) for doc in docs]
            all_entities += distances
        logger.debug("Found %d entities, caching", len(all_entities))
        result = sorted(all_entities)
        self.query_entity_cache[query] = result
        return result
        
    def search(self, query, max_matches=100):
        query = VALID_CHARS_PATTERN.sub(' ', query)
        logger.debug("Searching for %s", query)
        query = QueryParser(Version.LUCENE_CURRENT, "text",
                            self.analyzer).parse(query)
        score_docs = self.searcher.search(query, max_matches).scoreDocs
        logger.debug("%s total matching documents.",
                     len(score_docs))
        
        docs = [self.searcher.doc(d.doc) for d in score_docs]
        return [self.convert_to_dict(doc) for doc in docs]
        
    def convert_to_dict(self, doc):
        return {field: doc.get(field) for field in self.fields}

    def save_cache(self):
        with open(settings.QUERY_ENTITY_CACHE_PATH, 'w') as cache_file:
            json.dump(self.query_entity_cache, cache_file, indent=4)

if __name__ == '__main__':
    print 'lucene', lucene.VERSION
    path = settings.LUCENE_PATH
    searcher = LuceneSearcher(path)
    docs = searcher.search(sys.argv[1], 400)
    for doc in docs:
        print doc

