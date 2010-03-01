from __future__ import print_function

import sys
import os, os.path
from collections import deque

from tokenizer import Tokenizer
from function import dispatch
from dmlexceptions import DMLError
from broadcast import broadcast
import constants
import events

class NullDevice():
    def write(self, s):
        pass

def main(dml_file, options):
    if not options.verbose:
        sys.stdout = NullDevice()
    
    filename, ext = os.path.splitext(os.path.basename(dml_file))
    path = os.getcwd()
    broadcaster = broadcast(path, filename)
    broadcaster.next()
    
    try:
        with open(dml_file) as dml:
            print("opening", dml_file, "...")
            tokenizer = Tokenizer(dml)
            buffer = deque()
            for token in tokenizer:
                # check for functions
                if token == "@":
                    function_dispatch = dispatch(broadcaster, tokenizer.next())
                    function_dispatch.next()
                    try:
                        while True:
                            function_dispatch.send(tokenizer.next())
                    except StopIteration:
                        pass
                    finally:
                        function_dispatch.close()
                elif token == "=":
                    token = tokenizer.next()
                    if token != "=":
                        print("processing title ...")
                        broadcaster.send((events.TITLE_START, None, None))
                        while True:
                            broadcaster.send((events.TITLE_DATA, constants.TITLE, token))
                            token = tokenizer.next()
                            if token == "=":
                                broadcaster.send((events.TITLE_END, None, None))
                                break
                    else:
                        token = tokenizer.next()
                        if token != "=":
                            print("processing cast ...")
                            broadcaster.send((events.CAST_START, None, None))
                            while True:
                                broadcaster.send((events.CAST_DATA, constants.CAST, token))
                                token = tokenizer.next()
                                if token == "=":
                                    token = tokenizer.next()
                                    if token == "=":
                                        broadcaster.send((events.CAST_END, None, None))
                                        break
                                    else:
                                        raise DMLSyntaxError(token, "=")
                        else:
                            token = tokenizer.next()
                            if token != "=":
                                print("processing act ...")
                                broadcaster.send((events.ACT_START, None, None))
                                while True:
                                    broadcaster.send((events.ACT_DATA, constants.ACT, token))
                                    token = tokenizer.next()
                                    if token == "=":
                                        token = tokenizer.next()
                                        if token == "=":
                                            token = tokenizer.next()
                                            if token == "=":
                                                broadcaster.send((events.ACT_END, None, None))
                                                break
                                            else:
                                                raise DMLSyntaxError(token, "=")
                                        else:
                                            raise DMLSyntaxError(token, "==")
                elif token == "\n":
                    broadcaster.send((events.BODY, constants.NEWLINE, token))
                else:
                    broadcaster.send((events.BODY, constants.TOKEN, token))
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
