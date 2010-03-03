from __future__ import print_function

import sys
import os, os.path

from src.tokenizer import Tokenizer
from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.parser import parser_entry
import src.constants as constants
import src.events as events


class NullDevice():
    def write(self, dummy_out):
        pass

def main(dml_file, options=None):
    filepath, filename = os.path.split(dml_file)
    name, ext = os.path.splitext(os.path.basename(dml_file))
    del ext
    metadata = {"filepath": filepath, "name": name, "filename": filename, "working_dir": os.getcwd()}
    
    # Initialize broadcaster, the endpoint of the parsing chain
    broadcaster = broadcast(metadata)
    broadcaster.next()
    
    if options is not None:
        if not options.verbose:
            sys.stdout = NullDevice()
        # This won't win a beaty contest, but seems robust.
        import sinks
        sink_mods = [sinks.__dict__[mod] for mod in sinks.__all__]
        for mod in sink_mods:
            if options.__dict__[mod.SHORTNAME]:
                broadcaster.send((events.CMD_LINE_OPTION, constants.OUTPUT, mod.SHORTNAME))

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
