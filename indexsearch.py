#!/usr/bin/env python

INDEX_DIR = "IndexFiles.index"

import sys, os, lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = unicode(raw_input("Query:"))
        if command == '':
            return

        print
        print "Searching for:", repr(command)
        query = QueryParser(Version.LUCENE_CURRENT, "text",
                            analyzer).parse(command)
        scoreDocs = searcher.search(query, 100).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            print 'ID:', doc.get("id"), 'text:', doc.get('text'), 'types:', doc.get("types"), 'popularity', doc.get('popularity')


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    path = '/home/dc/Experiments/sempre/lib/lucene/4.4/inexact/'
    directory = SimpleFSDirectory(File(path))
    reader = DirectoryReader.open(directory)
    print "Number of documents: ", reader.numDocs()
    for i in range(10):
        doc = reader.document(i)
        print "Doc fields", doc.getFields()
        print "Text", doc.getValues('text')

    searcher = IndexSearcher(reader)
    analyzer = StandardAnalyzer(Version.LUCENE_CURRENT)
    run(searcher, analyzer)
    del searcher
