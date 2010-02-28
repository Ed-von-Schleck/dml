from __future__ import print_function

import functions
from dmlexceptions import DMLSyntaxError, DMLFunctionNameError

def function(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

def dispatch(root, func_name):
    try:
        if func_name not in functions.functions:
            raise DMLFunctionNameError(func_name)
        open_brackets = (yield)
        if open_brackets != "{":
            raise DMLSyntaxError(open_brackets, "{")
        func = functions.functions[func_name](root)
        func.next()
        while True:
            token = (yield)
            if token == "}":
                break
            func.send(token)
        func.close()
    except GeneratorExit:
        pass
