from __future__ import print_function

import sys
import os, os.path

from src.tokenizer import Tokenizer
from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.parserentry import parser_entry
import src.constants as constants
import src.events as events

class NullDevice():
    def write(self, dummy_out):
        pass

def main(dml_file, options=None):
    if options is not None and not options.verbose:
        sys.stdout = NullDevice()
    
    filepath, filename = os.path.split(dml_file)
    name, ext = os.path.splitext(os.path.basename(dml_file))
    del ext
    metadata = {"filepath": filepath, "name": name, "filename": filename, "working_dir": os.getcwd()}
    broadcaster = broadcast(metadata)
    broadcaster.next()
    
    # TODO: generic solution
    if options is not None and options.pdf:
        broadcaster.send((events.CMD_LINE_OPTION, constants.OUTPUT, "pdf"))
    if options is not None and options.html:
        broadcaster.send((events.CMD_LINE_OPTION, constants.OUTPUT, "html"))

    try:
        with open(dml_file) as dml:
            print("opening", dml_file, "...")
            tokenizer = Tokenizer(dml)
            tokenizer.run(broadcaster, parser_entry, metadata)
        print("closed", dml_file)
    except DMLError as dml_error:
        import linecache
        print(linecache.getline(dml_file, tokenizer.line_number))
        print("Error in line", tokenizer.line_number, ":", dml_error)
        sys.exit(1)
    
    # overwrite document settings
