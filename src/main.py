# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os, os.path
from collections import namedtuple
from tempfile import NamedTemporaryFile
import io
import codecs

from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.lex import DmlLex
import sinks

class NullDevice():
    "Dummy output device if option '-q' is selected"
    def write(self, dummy_out):
        pass
        
MySink = namedtuple("MySink", "mod cor tmpfile closed")
Metadata = namedtuple("Metadata", "filepath name filename working_dir")

def main(dml_file, options):
    filepath, filename = os.path.split(dml_file)
    name, ext = os.path.splitext(os.path.basename(dml_file))
    del ext
    metadata = Metadata(filepath, name, filename, os.getcwd())
    if not options.verbose:
        sys.stdout = NullDevice()
        
    # This won't win a beauty contest, but seems robust.
    mysinks = []
    sink_mods = [sinks.__dict__[mod] for mod in sinks.__all__]
    for mod in sink_mods:
        if options.__dict__[mod.NAME]:
            tmpfile = NamedTemporaryFile(mode="w", delete=False)
            cor = mod.sink(metadata, tmpfile)
            cor.next()
            mysinks.append(MySink(mod, cor, tmpfile, False))
    
    broadcaster = broadcast(metadata, mysinks)
    broadcaster.next()

    try:
        try:
            dml = io.open(dml_file, "rU", encoding="utf-8")
            print("opening", dml_file, "...")
            lexer = DmlLex(dml, filename=dml_file)
            lexer.run(broadcaster, metadata)
        except IOError:
            pass
        finally:
            dml.close()
            print("closed", dml_file)
    except DMLError as dml_error:
        import linecache
        print ("*" * 80)
        print("A", dml_error.error_name, "was encountered:")
        print(dml_error)
        print("\tfile:  ", lexer.filename)
        print("\tline:  ", lexer.lineno)
        print("\tcolumn:", lexer.pos)
        print(linecache.getline(lexer.filename, lexer.lineno), end="")
        print(" " * (lexer.pos - 1) + "^")
        print ("*" * 80)
        sys.exit(1)
