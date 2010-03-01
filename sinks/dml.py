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
    try:
        with open(filename, "w") as file:
            print("starting writing file '{0}' ...".format(filename))
            while True:
                state, event, key, value = (yield)
                if event == events.FUNCTION_START:
                    file.write("".join(("@", value, " {\n")))
                elif event == events.FUNCTION_END:
                    file.write("}\n")
                elif event == events.FUNCTION_DATA:
                    file.write("".join((constants.names[key], ": ", value, "\n")))
                    
                elif event == events.TITLE_START:
                    file.write("= ")
                elif event == events.TITLE_DATA:
                    file.write("".join((value, " ")))
                elif event == events.TITLE_END:
                    file.write("=\n")
                    
                elif event == events.CAST_START:
                    file.write("== ")
                elif event == events.CAST_DATA:
                    file.write("".join((value, " ")))
                elif event == events.CAST_END:
                    file.write("==\n")
                    
                elif event == events.ACT_START:
                    file.write("=== ")
                elif event == events.ACT_DATA:
                    file.write("".join((value, " ")))
                elif event == events.ACT_END:
                    file.write("===\n")

                elif event == events.BODY:
                    file.write("".join((value, " ")))
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
                    
