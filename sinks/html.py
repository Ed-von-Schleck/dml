# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import os.path
from shutil import copyfileobj

import src.constants as constants
import src.states as states
import src.events as events

NAME = "html"
EXTENSION = "html"
DESCRIPTION = "generates HTML output"
filters = ()

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        with open("sinks/html/boilerplate") as boilerplate:
            copyfileobj(boilerplate, file_obj)
        paragraphs_open = 0
        dialogs_open = 0
        write = file_obj.write
        last_state = -1
        state_key_names = {states.TITLE_TAG: "DML_title_tag",
                states.ACTOR_DEC: "DML_actor_declaration",
                states.ACTOR: "DML_actor"}
        state_value_names = {states.TITLE_VALUE: "DML_title_value",
                states.ACTOR_DES: "DML_actor_description",
                states.DIALOG: "DML_dialog"}
        state_line_names = {states.TITLE_TAG: "DML_title_value_line",
                states.ACTOR_DEC: "DML_actor_description_line",
                states.ACTOR: "DML_dialog_line"}
        state_block_names = {states.TITLE_BLOCK: "DML_title_block",
                states.CAST_BLOCK: "DML_cast_block",
                states.BLOCK: "DML_block"}
        while True:
            state, event, key, value = (yield)
            
            if event == events.DATA:
                if key == constants.TOKEN:
                    write("".join((value, " ")))
                elif key == constants.FORCE_NEWLINE:
                    write("<br />")
            
            #elif event == events.MACRO_START:
            #    file.write("".join(("@", value, " {\n")))
            #elif event == events.MACRO_END:
            #    file.write("}")
            #elif event == events.MACRO_DATA:
            #    file.write("".join((constants.names[key], ": ", value, "\n")))
                
            elif event == events.TITLE_DEL:
                if state == states.TITLE:
                    write("\n<h1 id='DML_title'> ")
                else:
                    write("</h1>\n")
                
            elif event == events.CAST_DEL:
                if state == states.CAST:
                    write("\n<h2 id='DML_cast'> ")
                else:
                    write("</h2>\n")
                
            elif event == events.ACT_DEL:
                if state == states.ACT:
                    write("\n<h3 class='DML_act'> ")
                else:
                    write("</h3>\n")

            elif event == events.NEW_PARAGRAPH:
                if dialogs_open > 0:
                    write("</span>")
                    dialogs_open -= 1
                if paragraphs_open > 0:
                    write("</p>\n")
                    paragraphs_open -= 1
                
            elif event == events.BLOCK_START:
                write("<p class='" + state_block_names[state] + "'>")
                paragraphs_open += 1

            elif event == events.INLINE_DIR_START:
                write("<span class='DML_stage_direction'> ")
            elif event == events.INLINE_DIR_END:
                write("</span> ")
                
            elif event == events.KEY_START:
                if dialogs_open > 0:
                    write("</span>")
                    dialogs_open -= 1
                if paragraphs_open > 0:
                    write("</p>\n")
                    paragraphs_open -= 1
                write("<p class='" + state_line_names[state] + "'><span class='" + state_key_names[state] + "'> ")
                paragraphs_open += 1
            elif event == events.KEY_END:
                write("</span> <span class='" + state_value_names[state] + "'>")
                dialogs_open += 1
            elif event == events.END:
                if dialogs_open > 0:
                    write("</span>")
                if paragraphs_open > 0:
                    write("</p>\n")
                write("</body>\n</html>")
                break
    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
