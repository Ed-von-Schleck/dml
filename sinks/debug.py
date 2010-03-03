"""
a debug sink
"""

from __future__ import print_function

import os.path

import src.constants as constants
import src.states as states
import src.events as events
from filters.stopnotrequested import filter as stop_if_not_requested

NAME = "debug"
SHORTNAME = "debug"
VERYSHORTNAME = "b"
DESCRIPTION = "generates debug output"
filters = ()

def sink(metadata):
    print("starting sink '{0}' ...".format(SHORTNAME))
    filename = os.path.join(metadata["working_dir"], metadata["name"] + "." + SHORTNAME)
    try:
        with open(filename, "w") as outfile:
            print("starting writing file '{0}' ...".format(filename))
            count = 0
            header = "{0: ^19}|{1: ^20}|{2: ^20}|{3: ^19}\n".format("state", "event", "key", "token")
            line = "-" * 79 + "\n"
            write = outfile.write
            while True:
                state, event, key, value = (yield)
                state_name = states.names[state]
                event_name = events.names[event]
                key_name = "-" if key == None else constants.names[key]
                value_name = "-" if value == None else value
                out = "{0:19}| {1:19}| {2:19}| {3:18}\n".format(state_name, event_name, key_name, value_name)
                if count == 0:
                    write("\n")
                    write(header)
                    write(line)
                count += 1
                count %= 40
                write(out)
        print("stopped writing file '{0}'".format(filename))

    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
