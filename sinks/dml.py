"""
a dml sink

Yes, this doesn't make much sense for an end user, but it's great for testing
and debugging. 
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
filters = (stop_if_not_requested,)

def sink(path, filename):
    print("starting sink '{0}' ...".format(SHORTNAME))
    filename = os.path.join(path, filename + "." + SHORTNAME)
    last_token_key = None
    try:
        with open(filename, "w") as file:
            print("starting writing file '{0}' ...".format(filename))
            while True:
                state, event, key, value = (yield)
                
                if event == events.DATA:
                    if key == constants.TOKEN:
                        file.write("".join((value, " ")))
                    elif key == constants.FORCE_NEWLINE:
                        file.write("\n")
                        
                
                elif event == events.FUNCTION_START:
                    file.write("".join(("@", value, " {\n")))
                elif event == events.FUNCTION_END:
                    file.write("}")
                elif event == events.FUNCTION_DATA:
                    file.write("".join((constants.names[key], ": ", value, "\n")))
                    
                elif event == events.TITLE_START:
                    file.write("\n= ")
                elif event == events.TITLE_END:
                    file.write("=")
                    
                elif event == events.CAST_START:
                    file.write("\n== ")
                elif event == events.CAST_END:
                    file.write("==")
                    
                elif event == events.ACT_START:
                    file.write("\n=== ")

                elif event == events.ACT_END:
                    file.write("===")

                elif event == events.NEW_PARAGRAPH:
                    file.write("\n")
                    
                elif event == events.BLOCK_START:
                    file.write("\n")

                elif event == events.INLINE_DIR_START:
                    file.write("< ")
                elif event == events.INLINE_DIR_END:
                    file.write("> ")
                    
                elif event == events.KEY_START:
                    file.write("\n\t")
                elif event == events.KEY_END:
                    file.write(": ")
                    
                last_token_key = key
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
                    
