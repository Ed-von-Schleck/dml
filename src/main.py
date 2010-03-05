# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os, os.path
from collections import namedtuple
from tempfile import NamedTemporaryFile

from src.tokenizer import Tokenizer
from src.dmlexceptions import DMLError
from src.broadcast import broadcast
from src.parser import parser_entry
import src.constants as constants
import src.events as events
from src.lex import DmlLex
import sinks

class NullDevice():
    def write(self, dummy_out):
        pass
        
MySink = namedtuple("MySink", "mod cor filters tmpfile closed")

def main(dml_file, options):
    filepath, filename = os.path.split(dml_file)
    name, ext = os.path.splitext(os.path.basename(dml_file))
    del ext
    metadata = {"filepath": filepath, "name": name, "filename": filename, "working_dir": os.getcwd()}
    
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
            number_of_filters = len(mod.filters)
            myfilters = []
            for i in range(number_of_filters):
                target = cor if i + 1 >= number_of_filters else mod.filters[i + 1]
                myfilter = mod.filters[i](target, mod.SHORTNAME)
                myfilter.next()
                myfilters.append(myfilter)
            mysinks.append(MySink(mod, cor, myfilters, tmpfile, False))
    
    broadcaster = broadcast(metadata, mysinks)
    broadcaster.next()

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
        print("A", dml_error.error_name, "was encountered:")
        print(dml_error)
        print("\tfile:  ", lexer.filename)
        print("\tline:  ", lexer.lineno)
        print("\tcolumn:", lexer.pos)
        print(linecache.getline(lexer.filename, lexer.lineno), end="")
        print(" " * (lexer.pos - 1) + "^")
        print ("*" * 80)
        sys.exit(1)
