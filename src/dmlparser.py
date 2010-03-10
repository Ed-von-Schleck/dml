# -*- coding: utf-8
"""
the parser

Here we got the parser entry point which the lexer sends to, a bunch of other
coroutines the entry point delegates the token stream to, and a contextmanager
for those delegates.

"""

from __future__ import unicode_literals

from contextlib import contextmanager
from collections import namedtuple

from src.constants import events, states
from src.dmlexceptions import DMLSyntaxError, DMLMacroNameError

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
                send((events.NEW_PARAGRAPH, None))
                token = (yield)
                if token == "\n":
                    while True:
                        token = (yield)
                        if token != "\n":
                            break
                if token == "*":            # This delimits key (actor or tag or sth.).
                    with parser_manager(key, broadcaster) as key_parser:
                        while True:
                            key_parser((yield))    # The key parser return for token ':'.
                elif token == "=":          # This is a title, cast or act.
                    with parser_manager(title_cast_or_act, broadcaster) as tca:
                        while True:
                            tca((yield))    # It will return when the same number of '=' is seen
                                            # twice with data in-between
                else:
                    send((events.BLOCK_START, None))  # If it's no macro, key or title, cast or act,
                                                            # it must be a new block
                    send((events.DATA, token))
                        
            elif token == "*":
                with parser_manager(key, broadcaster) as key_parser:
                    while True:
                        key_parser((yield))
                        
            elif token == "=":
                with parser_manager(title_cast_or_act, broadcaster) as tca:
                    while True:
                        tca((yield))
            elif token == "<":
                send((events.INLINE_DIR_START, None))
                
            elif token == ">":
                send((events.INLINE_DIR_END, None))
            else:
                send((events.DATA, token))
                
        elif token == "\\":
            token = (yield)
            if token == "\\":               # '\\' forces a line break.
                send((events.DATA, "\n"))
            else:                           # '\' is waved through.
                send((events.DATA, "\\"))
                send((events.DATA, token))
                
        elif token == "<":
            send((events.INLINE_DIR_START, None))
            
        elif token == ">":
            send((events.INLINE_DIR_END, None))
        
        else:
            send((events.DATA, token))

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
        send((events.TITLE_DEL, None))
        while True:
            send((events.DATA, token))
            token = (yield)
            if token == "=":
                send((events.TITLE_DEL, None))
                break
    else:
        token = (yield)
        if token != "=":
            send((events.CAST_DEL, None))
            while True:
                send((events.DATA, token))
                token = (yield)
                if token != "=":
                    continue
                token = (yield)
                if token == "=":
                    send((events.CAST_DEL, None))
                    break
                raise DMLSyntaxError(token, "=")
        else:
            token = (yield)
            if token != "=":
                send((events.ACT_DEL, None))
                while True:
                    send((events.DATA, token))
                    token = (yield)
                    if token != "=":
                        continue
                    token = (yield)
                    if token == "=":
                        token = (yield)
                        if token == "=":
                            send((events.ACT_DEL, None))
                            break
                        raise DMLSyntaxError(token, "=")
                    raise DMLSyntaxError(token, "==")
            else:
                token = (yield)
                if token != "=":
                    send((events.SCENE_DEL, None))
                    while True:
                        send((events.DATA, token))
                        token = (yield)
                        if token != "=":
                            continue
                        token = (yield)
                        if token == "=":
                            token = (yield)
                            if token == "=":
                                token = (yield)
                                if token == "=":
                                    send((events.SCENE_DEL, None))
                                    break
                                raise DMLSyntaxError(token, "=")
                            raise DMLSyntaxError(token, "==")
                        raise DMLSyntaxError(token, "===")
def key(broadcaster):
    """
    key parser
    
    This little critter gets called when a '*' is seen. It sends data until
    a the next '*' is encountered.
    """
    broadcaster.send((events.KEY_START, None))
    while True:
        token = (yield)
        if token == "*":
            broadcaster.send((events.KEY_END, None))
            break
        broadcaster.send((events.DATA, token))
        
@contextmanager
def parser_manager(coroutine, *args, **kwargs):
    """
    the parser contextmanager
    
    This handy little function initializes a parser coroutine and returns its
    'send' function. It also swallows the StopIteration exception.
    """
    cor = coroutine(*args, **kwargs)
    cor.next()
    try:
        yield cor.send
    except StopIteration:
        pass

