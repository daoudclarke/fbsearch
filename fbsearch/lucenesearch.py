#!/usr/bin/env python

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

import sys
import re


STOPWORDS = set("""
  a an and are as at be but by for if in into is it
  no not of on or such that the their then there these
  they this to was will with who what where
""".split())

VALID_CHARS_PATTERN = re.compile('[\W_]+')

lucene.initVM(vmargs=['-Djava.awt.headless=true'])


class LuceneSearcher(object):
    fields = ['id', 'text', 'types']

    def __init__(self, db_path):
        directory = SimpleFSDirectory(File(db_path))
        reader = DirectoryReader.open(directory)
        self.searcher = IndexSearcher(reader)
        self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
        logger.info("Loaded DB from %s with %d documents: ",
                    db_path, reader.numDocs())

    def query_search(self, query):
        """
        Find entities that are contained as substrings in the query.
        """
        query_terms = [term for term in query.split() if term not in STOPWORDS]
        all_entities = []
        for i in range(len(query_terms) - 1):
            subquery = ' '.join(query_terms[i:i+2])
            docs = self.search(subquery)
            distances = [(Levenshtein.distance(doc['text'], unicode(subquery)), doc) for doc in docs]
            all_entities += distances
        return sorted(all_entities)
        
    def search(self, query):
        query = VALID_CHARS_PATTERN.sub(' ', query)
        logger.debug("Searching for %s", query)
        query = QueryParser(Version.LUCENE_CURRENT, "text",
                            self.analyzer).parse(query)
        score_docs = self.searcher.search(query, 100).scoreDocs
        logger.debug("%s total matching documents.",
                     len(score_docs))
        
        docs = [self.searcher.doc(d.doc) for d in score_docs]
        return [self.convert_to_dict(doc) for doc in docs]
        
    def convert_to_dict(self, doc):
        return {field: doc.get(field) for field in self.fields}
        

if __name__ == '__main__':
    print 'lucene', lucene.VERSION
    path = '/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/'
    searcher = LuceneSearcher(path)
    docs = searcher.query_search(sys.argv[1])
    for doc in docs:
        print doc

