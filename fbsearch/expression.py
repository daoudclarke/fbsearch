"""
Represents an expression to be computed on the database.
"""


class Expression(object):
    def __eq__(self, other):
        return repr(self) == repr(other)

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return repr(self).__hash__()

class ConnectionExpression(Expression):
    def __init__(self, connection):
        self.connection = connection


    def apply(self, entities, related):
        return set(related.apply_connection(
            entities, self.connection))

    def __repr__(self):
        return repr(self.connection)

class ConjunctionExpression(Expression):
    def __init__(self, expression1, expression2):
        self.expression1 = expression1
        self.expression2 = expression2

    def apply(self, entities, related):
        result1 = self.expression1.apply(entities, related)
        result2 = self.expression2.apply(entities, related)
        return result1 & result2

    def __repr__(self):
        return "%r & %r" % (self.expression1, self.expression2)
