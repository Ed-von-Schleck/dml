# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import os.path
from shutil import copyfileobj

from src.constants import sink_events as events, states
NAME = "html"
EXTENSION = "html"
DESCRIPTION = "generates HTML output"
filters = ()

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        with open("sinks/html/boilerplate") as boilerplate:
            copyfileobj(boilerplate, file_obj)
        write = file_obj.write
        state, event, value = (yield)
        
        table_of_contents = False
        title_infos = {}
                
        # Start
        while True:
            if state != states.START:
                break
            state, event, value = (yield)
        
        # Header
        while state == states.HEAD:
            if event == events.MACRO_DATA:
                # TODO
                continue
            state, event, value = (yield)
        
        # Title
        while state in (states.TITLE, states.TITLE_BODY, states.TITLE_BLOCK,
                             states.TITLE_VALUE, states.TITLE_TAG):           
            if state == states.TITLE:
                if event == events.START:
                    title = []
                if event == events.DATA:
                    title.append(value)
                if event == events.END:
                    title_infos["Title"] = " ".join(title)
            if event == events.MACRO_DATA:
                # TODO
                continue
            state, event, value = (yield)
        
        write("<title>")
        write(title_infos["Title"])
        write("</title>\n<body>\n")
        write("<h1 id='DML_title'>")
        write(title_infos["Title"])
        write("</h1>")

        while state in (states.CAST, states.CAST_BODY, states.CAST_BLOCK,
                             states.ACTOR_DES, states.ACTOR_DEC):
            state, event, value = (yield)

        # main
        # if this doesn't make a convincing case for a switch statement in python
        # then I don't know one
        while state != states.END:
            if event == events.START:
                if state == states.BLOCK:
                    write("<p class='DML_block'>\n")
                elif state == states.ACTOR:
                    write("<p class='DML_dialog_line'><span class='DML_actor'>")
                elif state == states.DIALOG:
                    write("<span class='DML_dialog'>")
                elif state == states.INLINE_DIR:
                    write("<span class='DML_stage_direction'>")
                elif state == states.ACT:
                    write("<h3 class='DML_act'>")
                elif state == states.SCENE:
                    write("<h4 class='DML_scene'>")

            elif event == events.END:
                if state == states.BLOCK:
                    write("</p>\n")
                elif state == states.ACTOR:
                    write("</span>")
                elif state == states.DIALOG:
                    write("</span></p>\n")
                elif state == states.INLINE_DIR:
                    write("</span>")
                elif state == states.ACT:
                    write("</h3>\n")
                elif state == states.SCENE:
                    write("</h4>")
                    
            elif event == events.DATA:
                if value == "\n":
                    write("<br />")
                else:
                    write(" ")
                    write(value.encode("utf-8"))
            state, event, value = (yield)
        
        write("\n</body>")
        while state == states.END:
            state, event, value = (yield)

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
