# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os, os.path
from collections import namedtuple
from tempfile import NamedTemporaryFile
import io

from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.lex import DmlLex
from sinks import *     # so that they register themselves
import src.registry

class NullDevice():
    "Dummy output device if option '-q' is selected"
    def write(self, dummy_out):
        pass
        
MySink = namedtuple("MySink", "meta send tmpfile")
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
    for sinkname, sink in src.registry.sinks.items():
        if options.__dict__[sinkname]:
            tmpfile = NamedTemporaryFile(mode="w", delete=False)
            cor = sink.coroutine(metadata, tmpfile)
            cor.next()
            mysinks.append(MySink(sink, cor.send, tmpfile))
    
    broadcaster = broadcast(metadata, mysinks)
    broadcaster.next()

    try:
        dml = io.open(dml_file, "rU", encoding="utf-8")
        print(b"opening", dml_file, b"...")
        lexer = DmlLex(dml, filename=dml_file)
        lexer.run(broadcaster, metadata)
    except IOError:
        pass
    except DMLError as dml_error:
        import linecache
        print (b"*" * 80)
        print(b"A", dml_error.error_name, b"was encountered:")
        print(dml_error)
        print(b"\tfile:  ", lexer.filename)
        print(b"\tline:  ", lexer.lineno)
        print(b"\tcolumn:", lexer.pos)
        print(linecache.getline(lexer.filename, lexer.lineno), end="")
        print(b" " * (lexer.pos - 1) + b"^")
        print (b"*" * 80)
        sys.exit(1)
    finally:
        dml.close()
        print(b"closed", dml_file)
