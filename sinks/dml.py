"""
a dml sink

Yes, this doesn't make much sense for an end user, but it's great for testing
and debugging. No Functions though (wouldn't make much sense if you think about
it.
"""

from __future__ import print_function

import os.path

import src.constants as constants
import src.states as states
import src.events as events
from filters.stopnotrequested import filter as stop_if_not_requested

NAME = "drama markup language"
SHORTNAME = "dml"
VERYSHORTNAME = "d"
DESCRIPTION = "generates DML output"
filters = ()

def sink(metadata):
    print("starting sink '{0}' ...".format(SHORTNAME))
    filename = os.path.join(metadata["working_dir"], metadata["name"] + "." + SHORTNAME)
    try:
        with open(filename, "w") as file:
            write = file.write
            print("starting writing file '{0}' ...".format(filename))
            while True:
                state, event, key, value = (yield)
                
                if event == events.DATA:
                    if key == constants.TOKEN:
                        write("".join((value, " ")))
                    elif key == constants.FORCE_NEWLINE:
                        write("\\\\\n")
                    
                elif event == events.TITLE_DEL:
                    if state == states.TITLE:
                        write("\n= ")
                    else:
                        write("=")
                    
                elif event == events.CAST_DEL:
                    if state == states.CAST:
                        write("\n== ")
                    else:
                        write("==")
                    
                elif event == events.ACT_DEL:
                    if state == states.ACT:
                        write("\n=== ")
                    else:
                        write("===")

                elif event == events.NEW_PARAGRAPH:
                    write("\n")
                    
                elif event == events.BLOCK_START:
                    write("\n")

                elif event == events.INLINE_DIR_START:
                    write("< ")
                elif event == events.INLINE_DIR_END:
                    write("> ")
                    
                elif event == events.KEY_START:
                    write("\n\t")
                elif event == events.KEY_END:
                    write(": ")
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
                    
