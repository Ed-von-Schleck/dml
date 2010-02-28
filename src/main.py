from __future__ import print_function

import sys
import os
from collections import deque

from tokenizer import Tokenizer
from function import dispatch
from dmlexceptions import DMLError
from broadcast import broadcast
import constants 

class NullDevice():
    def write(self, s):
        pass

def main(dml_file, options):
    if not options.verbose:
        sys.stdout = NullDevice()
        
    broadcaster = broadcast()
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
                else:
                    buffer.append(token)
        print("closed", dml_file)
    except DMLError as dml_error:
        import linecache, sys
        print(linecache.getline(dml_file, tokenizer.line_number))
        print("Error in line", tokenizer.line_number, ":", dml_error)
        sys.exit(1)
    
    # overwrite document settings
    if options.pdf:
        broadcaster.send((constants.OUTPUT, "pdf"))
    if options.html:
        broadcaster.send((constants.OUTPUT, "html"))
