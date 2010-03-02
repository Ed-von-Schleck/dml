from __future__ import print_function

import shlex

from parsermanager import parser_manager
import events

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = False
        self._lex_file.whitespace = " \r"
        self._lex_file.wordchars += "!,.;"
        self._lex_file.commenters = ""
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
        
    def set_whitespace(self, value):
        if value:
            self._lex_file.whitespace = self._lex_file.whitespace.replace(" ", "")
        else:
            if not " " in self._lex_file.whitespace:
                self._lex_file.whitespace += " "

    def run(self, broadcaster, parser_entry):
        with parser_manager(parser_entry, broadcaster, self._lex_file.push_token, self.set_whitespace) as entry:
            get_token = self._lex_file.get_token
            eof = self._eof
            send = entry.send
            while True:
                token = get_token()
                if token == "#":
                    # my own commenting logic, because shlex doesn't give me
                    # line endings
                    while True:
                        token = get_token()
                        if token == "\n":
                            break
                        elif token is eof:
                            break
                elif token is eof:
                    break
                send(token)
            broadcaster.send((events.END, None, None))
        
