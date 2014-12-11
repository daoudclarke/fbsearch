#!/usr/bin/env python

from log import logger

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

import sys, lucene

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
        
    def search(self, query):
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
    docs = searcher.search(sys.argv[1])
    for doc in docs:
        print doc

