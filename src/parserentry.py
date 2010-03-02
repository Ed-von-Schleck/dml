import constants
import events
from parsermanager import parser_manager
from function import dispatch
from titlecastact import title_cast_or_act
from key import key
from tokenizer import Tokenizer

def parser_entry(broadcaster, push, set_whitespace):
    while True:
        token = (yield)
        # check for functions
        if token == "@":
            with parser_manager(dispatch, broadcaster, push) as function_dispatch:
                while True:
                    function_dispatch.send((yield))
        elif token == "\n":
            set_whitespace(True)
            token = (yield)
            set_whitespace(False)
            if token == "\n":
                broadcaster.send((events.NEW_PARAGRAPH, None, None))
                set_whitespace(True)
                token = (yield)
                set_whitespace(False)
                if token == " " or token == "\t":   # key (actor or tag or sth.)
                    with parser_manager(key, broadcaster, push) as key_parser:
                        while True:
                            key_parser.send((yield))

                elif token == "=":  # this is a title, cast or act
                    with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                        while True:
                            tca.send((yield))
                elif token == "\n":
                    pass # ignore 3 linebreaks. Have to check if that makes sense, though
                else:
                    broadcaster.send((events.BLOCK_START, None, None))
                    broadcaster.send((events.DATA, constants.TOKEN, token))

            elif token == " " or token == "\t":
                with parser_manager(key, broadcaster, push) as key_parser:
                    while True:
                        key_parser.send((yield))
            else:
                broadcaster.send((events.DATA, constants.TOKEN, token))
                
                
        elif token == "\\":
            token = (yield)
            if token == "\\":
                broadcaster.send((events.DATA, constants.FORCE_NEWLINE, token))
            else:
                broadcaster.send((events.DATA, constants.TOKEN, "\\"))
                broadcaster.send((events.DATA, constants.TOKEN, token))
                
        elif token == "<":
            broadcaster.send((events.INLINE_DIR_START, None, None))
            
        elif token == ">":
            broadcaster.send((events.INLINE_DIR_END, None, None))
            
        else:
            if token != " ":   
                # for some reason, sometimes whitespaces appears here
                # I suspect some kind of prefetching in the generator
                # or a programming bug, who knows ...
                broadcaster.send((events.DATA, constants.TOKEN, token))
