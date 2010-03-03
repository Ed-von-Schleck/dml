from __future__ import print_function

import functions
from dmlexceptions import DMLSyntaxError, DMLFunctionNameError
import constants
import events
from parsermanager import parser_manager

def dispatch(broadcaster, metadata, push, source):
    func_name = (yield)
    #print(func_name)
    try:
        if func_name not in functions.__all__:
            raise DMLFunctionNameError(func_name)
        open_brackets = (yield)
        if open_brackets != "{":
            raise DMLSyntaxError(open_brackets, "{")
        with parser_manager(functions.__dict__[func_name].function, broadcaster, metadata, push, source) as func:
            while True:
                token = (yield)
                if token == "}":
                    break
                func(token)
    except GeneratorExit:
        pass
