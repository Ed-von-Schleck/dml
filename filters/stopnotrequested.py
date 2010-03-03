from __future__ import print_function

import src.states as states
import src.constants as constants
import src.events as events

NAME = "stop if not requested in HEAD"
SHORTNAME = "stop_if_not_requested"

def filter(target, target_shortname):
    send = target.send
    print("starting filter '{0}' for {1} ... ".format(NAME, target_shortname))
    try:
        while True:
            state, event, key, value = (yield)
            if state == states.START or state == states.HEAD:
                if event == events.CMD_LINE_OPTION or event == events.FUNCTION_DATA:
                    if key == constants.OUTPUT and value == target_shortname:
                        send((state, event, key, value))
                        break
                else:
                    print("filter '{0}' stopping '{1}' ... ".format(NAME, target_shortname))
                    target.close()
                    raise StopIteration
            send((state, event, key, value))
        while True:
            send((yield))
    except GeneratorExit:
        print("stopped filter '{0}' for '{1}'".format(NAME, target_shortname))
