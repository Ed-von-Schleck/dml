# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from shutil import copyfileobj
from src.registry import sinks, Sink

def sink(metadata, file_obj):
    print(b"starting sink 'html' ...")
    try:
        with open(b"sinks/html/boilerplate") as boilerplate:
            copyfileobj(boilerplate, file_obj)
        write = file_obj.write
        
        title_infos = {}
        
        state, event, value = (yield)
        data = intern(b"data")
        start = intern(b"start")
        end = intern(b"end")
        
        # Start
        while True:
            if state != b"start":
                break
            state, event, value = (yield)
        
        # Header
        while state == b"head":
            if event == b"macro_data":
                # happily ignores "table of contents" or other requests
                pass
            state, event, value = (yield)
        
        # Title
        title = None
        while state in (b"title", b"title_body", b"title_block", b"title_value", b"title_tag"):           
            if state == b"title":
                if event is start:
                    title = []
                if event is data:
                    title.append(value)
                if event is end:
                    title_infos["Title"] = " ".join(title)
            if event == b"macro_data":
                # TODO
                continue
            state, event, value = (yield)
        else:
            if title is not None:
                write("<title>")
                write(title_infos["Title"])
                write("</title>\n<body>\n")
                write("<h1 id='DML_title'>")
                write(title_infos["Title"])
                write("</h1>")

        while state in (b"cast", b"cast_body", b"cast_block", b"actor_des", b"actor_dec"):
            state, event, value = (yield)
            # TODO

        # main
        start_switch = {
            b"block": b"<p class='DML_block'>",
            b"actor": b"<p class='DML_dialog_line'><span class='DML_actor'>",
            b"dialog": b"<span class='DML_dialog'>",
            b"inline_dir": b"<span class='DML_stage_direction'>",
            b"act": b"<h3 class='DML_act'>",
            b"scene": b"<h4 class='DML_scene'>"}
        end_switch = {
            b"block": b"</p>\n",
            b"actor": b"</span>",
            b"dialog": b"</span></p>\n",
            b"inline_dir": b"</span>",
            b"act": b"</h3>\n",
            b"scene": b"</h4>"}
        # if this doesn't make a convincing case for a switch statement in python
        # then I don't know one
        while state is not end:
            if event is start:
                try:
                    write(start_switch[state])
                except KeyError:
                    state, event, value = (yield)
                    continue

            elif event is end:
                try:
                    write(end_switch[state])
                except KeyError:
                    state, event, value = (yield)
                    continue
                    
            elif event is data:
                if value == "\n":
                    write(b"<br />")
                else:
                    write(b" ")
                    write(value.encode(b"utf-8"))
            state, event, value = (yield)
        
        write(b"\n</body>")
        while state is end:
            state, event, value = (yield)

    except GeneratorExit:
        pass
    finally:
        print("stopped sink 'html'")

sinks["html"] = Sink("html", "generates HTML output", sink)
