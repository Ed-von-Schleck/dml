from __future__ import print_function

import constants
import events
from dmlexceptions import DMLError

START, HEAD, TITLE, TITLE_BODY, CAST, CAST_BODY, ACT, BODY, FUNCTION_HEAD, FUNCTION_TITLE, FUNCTION_CAST, FUNCTION_BODY, END = range(13)
names = ["Start", "Head", "Title", "Title Body", "Cast", "Cast Body", "Act", "Body", "Head Function", "Title Function", "Cast Function", "Body Function", "End"]

def state_tracker():
    state = START
    # this is ugly, but the information has to go somewhere
    transitions = dict((
        ((START, events.FUNCTION_START), FUNCTION_HEAD),
        ((START, events.TITLE_START), TITLE),
        ((START, events.CAST_START), CAST),
        ((START, events.ACT_START), ACT),
        ((START, events.BODY), HEAD),
        ((HEAD, events.BODY), HEAD),
        ((HEAD, events.TITLE_START), TITLE),
        ((HEAD, events.CAST_START), CAST),
        ((HEAD, events.ACT_START), ACT),
        ((HEAD, events.FUNCTION_START), FUNCTION_HEAD),
        ((FUNCTION_HEAD, events.FUNCTION_DATA), FUNCTION_HEAD),
        ((FUNCTION_HEAD, events.FUNCTION_END), HEAD),
        ((TITLE, events.TITLE_DATA), TITLE),
        ((TITLE, events.TITLE_END), TITLE_BODY),
        ((TITLE_BODY, events.BODY), TITLE_BODY),
        ((TITLE_BODY, events.CAST_START), CAST),
        ((TITLE_BODY, events.ACT_START), ACT),
        ((TITLE_BODY, events.FUNCTION_START), FUNCTION_TITLE),
        ((FUNCTION_TITLE, events.FUNCTION_DATA), FUNCTION_TITLE),
        ((FUNCTION_TITLE, events.FUNCTION_END), TITLE_BODY),
        ((CAST, events.CAST_DATA), CAST),
        ((CAST, events.CAST_END), CAST_BODY),
        ((CAST, events.FUNCTION_START), FUNCTION_CAST),
        ((FUNCTION_CAST, events.FUNCTION_DATA), FUNCTION_CAST),
        ((FUNCTION_CAST, events.FUNCTION_END), CAST),
        ((CAST_BODY, events.BODY), CAST_BODY),
        ((CAST_BODY, events.ACT_START), ACT),
        ((ACT, events.ACT_DATA), ACT),
        ((ACT, events.ACT_END), BODY),
        ((BODY, events.FUNCTION_START), FUNCTION_BODY),
        ((BODY, events.CAST_START), CAST),
        ((BODY, events.ACT_START), ACT),
        ((BODY, events.BODY), BODY),
        ((BODY, events.TITLE_START), TITLE),
        ((FUNCTION_BODY, events.FUNCTION_DATA), FUNCTION_BODY),
        ((FUNCTION_BODY, events.FUNCTION_END), BODY),
        ((BODY, events.END), END),
        ((END, events.END), END))
    )
    while True:
        event = (yield state)
        try:
            state = transitions[(state, event)]
        except KeyError:
            raise DMLStateTransitionError(state, event)
        
class DMLStateTransitionError(DMLError):
    """Exception raised if an event was sent that doesn't match with a valid transition

    Attributes:
        state -- starting state
        event -- invalid event
    """
    def __init__(self, state, event):
        self.state = state
        self.event = event
    
    def __str__(self):
        return "event '{0}' is not valid in state '{1}'".format(names[self.state], events.names[self.event])
