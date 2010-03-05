# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import shlex
from collections import deque

from src.parser import parser_manager, parser_entry
import src.events as events
import macros
from src.dmlexceptions import DMLMacroNameError, DMLSyntaxError

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = False
        self._lex_file.whitespace = " \r\t"
        self._lex_file.wordchars += "!,.;-"
        self._lex_file.commenters = ""
        
    @property
    def line_number(self):
        return self._lex_file.lineno

    def run(self, broadcaster, metadata):
        next = self._lex_file.next
        with parser_manager(parser_entry, broadcaster) as entry:
            for token in self._lex_file:               
                if token == "#":
                    # my own commenting logic, because shlex doesn't give me
                    # line endings
                    for token in self._lex_file:
                        if token == "\n":
                            break

                if token == "@":    # This checks for macros.
                    buffer = deque()
                    for token in self._lex_file:
                        if token == "}":
                            break
                        buffer.append(token)
                    name = buffer.popleft()
                    open_brackets = buffer.popleft()
                    if name not in macros.__all__:
                        raise DMLMacroNameError(name)
                    if open_brackets != "{":
                        raise DMLSyntaxError(open_brackets, "{")
                    macros.__dict__[name].macro(broadcaster,
                                        metadata,
                                        buffer,
                                        self._lex_file.push_token,
                                        self._lex_file.push_source)
                    continue
                entry(token)
                
            # I would rather do that:
            #map(entry, self._lex_file)
            # but then I guess I'd have to write my own lexer ...
            
            broadcaster.send((events.END, None, None))
        
