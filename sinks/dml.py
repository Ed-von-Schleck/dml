"""
a dml sink

Yes, this doesn't make much sense for an end user, but it's great for testing
and debugging. It ignores all kind of meta, giving just plain drama.
"""

from __future__ import print_function

import src.constants as constants
import src.states as states
from src.sinktools import stop_if_not_requested

NAME = "drama markup language"
SHORTNAME = "dml"
VERYSHORTNAME = "d"
DESCRIPTION = "generates DML output"

def sink():
    listening_for_output_request = True
    try:
        while True:
            state, event, key, value = (yield)
            #print(state, event, key, value)
            if listening_for_output_request:
                if state == states.FUNCTION_HEAD:
                    if key == constants.OUTPUT and value == SHORTNAME:
                        listening_for_output_request = False
                elif state != states.START or state != states.HEAD:
                    break
    except GeneratorExit:
        pass
                    
