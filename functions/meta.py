from __future__ import print_function
from src.dmlexceptions import DMLError
import src.constants as constants
import src.events as events

def function(broadcaster, metadata, push, source):
    key = ""
    values = []
    KEY, VALUES = 0, 1
    pointer = KEY
    switch = {
        "table_of_contents": (events.FUNCTION_DATA, constants.TOC),
        "paper_size": (events.FUNCTION_DATA, constants.PAPER_SIZE),
        }
    try:
        while True:
            token = (yield)
            if token == "\n" or token == ";":
                if not key and not values:
                    continue
                if bool(key) != bool(values):
                    raise DMLMetaSyntaxError("no key or value(s) defined")
                for value in values:
                    broadcaster.send((switch[key][0], switch[key][1], value))
                pointer = KEY
                key = ""
                values = []

            elif token == "=" or token == ":":
                if key == "":
                    raise DMLMetaSyntaxError("no key defined")
                pointer = VALUES
                
            else:
                if pointer == KEY:
                    if key != "":
                        raise DMLMetaSyntaxError("a key is already defined")
                    key = token.lower()
                else:
                    values.append(token.lower())
    except GeneratorExit:
        if not key and not values:
            return
        if bool(key) != bool(values):
            raise DMLMetaSyntaxError("no key or value(s) defined")
        for value in values:
            broadcaster.send((switch[key][0], switch[key][1], value))


class DMLMetaSyntaxError(DMLError):
    """Exception raised if a syntax error in a meta function occurs

    Attributes:
        msg -- message
    """
