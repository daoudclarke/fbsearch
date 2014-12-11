from rdflib.store import Store
from rdflib.plugin import get as plugin
from rdflib import URIRef
#from rdflib.namespace import RDF
from rdflib.term import Literal
from rdflib.plugins.stores.regexmatching import REGEXTerm

import sys
import logging
#import virtuoso

logger = logging.getLogger('virtuoso.vstore')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


Virtuoso = plugin("Virtuoso", Store)
store = Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y;Host=localhost:13093")

fb_type = URIRef('http://rdf.freebase.com/ns/type.object.type')

vivaldi = Literal('Vivaldi')
capital = Literal('is_capital_of')

vivaldi = REGEXTerm('.*Vivaldi.*')

results = store.query("""
prefix : <http://rdf.freebase.com/ns/>
SELECT *
WHERE
{
    ?s :type.object.name ?o .
    ?o bif:contains "'world war'"
    OPTION (score ?sc) .
    FILTER regex(str(?o), "^USA ")
}
ORDER BY DESC (?sc)
""")

# results = store.query("""
# prefix : <http://rdf.freebase.com/ns/>
# select ?x {
#    ?x :type.object.name 'King Henry'@en .
# }
# """)

# results = store.query("""
# prefix : <http://rdf.freebase.com/ns/>
# select ?z1, ?z2, ?z3, ?a, ?b {
#    ?x :type.object.name 'Bach'@en .
#    ?x ?z1 ?a .
#    ?a ?z2 ?b .
#    ?b ?z3 ?y .
#    ?y :type.object.name 'Vivaldi'@en .
# }
# """)

# # results = store.query("""
# # prefix : <http://rdf.freebase.com/ns/>

# # select ?river ?length {
# #    ?river :geography.river.length ?length .
# #    ?river :location.location.containedby :m.06bnz .
# # } ORDER BY DESC(?length) LIMIT 1
# # """)

# # results = store.query("""
# # SELECT ?x ?y ?z
# #        WHERE {
# #           ?x ?y ?z .
# #        }
# # """)

for row in results:
    print row

# name = URIRef('http://rdf.freebase.com/ns/type.object.name')

# # vivaldi = Literal(u'Bach')

# film = Literal(u'bach', lang='en')

# for triple in store.triples((None, None, film)):
#     print triple

# for triple in store.triples(('?x', '?y', '?z')):
#     print triple
