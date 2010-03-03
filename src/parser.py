"""
the parser

Here we got the parser entry point, which the tokenizer sends to, a bunch
of other coroutines the entry point delegates the token stream to, and a
contextmanager for those delegates

"""

from contextlib import contextmanager
import src.constants as constants
import src.events as events
import functions
from dmlexceptions import DMLSyntaxError, DMLFunctionNameError

def parser_entry(broadcaster, metadata, push, source, get_next_whitespace, ignore_next_newline):
    """
    the entry point for the dml-parser

    This coroutine is intended to be called from the tokenizer. It gets all 
    tokens (except for those commented out) and can choose to ignore the token, 
    send a tuple(event, key (or None) and token (or None)) to the broadcaster
    directly, or to delegate the token stream to a helper coroutine. They then
    handle the stream and return control when they decide to do so.
    """
    send = broadcaster.send
    
    while True:
        token = (yield)
        if token == "@":    # This checks for functions.
            with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                while True:
                    function_dispatch((yield)) # the function dispatcher returns on token '}'.
                    
        elif token == "\n":     # On the first newline don't send any special events.
            get_next_whitespace()   # Whitespace and tabs are key delimiters.
            token = (yield)
            if token == "\n":   # The second newline indicates a new paragraph.
                send((events.NEW_PARAGRAPH, None, None))
                get_next_whitespace()
                ignore_next_newline()   # Ignores more than two newlines.
                token = (yield)
                if token == "\t" or " " in token:   # This delimits key (actor or tag or sth.).
                    with parser_manager(key, broadcaster, push) as key_parser:
                        while True:
                            key_parser((yield))    # The key parser return for token ':'.
                            
                elif token == "@":
                    with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                        while True:
                            function_dispatch((yield))

                elif token == "=":  # This is a title, cast or act.
                    with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                        while True:
                            tca((yield))   # It will return when the same number of '=' is seen
                                                # twice with data in-between
                else:
                    send((events.BLOCK_START, None, None))  # If it's no function, key or title, cast or act,
                                                            # it must be a new block
                    send((events.DATA, constants.TOKEN, token))
            
            elif token == "@":
                with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                    while True:
                        function_dispatch((yield))
                        
            elif token == "\t" or " " in token:
                with parser_manager(key, broadcaster, push) as key_parser:
                    while True:
                        key_parser((yield))
                        
            elif token == "=":
                with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                    while True:
                        tca((yield))
            else:
                send((events.DATA, constants.TOKEN, token))
                
        elif token == "\\":
            token = (yield)
            if token == "\\":   # '\\' forces a line break.
                send((events.DATA, constants.FORCE_NEWLINE, token))
            else:               # '\' is waved through.
                send((events.DATA, constants.TOKEN, "\\"))
                send((events.DATA, constants.TOKEN, token))
                
        elif token == "<":
            send((events.INLINE_DIR_START, None, None))
            
        elif token == ">":
            send((events.INLINE_DIR_END, None, None))
        
        elif token == " ":
            continue
            # For some reason, sometimes whitespaces appears here.
            # I suspect some kind of prefetching in the generator
            # or a programming bug, who knows ...
        
        else:
            send((events.DATA, constants.TOKEN, token))
            
def dispatch(broadcaster, metadata, push, source):
    func_name = (yield)
    #print(func_name)
    try:
        if func_name not in functions.__all__:
            raise DMLFunctionNameError(func_name)
        open_brackets = (yield)
        if open_brackets != "{":
            raise DMLSyntaxError(open_brackets, "{")
        with parser_manager(functions.__dict__[func_name].function, broadcaster, metadata, push, source) as func:
            while True:
                token = (yield)
                if token == "}":
                    break
                func(token)
    except GeneratorExit:
        pass


def title_cast_or_act(broadcaster, push):
    token = (yield)
    send = broadcaster.send
    if token != "=":
        send((events.TITLE_DEL, None, None))
        while True:
            send((events.DATA, constants.TOKEN, token))
            token = (yield)
            if token == "=":
                send((events.TITLE_DEL, None, None))
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
        
@contextmanager
def parser_manager(coroutine, *args, **kwargs):
    c = coroutine(*args, **kwargs)
    c.next()
    try:
        yield c.send
    except StopIteration:
        pass
    finally:
        c.close()
