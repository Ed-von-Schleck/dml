# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

from src.dmlexceptions import DMLStateTransitionError
from grammar import states

def state_tracker():
    state = "start"
    # this is ugly, but the information has to go somewhere
    transitions = dict((
        (("start", "cmd_line_option"), "start"),
        (("start", "macro_data"), "head"),
        (("start", "title_del"), "title"),
        (("start", "cast_del"), "cast"),
        (("start", "act_del"), "act"),
        (("start", "data"), "head"),
        (("start", "new_paragraph"), "head"),
        
        (("head", "data"), "head"),
        (("head", "new_paragraph"), "head"),
        (("head", "title_del"), "title"),
        (("head", "cast_del"), "cast"),
        (("head", "act_del"), "act"),
        (("head", "macro_data"), "head"),
        
        (("title", "data"), "title"),
        (("title", "title_del"), "title_body"),
        
        (("title_body", "new_paragraph"), "title_body"),
        (("title_body", "data"), "title_body"),
        (("title_body", "cast_del"), "cast"),
        (("title_body", "act_del"), "act"),
        (("title_body", "scene_del"), "scene"),
        (("title_body", "block_start"), "title_block"),
        (("title_body", "key_del"), "title_tag"),
        
        (("title_tag", "data"), "title_tag"),
        (("title_tag", "key_del"), "title_value"),
        
        (("title_value", "data"), "title_value"),
        (("title_value", "key_del"), "title_tag"),
        (("title_value", "new_paragraph"), "title_body"),
        
        (("title_block", "data"), "title_block"),
        (("title_block", "new_paragraph"), "title_body"),
        (("title_body", "macro_data"), "title_body"),
        
        (("cast", "data"), "cast"),
        (("cast", "cast_del"), "cast_body"),
        (("cast", "macro_data"), "cast"),
        
        (("cast_body", "data"), "cast_body"),
        (("cast_body", "act_del"), "act"),
        (("cast_body", "scene_del"), "scene"),
        (("cast_body", "new_paragraph"), "cast_body"),
        (("cast_body", "block_start"), "cast_block"),
        (("cast_body", "key_del"), "actor_dec"),
        
        (("cast_block", "data"), "cast_block"),
        (("cast_block", "new_paragraph"), "cast_body"),
        
        (("actor_dec", "data"), "actor_dec"),
        (("actor_dec", "key_del"), "actor_des"),
        
        (("actor_des", "data"), "actor_des"),
        (("actor_des", "key_del"), "actor_dec"),
        (("actor_des", "new_paragraph"), "cast_body"),
        
        (("act", "data"), "act"),
        (("act", "act_del"), "body"),
        
        (("scene", "data"), "scene"),
        (("scene", "scene_del"), "body"),
        
        (("body", "macro_data"), "body"),
        (("body", "act_del"), "act"),
        (("body", "scene_del"), "scene"),
        (("body", "new_paragraph"), "body"),
        (("body", "block_start"), "block"),
        (("body", "key_del"), "actor"),
        (("body", "end"), "end"),
        
        (("body", "key_del"), "actor"),
        (("actor", "data"), "actor"),
        (("actor", "key_del"), "dialog"),
        
        (("dialog", "data"), "dialog"),
        (("dialog", "key_del"), "actor"),
        (("dialog", "new_paragraph"), "body"),
        (("dialog", "inline_dir_del"), "inline_dir"),
        (("dialog", "end"), "end"),
        
        (("block", "data"), "block"),
        (("block", "new_paragraph"), "body"),
        (("block", "end"), "end"),
        
        (("inline_dir", "data"), "inline_dir"),
        (("inline_dir", "inline_dir_del"), "dialog"),

        (("end", "end"), "end"))
    )
    while True:
        event = (yield state)
        try:
            #state = transitions[(state, event)]
            state = states[state][1][event]
        except KeyError:
            raise DMLStateTransitionError(state, event)
