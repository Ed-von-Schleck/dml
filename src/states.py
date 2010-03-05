# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

import src.constants as constants
from src.dmlparser import events
from src.dmlexceptions import DMLStateTransitionError

States = namedtuple("States", "START HEAD TITLE TITLE_BODY TITLE_BLOCK CAST CAST_BODY CAST_BLOCK ACT BODY BLOCK ACTOR DIALOG TITLE_TAG TITLE_VALUE ACTOR_DEC ACTOR_DES INLINE_DIR END")
states = States(*xrange(19))

def state_tracker():
    state = states.START
    # this is ugly, but the information has to go somewhere
    transitions = dict((
        ((states.START, events.CMD_LINE_OPTION), states.START),
        ((states.START, events.MACRO_DATA), states.HEAD),
        ((states.START, events.TITLE_DEL), states.TITLE),
        ((states.START, events.CAST_DEL), states.CAST),
        ((states.START, events.ACT_DEL), states.ACT),
        ((states.START, events.DATA), states.HEAD),
        ((states.START, events.NEW_PARAGRAPH), states.HEAD),
        
        ((states.HEAD, events.DATA), states.HEAD),
        ((states.HEAD, events.NEW_PARAGRAPH), states.HEAD),
        ((states.HEAD, events.TITLE_DEL), states.TITLE),
        ((states.HEAD, events.CAST_DEL), states.CAST),
        ((states.HEAD, events.ACT_DEL), states.ACT),
        ((states.HEAD, events.MACRO_DATA), states.HEAD),
        
        ((states.TITLE, events.DATA), states.TITLE),
        ((states.TITLE, events.TITLE_DEL), states.TITLE_BODY),
        
        ((states.TITLE_BODY, events.NEW_PARAGRAPH), states.TITLE_BODY),
        ((states.TITLE_BODY, events.DATA), states.TITLE_BODY),
        ((states.TITLE_BODY, events.CAST_DEL), states.CAST),
        ((states.TITLE_BODY, events.ACT_DEL), states.ACT),
        ((states.TITLE_BODY, events.BLOCK_START), states.TITLE_BLOCK),
        ((states.TITLE_BODY, events.KEY_START), states.TITLE_TAG),
        
        ((states.TITLE_TAG, events.DATA), states.TITLE_TAG),
        ((states.TITLE_TAG, events.KEY_END), states.TITLE_VALUE),
        
        ((states.TITLE_VALUE, events.DATA), states.TITLE_VALUE),
        ((states.TITLE_VALUE, events.KEY_START), states.TITLE_TAG),
        ((states.TITLE_VALUE, events.NEW_PARAGRAPH), states.TITLE_BODY),
        
        ((states.TITLE_BLOCK, events.DATA), states.TITLE_BLOCK),
        ((states.TITLE_BLOCK, events.NEW_PARAGRAPH), states.TITLE_BODY),
        ((states.TITLE_BODY, events.MACRO_DATA), states.TITLE_BODY),
        
        ((states.CAST, events.DATA), states.CAST),
        ((states.CAST, events.CAST_DEL), states.CAST_BODY),
        ((states.CAST, events.MACRO_DATA), states.CAST),
        
        ((states.CAST_BODY, events.DATA), states.CAST_BODY),
        ((states.CAST_BODY, events.ACT_DEL), states.ACT),
        ((states.CAST_BODY, events.NEW_PARAGRAPH), states.CAST_BODY),
        ((states.CAST_BODY, events.BLOCK_START), states.CAST_BLOCK),
        ((states.CAST_BODY, events.KEY_START), states.ACTOR_DEC),
        
        ((states.CAST_BLOCK, events.DATA), states.CAST_BLOCK),
        ((states.CAST_BLOCK, events.NEW_PARAGRAPH), states.CAST_BODY),
        
        ((states.ACTOR_DEC, events.DATA), states.ACTOR_DEC),
        ((states.ACTOR_DEC, events.KEY_END), states.ACTOR_DES),
        
        ((states.ACTOR_DES, events.DATA), states.ACTOR_DES),
        ((states.ACTOR_DES, events.KEY_START), states.ACTOR_DEC),
        ((states.ACTOR_DES, events.NEW_PARAGRAPH), states.CAST_BODY),
        
        ((states.ACT, events.DATA), states.ACT),
        ((states.ACT, events.ACT_DEL), states.BODY),
        
        ((states.BODY, events.MACRO_DATA), states.BODY),
        ((states.BODY, events.ACT_DEL), states.ACT),
        ((states.BODY, events.NEW_PARAGRAPH), states.BODY),
        ((states.BODY, events.BLOCK_START), states.BLOCK),
        ((states.BODY, events.KEY_START), states.ACTOR),
        ((states.BODY, events.END), states.END),
        
        ((states.BODY, events.KEY_START), states.ACTOR),
        ((states.ACTOR, events.DATA), states.ACTOR),
        ((states.ACTOR, events.KEY_END), states.DIALOG),
        
        ((states.DIALOG, events.DATA), states.DIALOG),
        ((states.DIALOG, events.KEY_START), states.ACTOR),
        ((states.DIALOG, events.NEW_PARAGRAPH), states.BODY),
        ((states.DIALOG, events.INLINE_DIR_START), states.INLINE_DIR),
        ((states.DIALOG, events.END), states.END),
        
        ((states.BLOCK, events.DATA), states.BLOCK),
        ((states.BLOCK, events.NEW_PARAGRAPH), states.BODY),
        ((states.BLOCK, events.END), states.END),
        
        ((states.INLINE_DIR, events.DATA), states.INLINE_DIR),
        ((states.INLINE_DIR, events.INLINE_DIR_END), states.DIALOG),

        ((states.END, events.END), states.END))
    )
    while True:
        event = (yield state)
        try:
            state = transitions[(state, event)]
        except KeyError:
            raise DMLStateTransitionError(states._fields[state], events._fields[event])
