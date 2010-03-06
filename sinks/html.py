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
        while True:
            state, event, value = (yield)
            if event == events.DATA:
                write(value)
                break
            #TODO

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
