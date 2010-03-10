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


from src.dmlparser import parser_entry, parser_manager
from macros import macros
from src.dmlexceptions import DMLMacroSyntaxError, DMLMacroNameError

Source = namedtuple("Source", "file_obj filename lineno pos")

class DmlLex(object):
    def __init__(self,
                 file_obj,
                 filename=None,
                 special_chars="<*\n>=\\",
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
        current_token = deque()
        with nested(parser_manager(parser_entry, broadcaster),
                    parser_manager(macro_dispatch, broadcaster, metadata, self)) as (entry, dispatch):
            while True:
                current_char = self._file_obj.read(1)
                self.pos += 1
                current_token.clear()
                while current_char or self._source_stack:
                    if not current_char:
                        self.pop_source()
                        break
                    if current_char in special_chars:
                        if current_char == "\n":
                            self.lineno += 1
                            self.pos = 0
                        if current_token:
                            entry("".join(current_token))
                        entry(current_char)
                        break
                    if current_char in whitespace:
                        if current_token:
                            entry("".join(current_token))
                        break
                    if current_char == '#':
                        if current_token:
                            entry("".join(current_token))
                        self._file_obj.readline()
                        self.lineno += 1
                        entry("\n")
                        break
                    if current_char == '@':
                        if current_token:
                            entry("".join(current_token))
                        line = self._file_obj.readline()
                        dispatch(line)
                        self.lineno += 1
                        entry("\n")
                        break
                    
                    current_token.append(current_char)
                    current_char = self._file_obj.read(1)
                    self.pos += 1
                else:
                    break


def macro_dispatch(broadcaster, metadata, lexer):
    macro_objs = {}
    for key, macro_cls in macros.items():
        macro_objs[key] = macro_cls(broadcaster, metadata, lexer)
    while True:
        raw = (yield)
        #print(raw)
        name, sep, data = raw.partition(" ")
        if not sep and not data:
            raise DMLMacroSyntaxError()
        if name not in macros:
            raise DMLMacroNameError(name)
        macro_objs[name].action(data)
