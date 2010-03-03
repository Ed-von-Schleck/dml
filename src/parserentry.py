"""
the entry point for the dml-parser

This coroutine here is intended to be called from the tokenizer. It get's all 
tokens (except for those commented out) and can choose to ignore the token, 
send a tuple(event, key (or None) and token (or None)) to the broadcaster
directly, or to delegate the token stream to a helper coroutine. They then
handle the stream and return control when they decide to do so.
"""


import src.constants as constants
import src.events as events
from src.parsermanager import parser_manager
from src.function import dispatch
from src.titlecastact import title_cast_or_act
from src.key import key

def parser_entry(broadcaster, metadata, push, source, get_next_whitespace, ignore_next_newline):
    send = broadcaster.send
    
    while True:
        token = (yield)
        if token == "@":    # This checks for functions.
            with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                while True:
                    function_dispatch.send((yield)) # the function dispatcher returns on token '}'.
                    
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
                            key_parser.send((yield))    # The key parser return for token ':'.
                            
                elif token == "@":
                    with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                        while True:
                            function_dispatch.send((yield))

                elif token == "=":  # This is a title, cast or act.
                    with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                        while True:
                            tca.send((yield))   # It will return when the same number of '=' is seen
                                                # twice with data in-between
                else:
                    send((events.BLOCK_START, None, None))  # If it's no function, key or title, cast or act,
                                                            # it must be a new block
                    send((events.DATA, constants.TOKEN, token))
            
            elif token == "@":
                with parser_manager(dispatch, broadcaster, metadata, push, source) as function_dispatch:
                    while True:
                        function_dispatch.send((yield))
                        
            elif token == "\t" or " " in token:
                with parser_manager(key, broadcaster, push) as key_parser:
                    while True:
                        key_parser.send((yield))
                        
            elif token == "=":
                with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                    while True:
                        tca.send((yield))
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
