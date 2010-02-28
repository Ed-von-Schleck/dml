from __future__ import print_function

import shlex

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = False
        self._lex_file.whitespace = " \t\r"
        self._lex_file.wordchars += "-=*"

    def __iter__(self):
        return self
        
    def next(self):
        token = self._lex_file.get_token()
        if token is self._lex_file.eof:
            raise StopIteration
        return token

    @property
    def line_number(self):
        return self._lex_file.lineno
