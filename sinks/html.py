from __future__ import print_function

import src.constants as constants
from filters.stopnotrequested import filter as stop_if_not_requested

NAME = "Hypertext Markup Language"
SHORTNAME = "html"
VERYSHORTNAME = "t"
DESCRIPTION = "generates HTML output"
filters = (stop_if_not_requested,)

def sink(path, filename):
    print("starting sink '{0}' ...".format(SHORTNAME))
    try:
        while True:
            state, event, key, value = (yield)
    except GeneratorExit:
        print("stopped sink '{0}'".format(SHORTNAME))
