class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class DMLSyntaxError(Error):
    """Exception raised for errors in the DML syntax.

    Attributes:
        is_expr -- unexpected token
        should_be_expr  -- expected token
    """

    def __init__(self, is_expr, should_be_expr):
        self.is_expr = is_expr
        self.should_be_expr = should_be_expr
        
    def __str__(self):
        return "unexpected token '{0}', expected '{1}'".format(self.is_expr, self.should_be_expr)
                
