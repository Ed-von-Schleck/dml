from dmlexceptions import DMLSyntaxError
import constants
import events

def title_cast_or_act(broadcaster, push):
    token = (yield)
    if token != "=":
        broadcaster.send((events.TITLE_START, None, None))
        while True:
            broadcaster.send((events.DATA, constants.TOKEN, token))
            token = (yield)
            if token == "=":
                broadcaster.send((events.TITLE_END, None, None))
                break
    else:
        token = (yield)
        if token != "=":
            broadcaster.send((events.CAST_START, None, None))
            while True:
                broadcaster.send((events.DATA, constants.TOKEN, token))
                token = (yield)
                if token != "=":
                    continue
                token = (yield)
                if token == "=":
                    broadcaster.send((events.CAST_END, None, None))
                    break
                else:
                    raise DMLSyntaxError(token, "=")
        else:
            token = (yield)
            if token != "=":
                broadcaster.send((events.ACT_START, None, None))
                while True:
                    broadcaster.send((events.DATA, constants.TOKEN, token))
                    token = (yield)
                    if token != "=":
                        continue
                    token = (yield)
                    if token == "=":
                        token = (yield)
                        if token == "=":
                            broadcaster.send((events.ACT_END, None, None))
                            break
                        else:
                            raise DMLSyntaxError(token, "=")
                    else:
                        raise DMLSyntaxError(token, "==")
