# -*- coding: utf-8
"""
the parser

Here we got the parser entry point which the lexer sends to, as well as a
contextmanager for parser coroutines.

"""

from __future__ import unicode_literals

from contextlib import contextmanager
from itertools import count

from src.dmlexceptions import DMLSyntaxError

def parser_entry(send):
    """
    the entry point for the dml-parser

    This coroutine is intended to be called from the tokenizer. It gets all 
    tokens (except for macros or comments) and sends either a tuple (event, None)
    or (b"data", token) to the broadcaster, where event is something like
    "new_paragraph" or "key_del" (delimiter), and token is, duh, the token.
    """
    delimiters = [b"title_del", b"cast_del", b"act_del", b"scene_del"]
    
    while True:
        token = (yield)
        if token == "\n":
            # On the first newline don't send any special events.
            token = (yield)
            if token == "\n":
                # The second newline indicates a new paragraph.
                send((b"new_paragraph", None))
                token = (yield)
                if token == "\n":
                    while token == "\n":
                        token = (yield)
                if token == "*":
                    # This delimits key (actor or tag or sth.).
                    send((b"key_del", None))
                    token = (yield)
                    while token != "*":
                        send((b"data", token))
                        token = (yield)
                    send((b"key_del", None))
                
                elif token == "=":
                    # This is a title, cast, act or scene.
                    i = 0
                    token = (yield)
                    while token == "=":
                        i += 1
                        token = (yield)
                    send((delimiters[i], None))
                    while token != "=":
                        send((b"data", token))
                        token = (yield)
                    send((delimiters[i], None))
                    for j in xrange(i):
                        token = (yield)
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
                # Again, this is a title, cast, act or scene.
                i = 0
                token = (yield)
                while token == "=":
                    i += 1
                    token = (yield)
                send((delimiters[i], None))
                while token != "=":
                    send((b"data", token))
                    token = (yield)
                send((delimiters[i], None))
                for j in xrange(i):
                    token = (yield)
                        
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

