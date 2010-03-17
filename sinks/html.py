# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

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
        
        table_of_contents = False
        title_infos = {}
        
        state, event, value = (yield)
                
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
        title = None
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
        
        if title is not None:
            write("<title>")
            write(title_infos["Title"])
            write("</title>\n<body>\n")
            write("<h1 id='DML_title'>")
            write(title_infos["Title"])
            write("</h1>")

        while state in ("cast", "cast_body", "cast_block",
                             "actor_des", "actor_dec"):
            state, event, value = (yield)
            # TODO

        # main
        start_switch = {
            "block": "<p class='DML_block'>",
            "actor": "<p class='DML_dialog_line'><span class='DML_actor'>",
            "dialog": "<span class='DML_dialog'>",
            "inline_dir": "<span class='DML_stage_direction'>",
            "act": "<h3 class='DML_act'>",
            "scene": "<h4 class='DML_scene'>"}
        end_switch = {
            "block": "</p>\n",
            "actor": "</span>",
            "dialog": "</span></p>\n",
            "inline_dir": "</span>",
            "act": "</h3>\n",
            "scene": "</h4>"}
        # if this doesn't make a convincing case for a switch statement in python
        # then I don't know one
        while state != "end":
            if event == "start":
                try:
                    write(start_switch[state])
                except KeyError:
                    state, event, value = (yield)
                    continue

            elif event == "end":
                try:
                    write(end_switch[state])
                except KeyError:
                    state, event, value = (yield)
                    continue
                    
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
