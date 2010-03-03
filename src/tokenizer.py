from __future__ import print_function

import shlex

from src.parser import parser_manager
import src.events as events

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = False
        self._lex_file.whitespace = " \r\t"
        self._lex_file.wordchars += "!,.;-"
        self._lex_file.commenters = ""
        self._get_next_whitespace = False
        self._ignore_next_newline = False
        
    @property
    def line_number(self):
        return self._lex_file.lineno
                
    def get_next_whitespace(self):
        self._get_next_whitespace = True
        self._lex_file.whitespace = self._lex_file.whitespace.replace(" ", "")
        self._lex_file.whitespace = self._lex_file.whitespace.replace("\t", "")
        
    def ignore_next_newline(self):
        self._ignore_next_newline = True
        self._lex_file.whitespace += "\n"

    def run(self, broadcaster, parser_entry, metadata):
        with parser_manager(parser_entry,
                            broadcaster,
                            metadata,
                            self._lex_file.push_token,
                            self._lex_file.push_source,
                            self.get_next_whitespace,
                            self.ignore_next_newline) as entry:
            
            for token in self._lex_file:
                if token == "#":
                    # my own commenting logic, because shlex doesn't give me
                    # line endings
                    for token in self._lex_file:
                        if token == "\n":
                            break
                
                if self._get_next_whitespace:
                    self._get_next_whitespace = False
                    self._lex_file.whitespace += " \t"
                if self._ignore_next_newline:
                    self._ignore_next_newline = False
                    self._lex_file.whitespace = self._lex_file.whitespace.replace("\n", "")
                entry(token)
            
            # I would rather do that:
            #map(entry, self._lex_file)
            # but then I guess I'd have to write my own lexer ...
            
            broadcaster.send((events.END, None, None))
        
