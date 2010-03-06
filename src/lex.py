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

from src.dmlparser import parser_entry, parser_manager
import macros

Source = namedtuple("Source", "file_obj filename lineno pos")

class DmlLex(object):
    def __init__(self,
                 file_obj,
                 filename=None,
                 special_chars="@{}*\n<>:=\\",
                 whitespace=" \t\r",
                 commentors="#"):
        self._source_stack = deque()
        self._pushback_stack = deque()
        self._file_obj = file_obj
        self.filename = filename
        self.lineno = 2
        self.pos = 0
        self._special_chars = special_chars
        self._whitespace = whitespace
        self._commentors = commentors
        
    def push_source(self, new_file_obj, filename=None):
        self._source_stack.appendleft(Source(self._file_obj, self.filename, self.lineno, self.pos))
        self._file_obj = new_file_obj
        self.filename = filename
        self.lineno = 2
        self.pos = 0
        
    def pop_source(self):
        self._file_obj, self.filename, self.lineno, self.pos = self._source_stack.popleft()
        
    def push_token(self, token):
        self._pushback_stack.append(token)
        
    def pop_token(self):
        return self._pushback_stack.pop()

    def run(self, broadcaster, metadata):
        special_chars = self._special_chars
        whitespace = self._whitespace
        commentors = self._commentors
        read = self._file_obj.read
        readline = self._file_obj.readline
        pop_token = self.pop_token
        with parser_manager(preprocessor, broadcaster, metadata, self) as prepro:
            while True:
                if self._pushback_stack:
                    prepro(pop_token())
                    break
                current_char = self._file_obj.read(1)
                self.pos += 1
                current_token = deque()
                while current_char or self._source_stack or self._pushback_stack:
                    if not current_char:
                        self.pop_source()
                        break
                    if current_char in special_chars:
                        if current_char == "\n":
                            self.lineno += 1
                            self.pos = 0
                        if current_token:
                            prepro("".join(current_token))
                        prepro(current_char)
                        break
                    if current_char in whitespace:
                        if current_token:
                            prepro("".join(current_token))
                        break
                    if current_char in commentors:
                        if current_token:
                            prepro("".join(current_token))
                        self._file_obj.readline()
                        prepro("\n")
                        break
                    
                    current_token.append(current_char)
                    current_char = self._file_obj.read(1)
                    self.pos += 1
                else:
                    break
                
                
def preprocessor(broadcaster, metadata, lexer):
    """
    preprocessing the token stream
    
    The preprocessor sorts out macros (beginning with '@') and hands them a
    deque of tokens in the macro block. They aren't coroutines cause they might
    want to mess with the token stream. They all get the metadata als well as
    the lexer object.
    
    """
    with parser_manager(parser_entry, broadcaster) as entry:
        macronames = macros.__all__
        macrodict = macros.__dict__
        while True:
            token = (yield)
            if token == "@":    # This checks for macros.
                buffer = deque()
                while True:
                    token = (yield)
                    if token == "}":
                        break
                    buffer.append(token)
                name = buffer.popleft()
                open_brackets = buffer.popleft()
                if name not in macronames:
                    raise DMLMacroNameError(name)
                if open_brackets != "{":
                    raise DMLSyntaxError(open_brackets, "{")
                macrodict[name].macro(broadcaster, metadata, buffer, lexer)
                continue
            entry(token)            
        broadcaster.send((events.END, None, None))
