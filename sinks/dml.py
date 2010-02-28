"""
a dml sink

Yes, this doesn't make much sense for an end user, but it's great for testing
and debugging. It ignores all kind of meta, giving just plain drama.
"""

from __future__ import print_function

import src.constants as constants
import src.states as states

def dml():
    state = states.START
    while True:
        event, key, value = (yield)
