# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import os.path
from shutil import copyfileobj

NAME = "html"
EXTENSION = "html"
DESCRIPTION = "generates HTML output"

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
            if state != "start":
                break
            state, event, value = (yield)
        
        # Header
        while state == "head":
            if event == "macro_data":
                # happily ignores "table of contents" or other requests
                pass
            state, event, value = (yield)
        
        # Title
        while state in ("title", "title_body", "title_block",
                             "title_value", "title_tag"):           
            if state == "title":
                if event == "start":
                    title = []
                if event == "data":
                    title.append(value)
                if event == "end":
                    title_infos["Title"] = " ".join(title)
            if event == "macro_data":
                # TODO
                continue
            state, event, value = (yield)
        
        write("<title>")
        write(title_infos["Title"])
        write("</title>\n<body>\n")
        write("<h1 id='DML_title'>")
        write(title_infos["Title"])
        write("</h1>")

        while state in ("cast", "cast_body", "cast_block",
                             "actor_des", "actor_dec"):
            state, event, value = (yield)

        # main
        # if this doesn't make a convincing case for a switch statement in python
        # then I don't know one
        while state != "end":
            if event == "start":
                if state == "block":
                    write("<p class='DML_block'>\n")
                elif state == "actor":
                    write("<p class='DML_dialog_line'><span class='DML_actor'>")
                elif state == "dialog":
                    write("<span class='DML_dialog'>")
                elif state == "inline_dir":
                    write("<span class='DML_stage_direction'>")
                elif state == "act":
                    write("<h3 class='DML_act'>")
                elif state == "scene":
                    write("<h4 class='DML_scene'>")

            elif event == "end":
                if state == "block":
                    write("</p>\n")
                elif state == "actor":
                    write("</span>")
                elif state == "dialog":
                    write("</span></p>\n")
                elif state == "inline_dir":
                    write("</span>")
                elif state == "act":
                    write("</h3>\n")
                elif state == "scene":
                    write("</h4>")
                    
            elif event == "data":
                if value == "\n":
                    write("<br />")
                else:
                    write(" ")
                    write(value.encode("utf-8"))
            state, event, value = (yield)
        
        write("\n</body>")
        while state == "end":
            state, event, value = (yield)

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
