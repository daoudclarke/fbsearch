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

    def get_connections(self):
        """
        Return the set of connections used by the expression.
        """
        return set([self.connection])

    def __repr__(self):
        return repr(self.connection)

class SetExpression(Expression):
    """
    An expression together with an associated set of entities.
    """
    def __init__(self, connection, entities):
        self.connection = connection
        self.entities = entities

    def apply(self, entities, related):
        return entities & self.entities

    def get_connections(self):
        return set([self.connection])

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


    def get_connections(self):
        return self.expression1.get_connections() | self.expression2.get_connections()

    def __repr__(self):
        return "%r & %r" % (self.expression1, self.expression2)
