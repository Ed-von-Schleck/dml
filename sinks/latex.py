# -*- coding: utf-8
"""
a latex sink

"""

from __future__ import print_function

import os.path

import src.constants as constants
import src.states as states
import src.events as events

NAME = "latex"
EXTENSION = "tex"
DESCRIPTION = "generates latex output"
filters = ()

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        write = file_obj.write
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
                
            elif event == events.END:
                break
                
    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
                    
