from src.dmlexceptions import DMLSyntaxError
import src.constants as constants
import src.events as events

def title_cast_or_act(broadcaster, push):
    token = (yield)
    send = broadcaster.send
    if token != "=":
        broadcaster.send((events.TITLE_DEL, None, None))
        while True:
            send((events.DATA, constants.TOKEN, token))
            token = (yield)
            if token == "=":
                broadcaster.send((events.TITLE_DEL, None, None))
                break
    else:
        token = (yield)
        if token != "=":
            send((events.CAST_DEL, None, None))
            while True:
                send((events.DATA, constants.TOKEN, token))
                token = (yield)
                if token != "=":
                    continue
                token = (yield)
                if token == "=":
                    send((events.CAST_DEL, None, None))
                    break
                else:
                    raise DMLSyntaxError(token, "=")
        else:
            token = (yield)
            if token != "=":
                send((events.ACT_DEL, None, None))
                while True:
                    send((events.DATA, constants.TOKEN, token))
                    token = (yield)
                    if token != "=":
                        continue
                    token = (yield)
                    if token == "=":
                        token = (yield)
                        if token == "=":
                            send((events.ACT_DEL, None, None))
                            break
                        else:
                            raise DMLSyntaxError(token, "=")
                    else:
                        raise DMLSyntaxError(token, "==")
