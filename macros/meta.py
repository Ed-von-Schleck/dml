# -*- coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

from src.dmlexceptions import DMLError
import src.constants as constants
from src.dmlparser import events

def macro(broadcaster, metadata, buffer, lexer):
    KEY, VALUES = 0, 1
    pointer = KEY
    key = ""
    values = []
    options = {
        "table_of_contents": (events.MACRO_DATA, constants.TOC),
        "paper_size": (events.MACRO_DATA, constants.PAPER_SIZE),
        }
    for token in buffer:
        if pointer == KEY:
            if token == "\n":
                pass
            elif token == ":" or token == "=":
                if not key:
                    raise DMLMetaSyntaxError("no key defined")
                pointer = VALUES
            elif key:
                raise DMLMetaSyntaxError("a key is already defined")
            else:
                key = token.lower()
        else:   # pointer to value
            if token == "\n" or token == ";":
                pointer = KEY
                key = ""
                values = []
            else:
                broadcaster.send((options[key][0], options[key][1], token))
                
class DMLMetaSyntaxError(DMLError):
    """Exception raised if a syntax error in a meta macro occurs

    Attributes:
        msg -- message
    """
    def __init__(self, msg):
        self.error_name = "meta macro Error"
        self.msg = msg
        
    def __str__(self):
        return self.msg

