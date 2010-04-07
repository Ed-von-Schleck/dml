# -*- coding: utf-8
"""
a sink for debugging

This sink prints all states, the event that lead to them, and the keys and tokens
that come with them neatly in a table.
"""

from __future__ import print_function
from __future__ import unicode_literals

import os.path

NAME = "debug"
EXTENSION = "dbg"
DESCRIPTION = "generates debug output"

def sink(metadata, file_obj):
    print("starting sink '{0}' ...".format(NAME))
    try:
        count = 0
        header = b"\n{0: ^19}|{1: ^20}|{2: ^19}\n".format("state", "event", "token")
        header += "-" * 79 + "\n"
        write = file_obj.write
        write(header)
        while True:
            state, event, value = (yield)
            value_name = "" if value is None else value
            out = b"{0:19}| {1:19}| {2:18}\n".format(state, event, value_name.encode("utf-8"))
            if count == 40:
                write(header)
                count = 0
            count += 1
            write(out)

    except GeneratorExit:
        pass
    finally:
        print("stopped sink '{0}'".format(NAME))
