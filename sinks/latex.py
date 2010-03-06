# -*- coding: utf-8
"""
a latex sink

"""

from __future__ import print_function
from __future__ import unicode_literals

import os.path

from src.constants import sink_events as events, states

NAME = "latex"
EXTENSION = "tex"
DESCRIPTION = "generates latex output"
filters = ()

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        write = file_obj.write
        while True:
            state, event, value = (yield)
    
    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
                    
