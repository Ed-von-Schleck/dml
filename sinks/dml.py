"""
a dml sink

Yes, this doesn't make much sense for an end user, but it's great for testing
and debugging. It ignores all kind of meta, giving just plain drama.
"""

from __future__ import print_function

import src.constants as constants
import src.states as states
from filters.stopnotrequested import filter as stop_if_not_requested

NAME = "drama markup language"
SHORTNAME = "dml"
VERYSHORTNAME = "d"
DESCRIPTION = "generates DML output"
filters = (stop_if_not_requested,)

def sink():
    print("starting sink '{0}' ...".format(SHORTNAME))
    try:
        while True:
            state, event, key, value = (yield)
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
                    
