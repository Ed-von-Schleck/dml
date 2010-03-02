from __future__ import print_function

import sys
import os, os.path

from tokenizer import Tokenizer
from dmlexceptions import DMLError
from broadcast import broadcast
from parserentry import parser_entry

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
            tokenizer.run(broadcaster, parser_entry)
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
