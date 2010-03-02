from __future__ import print_function

import sys
import os, os.path

from tokenizer import Tokenizer
from function import dispatch
from titlecastact import title_cast_or_act
from key import key
from dmlexceptions import DMLError
from broadcast import broadcast
import constants
import events
from parsermanager import parser_manager

class NullDevice():
    def write(self, s):
        pass

def main(dml_file, options=None):
    if options is not None and not options.verbose:
        sys.stdout = NullDevice()
    
    filename, ext = os.path.splitext(os.path.basename(dml_file))
    broadcaster = broadcast(os.getcwd(), filename)
    broadcaster.next()
    
    try:
        with open(dml_file) as dml:
            print("opening", dml_file, "...")
            tokenizer = Tokenizer(dml)
            push = tokenizer.push
            for token in tokenizer:
                try:
                    # check for functions
                    if token == "@":
                        with parser_manager(dispatch, broadcaster, push) as function_dispatch:
                            while True:
                                function_dispatch.send(tokenizer.next())
                    elif token == "\n":
                        tokenizer.recognize_whitespace()
                        token = tokenizer.next()
                        tokenizer.ignore_whitespace()
                        if token == "\n":
                            broadcaster.send((events.NEW_PARAGRAPH, None, None))
                            tokenizer.recognize_whitespace()
                            token = tokenizer.next()
                            tokenizer.ignore_whitespace()
                            if token == " " or token == "\t":   # key (actor or tag or sth.)
                                with parser_manager(key, broadcaster, push) as key_parser:
                                    while True:
                                        key_parser.send(tokenizer.next())

                            elif token == "=":  # this is a title, cast or act
                                with parser_manager(title_cast_or_act, broadcaster, push) as tca:
                                    while True:
                                        tca.send(tokenizer.next())
                            elif token == "\n":
                                pass # ignore 3 linebreaks. Have to check if that makes sense, though
                            else:
                                broadcaster.send((events.BLOCK_START, None, None))
                                broadcaster.send((events.DATA, constants.TOKEN, token))

                        elif token == " " or token == "\t":
                            broadcaster.send((events.DATA, constants.TOKEN, "test"))
                            with parser_manager(key, broadcaster, push) as key_parser:
                                while True:
                                    key_parser.send(tokenizer.next())
                        else:
                            broadcaster.send((events.DATA, constants.TOKEN, token))
                            
                            
                    elif token == "\\":
                        token = tokenizer.next()
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
                        
                except StopIteration: # because it may be raised with any tokenizer.next()
                    pass
            broadcaster.send((events.END, None, None))
        print("closed", dml_file)
    except DMLError as dml_error:
        import linecache, sys
        print(linecache.getline(dml_file, tokenizer.line_number))
        print("Error in line", tokenizer.line_number, ":", dml_error)
        sys.exit(1)
    
    # overwrite document settings
    #if options.pdf:
    #    broadcaster.send((events.FUNCTION, constants.OUTPUT, "pdf"))
    #if options.html:
    #    broadcaster.send((events.FUNCTION, constants.OUTPUT, "html"))
