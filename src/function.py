from __future__ import print_function

import functions
from dmlexceptions import DMLSyntaxError, DMLFunctionNameError
import constants
import events

def function(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

def dispatch(broadcaster, push):
    func_name = (yield)
    try:
        if func_name not in functions.functions:
            raise DMLFunctionNameError(func_name)
        open_brackets = (yield)
        if open_brackets != "{":
            raise DMLSyntaxError(open_brackets, "{")
        func = functions.functions[func_name](broadcaster, push)
        func.next()
        broadcaster.send((events.FUNCTION_START, constants.FUNCTION_NAME, func_name))
        while True:
            token = (yield)
            if token == "}":
                break
            func.send(token)
        broadcaster.send((events.FUNCTION_END, constants.FUNCTION_NAME, func_name))
    except GeneratorExit:
        pass
