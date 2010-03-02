from __future__ import print_function

import os.path

import src.constants as constants
import src.states as states
import src.events as events
from filters.stopnotrequested import filter as stop_if_not_requested

NAME = "Hypertext Markup Language"
SHORTNAME = "html"
VERYSHORTNAME = "t"
DESCRIPTION = "generates HTML output"
filters = (stop_if_not_requested,)

def sink(path, filename):
    print("starting sink '{0}' ...".format(SHORTNAME))
    filename = os.path.join(path, filename + "." + SHORTNAME)
    paragraph_open = 0
    try:
        with open(filename, "w") as file:
            write = file.write
            print("starting writing file '{0}' ...".format(filename))
            last_state = -1
            while True:
                state, event, key, value = (yield)
                
                if event == events.DATA:
                    if key == constants.TOKEN:
                        write("".join((value, " ")))
                    elif key == constants.FORCE_NEWLINE:
                        write("<br />")
                
                #elif event == events.FUNCTION_START:
                #    file.write("".join(("@", value, " {\n")))
                #elif event == events.FUNCTION_END:
                #    file.write("}")
                #elif event == events.FUNCTION_DATA:
                #    file.write("".join((constants.names[key], ": ", value, "\n")))
                    
                elif event == events.TITLE_DEL:
                    if state == states.TITLE:
                        write("\n<h1> ")
                    else:
                        write("</h1>")
                    
                elif event == events.CAST_DEL:
                    if state == states.CAST:
                        write("\n<h2> ")
                    else:
                        write("</h2>")
                    
                elif event == events.ACT_DEL:
                    if state == states.ACT:
                        write("\n<h3> ")
                    else:
                        write("</h3>")

                elif event == events.NEW_PARAGRAPH:
                    if not state == states.HEAD and paragraph_open > 0:
                        write("</p>\n")
                        paragraph_open -= 1
                    
                elif event == events.BLOCK_START:
                    write("<p>")
                    paragraph_open += 1

                elif event == events.INLINE_DIR_START:
                    write("<i> ")
                elif event == events.INLINE_DIR_END:
                    write("</i> ")
                    
                elif event == events.KEY_START:
                    if paragraph_open > 0:
                        file.write("</p>\n")
                        paragraph_open -= 1
                    write("<p> <b> ")
                    paragraph_open += 1
                elif event == events.KEY_END:
                    write("</b> ")
                last_state = state
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
