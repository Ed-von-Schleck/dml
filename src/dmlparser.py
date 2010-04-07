# -*- coding: utf-8
"""
the parser

Here we got the parser entry point which the lexer sends to, a bunch of other
coroutines the entry point delegates the token stream to, and a contextmanager
for those delegates.

"""

from __future__ import unicode_literals

from contextlib import contextmanager

from src.dmlexceptions import DMLSyntaxError

def parser_entry(broadcaster):
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
        
        if token == "\n":                   # On the first newline don't send any special events.
            token = (yield)
            if token == "\n":               # The second newline indicates a new paragraph.
                send((b"new_paragraph", None))
                token = (yield)
                if token == "\n":
                    while token == "\n":
                        token = (yield)
                if token == "*":            # This delimits key (actor or tag or sth.).
                    send((b"key_del", None))
                    token = (yield)
                    while token != "*":
                        send((b"data", token))
                        token = (yield)
                    send((b"key_del", None))
                elif token == "=":          # This is a title, cast or act.
                    with parser_manager(title_cast_or_act, broadcaster) as tca:
                        while True:
                            tca((yield))    # It will return when the same number of '=' is seen
                                            # twice with data in-between
                else:
                    # If it's no macro, key or title, cast or act, it must be a new block
                    send((b"block_start", None))
                    send((b"data", token))
                        
            elif token == "*":
                send((b"key_del", None))
                token = (yield)
                while token != "*":
                    send((b"data", token))
                    token = (yield)
                send((b"key_del", None))
                        
            elif token == "=":
                with parser_manager(title_cast_or_act, broadcaster) as tca:
                    while True:
                        tca((yield))
                        
            elif token in "<>":
                send((b"inline_dir_del", None))
                
            else:
                send((b"data", token))
                
        elif token == "\\":
            token = (yield)
            if token == "\\":               # '\\' forces a line break.
                send((b"data", "\n"))
            else:                           # '\' is waved through.
                send((b"data", "\\"))
                send((b"data", token))
                
        elif token in "<>":
            send((b"inline_dir_del", None))
        
        else:
            send((b"data", token))

def title_cast_or_act(broadcaster):
    """
    parses a title, cast or act declaration
    
    It gets called when a '=' is seen. It then lookes if there are more of
    them, then it wants some data and afterwards the same number of '=' again
    or it gets angry (raises DMLSyntaxError)
    """
    token = (yield)
    send = broadcaster.send
    if token != "=":
        send((b"title_del", None))
        while True:
            send((b"data", token))
            token = (yield)
            if token == "=":
                send((b"title_del", None))
                break
    else:
        token = (yield)
        if token != "=":
            send((b"cast_del", None))
            while True:
                send((b"data", token))
                token = (yield)
                if token != "=":
                    continue
                token = (yield)
                if token == "=":
                    send((b"cast_del", None))
                    break
                raise DMLSyntaxError(token, "=")
        else:
            token = (yield)
            if token != "=":
                send((b"act_del", None))
                while True:
                    send((b"data", token))
                    token = (yield)
                    if token != "=":
                        continue
                    token = (yield)
                    if token == "=":
                        token = (yield)
                        if token == "=":
                            send((b"act_del", None))
                            break
                        raise DMLSyntaxError(token, "=")
                    raise DMLSyntaxError(token, "==")
            else:
                token = (yield)
                if token != "=":
                    send((b"scene_del", None))
                    while True:
                        send((b"data", token))
                        token = (yield)
                        if token != "=":
                            continue
                        token = (yield)
                        if token == "=":
                            token = (yield)
                            if token == "=":
                                token = (yield)
                                if token == "=":
                                    send((b"scene_del", None))
                                    break
                                raise DMLSyntaxError(token, "=")
                            raise DMLSyntaxError(token, "==")
                        raise DMLSyntaxError(token, "===")

@contextmanager
def parser_manager(coroutine, *args, **kwargs):
    """
    the parser contextmanager
    
    This handy little function initializes a parser coroutine and returns its
    'send' function. It also swallows the StopIteration exception.
    """
    cor = coroutine(*args, **kwargs)
    cor.next()
    send = cor.send
    try:
        yield send
    except StopIteration:
        pass

