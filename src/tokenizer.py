from __future__ import print_function

import shlex

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = False
        self._lex_file.whitespace = " \r"
        self._lex_file.wordchars += "!,.;"
        self._eof = self._lex_file.eof

    def __iter__(self):
        return self
        
    def next(self):
        token = self._lex_file.get_token()
        if token is self._eof:
            raise StopIteration
        return token

    @property
    def line_number(self):
        return self._lex_file.lineno
    
    def recognize_whitespace(self):
        self._lex_file.whitespace = self._lex_file.whitespace.replace(" ", "")

    def ignore_whitespace(self):
        if not " " in self._lex_file.whitespace:
            self._lex_file.whitespace += " "
            
    def push(self, token):
        self._lex_file.push_token(token)
