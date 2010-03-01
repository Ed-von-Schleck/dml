from __future__ import print_function

import src.states as states
import src.constants as constants

NAME = "stop if not requested in HEAD"
SHORTNAME = "stop_if_not_requested"

def filter(target, target_shortname):
    listening_for_output_request = True
    print("starting filter '{0}' for {1} ... ".format(NAME, target_shortname))
    try:
        while True:
            state, event, key, value = (yield)
            if listening_for_output_request:
                if state == states.FUNCTION_HEAD:
                    if key == constants.OUTPUT and value == target_shortname:
                        listening_for_output_request = False
                elif state != states.START or state != states.HEAD:
                    print("filter '{0}' stopping '{1}' ... ".format(NAME, target_shortname))
                    target.throw(GeneratorExit)                    
                    break
            target.send((state, event, key, value))
    except GeneratorExit:
        print("stopped filter '{0}' for '{1}'".format(NAME, target_shortname))
