# -*- coding: utf-8
"""
a lexer that is unicode-aware

The main problem of shlex for dml is that it only accepts ascii as wordchars.
In order to get arbitrary unicode chars work with dml, we have to turn the
concept of shlex around: Instead of defining a list of wordchars and treat
everything else als one-char tokens, we treat everything as a wordchar except
for those defined as special (one-char) tokens.
"""

from __future__ import unicode_literals
from __future__ import print_function

from collections import deque, namedtuple
from contextlib import nested
from array import array

from src.dmlparser import parser_entry, parser_manager
from macros import macros
from src.dmlexceptions import DMLMacroSyntaxError, DMLMacroNameError

Source = namedtuple("Source", "file_obj filename lineno pos")

class DmlLex(object):
    """
    the lexer class
    
    This is not a drop-in replacement for pythons shlex - it operates in a 
    different way that is consistent with the rest of dml. It reads the file
    char by char and then sends tokens to the parser coroutine or whole
    (unparsed) strings to the macro dispatcher.
    """
    def __init__(self,
                 file_obj,
                 filename=None,
                 special_chars="\n*<>=\\",
                 whitespace=" \t\r"):
        self._source_stack = deque()
        self._file_obj = file_obj
        self.filename = filename
        self.lineno = 1
        self.pos = 0
        self._special_chars = special_chars
        self._whitespace = whitespace
        
    def push_source(self, new_file_obj, filename=None):
        self._source_stack.appendleft(Source(self._file_obj, self.filename, self.lineno, self.pos))
        self._file_obj = new_file_obj
        self.filename = filename
        self.lineno = 1
        self.pos = 0
        
    def pop_source(self):
        self._file_obj, self.filename, self.lineno, self.pos = self._source_stack.popleft()
        
    def run(self, broadcaster, metadata):
        special_chars = self._special_chars
        whitespace = self._whitespace
        concenate = "".join
        pos = self.pos
        with nested(parser_manager(parser_entry, broadcaster),
                    parser_manager(macro_dispatch, broadcaster, metadata, self)) as (entry, dispatch):
            #entry("\n")                     # new file is like newline, isn't it?
            while True:
                read = self._file_obj.read  # can be changed by push/pop_source
                current_char = read(1)
                
                pos += 1
                self.pos = pos              # likewise
                current_token = []          # faster than deque(), I tested it
                current_token_append = current_token.append
                while current_char or self._source_stack:
                    if not current_char:
                        if current_token:
                            entry(concenate(current_token))
                        entry("\n")
                        self.pop_source()
                        break
                    if current_char in whitespace:
                        if current_token:
                            entry(concenate(current_token))
                        break
                    if current_char in special_chars:
                        if current_token:
                            entry(concenate(current_token))
                        if current_char == "\\":     # handle escapes
                            slash = current_char
                            current_char = read(1)
                            if current_char not in "#@":
                                entry(slash)
                        if current_char == "\n":
                            self.lineno += 1
                            pos = 0
                        entry(current_char)
                        break
                    if current_char == '#':
                        if current_token:
                            entry(concenate(current_token))
                        self._file_obj.readline()
                        self.lineno += 1
                        pos = 0
                        entry("\n")
                        break
                    if current_char == '@':
                        if current_token:
                            entry(concenate(current_token))
                        dispatch(self._file_obj.readline())
                        self.lineno += 1
                        pos = 0
                        entry("\n")
                        break

                    current_token_append(current_char)
                    current_char = read(1)
                    pos += 1
                else:
                    broadcaster.send((b"end", None))
                    break

def macro_dispatch(broadcaster, metadata, lexer):
    """
    the macro dispatcher
    
    It first makes a list of all available macros. When a string is sent, it
    resolves the macro name and calls the macro (a function, not a coroutine)
    with the rest of the string.
    """
    macro_objs = {}
    for key, macro_cls in macros.items():
        macro_objs[key] = macro_cls(broadcaster, metadata, lexer)
    while True:
        raw = (yield)
        name, sep, data = raw.partition(" ")
        if not sep and not data:
            raise DMLMacroSyntaxError()
        if name not in macros:
            raise DMLMacroNameError(name)
        macro_objs[name].action(data)
