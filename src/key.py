from dmlexceptions import DMLSyntaxError
import constants
import events

def key(broadcaster, push):
    broadcaster.send((events.KEY_START, None, None))
    while True:
        token = (yield)
        if token == ":":
            broadcaster.send((events.KEY_END, None, None))
            break
        if token == "\n":
            broadcaster.send((events.KEY_END, None, None))
            push("\n")
            break
        broadcaster.send((events.DATA, constants.TOKEN, token))
