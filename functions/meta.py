from __future__ import print_function
from src.dmlexceptions import DMLError
import src.constants as constants

def meta(broadcaster):
    key = ""
    values = []
    KEY, VALUES = 0, 1
    pointer = KEY
    try:
        while True:
            token = (yield)
            #print(token)
            if token == "\n" or token == ";":
                if not key and not values:
                    continue
                if bool(key) != bool(values):
                    raise DMLConfigSyntaxError("no key or value(s) defined")
                if key.lower() == "output":
                    for value in values:
                        broadcaster.send((constants.OUTPUT, value))
                pointer = KEY
                key = ""
                values = []

            elif token == "=" or token == ":":
                if key == "":
                    raise DMLConfigSyntaxError("no key defined")
                pointer = VALUES
                
            else:
                if pointer == KEY:
                    if key != "":
                        raise DMLConfigSyntaxError("a key is already defined")
                    key = token
                else:
                    values.append(token)
    except GeneratorExit:
        if not key and not values:
            return
        print(key, ":", values)

class DMLConfigSyntaxError(DMLError):
    """Exception raised if a syntax error in the config function in the dml file occurs

    Attributes:
        name -- undefined function
    """
