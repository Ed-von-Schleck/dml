# -*- coding: utf-8
"""
a sink for debugging

This sink prints all states, the event that lead to them, and the keys and tokens
that come with them neatly in a table.
"""

from __future__ import print_function
from __future__ import unicode_literals

import os.path

import src.constants as constants
import src.states as states
import src.events as events

NAME = "debug"
EXTENSION = "dbg"
DESCRIPTION = "generates debug output"
filters = ()

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        count = 0
        header = "\n{0: ^19}|{1: ^20}|{2: ^20}|{3: ^19}\n".format("state", "event", "key", "token")
        header += "-" * 79 + "\n"
        write = file_obj.write
        while True:
            state, event, key, value = (yield)
            state_name = states.names[state]
            event_name = events.names[event]
            key_name = "-" if key is None else constants.names[key]
            value_name = "-" if value is None else "'" + value + "'"
            out = "{0:19}| {1:19}| {2:19}| {3:18}\n".format(state_name, event_name, key_name, value_name)
            if count == 40:
                write(header)
                count = 0
            count += 1
            write(out)
    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
