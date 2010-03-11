# -*- coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function

class DMLError(Exception):
    """Base class for exceptions in dml."""
    pass

class DMLSyntaxError(DMLError):
    """Exception raised for errors in the DML syntax.

    Attributes:
        error_name -- pretty-print error name
        is_expr -- unexpected token
        should_be_expr  -- expected token
    """

    def __init__(self, is_expr, should_be_expr):
        self.error_name = "syntax error"
        self.is_expr = is_expr
        self.should_be_expr = should_be_expr
        
    def __str__(self):
        return "unexpected token '{0}', expected '{1}'".format(self.is_expr, self.should_be_expr)
                
class DMLMacroNameError(DMLError):
    """Exception raised if macro name is not defined

    Attributes:
        error_name -- pretty-print error name
        name -- undefined macro
    """

    def __init__(self, name):
        self.error_name = "macro name error"
        self.name = name
        
    def __str__(self):
        return "macro name '{0}' is not defined".format(self.name)
        
class DMLMacroSyntaxError(DMLError):
    """Exception raised if macro call is syntactically wrong

    Attributes:
        error_name -- pretty-print error name
    """

    def __init__(self):
        self.error_name = "macro syntax error"

    def __str__(self):
        return "syntax error in macro call"
        
class DMLStateTransitionError(DMLError):
    """Exception raised if an event was sent that doesn't match with a valid transition

    Attributes:
        error_name -- pretty-print error name
        state -- starting state
        event -- invalid event
    """
    def __init__(self, state, event):
        self.error_name = "state transition error"
        self.state = state
        self.event = event
    
    def __str__(self):
        return "event '{0}' is not valid in state '{1}'".format(self.event, self.state)
