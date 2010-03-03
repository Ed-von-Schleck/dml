from __future__ import print_function

import src.constants as constants
import src.events as events
from src.dmlexceptions import DMLError

START, HEAD, TITLE, TITLE_BODY, TITLE_BLOCK, CAST, CAST_BODY, CAST_BLOCK, ACT, BODY, BLOCK, ACTOR, DIALOG, TITLE_TAG, TITLE_VALUE, ACTOR_DEC, ACTOR_DES, INLINE_DIR, END = range(19)
names = "Start", "Head", "Title", "Title Body", "Title Block", "Cast", "Cast Body", "Cast Block", "Act", "Body", "Block", "Actor", "Dialog", "Title Tag", "Title Value", "Actor Declaration", "Actor Description", "Stage Dir.", "End"

def state_tracker():
    state = START
    # this is ugly, but the information has to go somewhere
    transitions = dict((
        ((START, events.CMD_LINE_OPTION), START),
        ((START, events.FUNCTION_DATA), START),
        ((START, events.TITLE_DEL), TITLE),
        ((START, events.CAST_DEL), CAST),
        ((START, events.ACT_DEL), ACT),
        ((START, events.DATA), HEAD),
        ((START, events.NEW_PARAGRAPH), HEAD),
        
        ((HEAD, events.DATA), HEAD),
        ((HEAD, events.NEW_PARAGRAPH), HEAD),
        ((HEAD, events.TITLE_DEL), TITLE),
        ((HEAD, events.CAST_DEL), CAST),
        ((HEAD, events.ACT_DEL), ACT),
        ((HEAD, events.FUNCTION_DATA), HEAD),
        
        ((TITLE, events.DATA), TITLE),
        ((TITLE, events.TITLE_DEL), TITLE_BODY),
        
        ((TITLE_BODY, events.NEW_PARAGRAPH), TITLE_BODY),
        ((TITLE_BODY, events.DATA), TITLE_BODY),
        ((TITLE_BODY, events.CAST_DEL), CAST),
        ((TITLE_BODY, events.ACT_DEL), ACT),
        ((TITLE_BODY, events.BLOCK_START), TITLE_BLOCK),
        ((TITLE_BODY, events.KEY_START), TITLE_TAG),
        
        ((TITLE_TAG, events.DATA), TITLE_TAG),
        ((TITLE_TAG, events.KEY_END), TITLE_VALUE),
        
        ((TITLE_VALUE, events.DATA), TITLE_VALUE),
        ((TITLE_VALUE, events.KEY_START), TITLE_TAG),
        ((TITLE_VALUE, events.NEW_PARAGRAPH), TITLE_BODY),
        
        ((TITLE_BLOCK, events.DATA), TITLE_BLOCK),
        ((TITLE_BLOCK, events.NEW_PARAGRAPH), TITLE_BODY),
        ((TITLE_BODY, events.FUNCTION_DATA), TITLE_BODY),
        
        ((CAST, events.DATA), CAST),
        ((CAST, events.CAST_DEL), CAST_BODY),
        ((CAST, events.FUNCTION_DATA), CAST),
        
        ((CAST_BODY, events.DATA), CAST_BODY),
        ((CAST_BODY, events.ACT_DEL), ACT),
        ((CAST_BODY, events.NEW_PARAGRAPH), CAST_BODY),
        ((CAST_BODY, events.BLOCK_START), CAST_BLOCK),
        ((CAST_BODY, events.KEY_START), ACTOR_DEC),
        
        ((CAST_BLOCK, events.DATA), CAST_BLOCK),
        ((CAST_BLOCK, events.NEW_PARAGRAPH), CAST_BODY),
        
        ((ACTOR_DEC, events.DATA), ACTOR_DEC),
        ((ACTOR_DEC, events.KEY_END), ACTOR_DES),
        
        ((ACTOR_DES, events.DATA), ACTOR_DES),
        ((ACTOR_DES, events.KEY_START), ACTOR_DEC),
        ((ACTOR_DES, events.NEW_PARAGRAPH), CAST_BODY),
        
        ((ACT, events.DATA), ACT),
        ((ACT, events.ACT_DEL), BODY),
        
        ((BODY, events.FUNCTION_DATA), BODY),
        ((BODY, events.ACT_DEL), ACT),
        ((BODY, events.NEW_PARAGRAPH), BODY),
        ((BODY, events.BLOCK_START), BLOCK),
        ((BODY, events.KEY_START), ACTOR),
        ((BODY, events.END), END),
        
        ((BODY, events.KEY_START), ACTOR),
        ((ACTOR, events.DATA), ACTOR),
        ((ACTOR, events.KEY_END), DIALOG),
        
        ((DIALOG, events.DATA), DIALOG),
        ((DIALOG, events.KEY_START), ACTOR),
        ((DIALOG, events.NEW_PARAGRAPH), BODY),
        ((DIALOG, events.INLINE_DIR_START), INLINE_DIR),
        ((DIALOG, events.END), END),
        
        ((BLOCK, events.DATA), BLOCK),
        ((BLOCK, events.NEW_PARAGRAPH), BODY),
        ((BLOCK, events.END), END),
        
        ((INLINE_DIR, events.DATA), INLINE_DIR),
        ((INLINE_DIR, events.INLINE_DIR_END), DIALOG),

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
        return "event '{0}' is not valid in state '{1}'".format(events.names[self.event], names[self.state])
