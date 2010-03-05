# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os, os.path

from src.tokenizer import Tokenizer
from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.parser import parser_entry
import src.constants as constants
import src.events as events
from src.lex import DmlLex

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
            if options.__dict__[mod.NAME]:
                broadcaster.send((events.CMD_LINE_OPTION, constants.OUTPUT, mod.NAME))

    try:
        try:
            dml = open(dml_file, 'r')
            print("opening", dml_file, "...")
            lexer = DmlLex(dml, filename=dml_file)
        
            lexer.run(broadcaster, metadata)
            #tokenizer = Tokenizer(dml)
            #tokenizer.run(broadcaster, metadata)
        except IOError:
            pass
        finally:
            dml.close()
            print("closed", dml_file)
    except DMLError as dml_error:
        import linecache
        print ("*" * 80)
        print("A", dml_error.__class__.__name__, "was encountered:")
        print(dml_error)
        print("\tfile:  ", lexer.filename)
        print("\tline:  ", lexer.lineno)
        print("\tcolumn:", lexer.pos)
        print(linecache.getline(lexer.filename, lexer.lineno), end="")
        print(" " * (lexer.pos - 1) + "^")
        print ("*" * 80)
        sys.exit(1)
