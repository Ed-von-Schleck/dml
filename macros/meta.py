# -*- coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

from src.dmlexceptions import DMLError

    
class Meta(object):
    def __init__(self, broadcaster, metadata, lexer):
        self.broadcaster = broadcaster
        #self.metadata = metadata
        #self.lexer = lexer
        self.false_strings = ('false', '0', 'off', 'no')
        self.true_strings = ('true', '1', 'on', 'yes')
        self.papersizes = ('a4', 'a5', 'letter')
        
    def action(self, data):
        key, sep, value = data.partition(":")
        if not sep:
            raise DMLMetaSyntaxError("expected ':' in macro expression")
        if not value:
            raise DMLMetaSyntaxError("no value given")
            
        value = value.lower().strip()
        if key == "table_of_contents":
            if value in self.false_strings:
                self.broadcaster.send(("macro_data", (key, False)))
                return
            if value in self.true_strings:
                self.broadcaster.send(("macro_data", (key, True)))
                return
            raise DMLMetaSyntaxError("expected bool value ('True' or 'False')")
        if key == "paper_size":
            if value in self.papersizes:
                self.broadcaster.send(("macro_data", (key, value)))
                return
            raise DMLMetaSyntaxError("expected papersize value ('A5', 'A4', 'letter' and the like)")
        if key == "two_page":
            if value in self.false_strings:
                self.broadcaster.send(("macro_data", (key, False)))
                return
            if value in self.true_strings:
                self.broadcaster.send(("macro_data", (key, True)))
                return
            raise DMLMetaSyntaxError("expected bool value ('True' or 'False')")
        raise DMLMetaSyntaxError("unknown key")
        
                
class DMLMetaSyntaxError(DMLError):
    """Exception raised if a syntax error in a meta macro occurs

    Attributes:
        msg -- message
    """
    def __init__(self, msg):
        self.error_name = "meta macro Error"
        self.msg = msg
        
    def __str__(self):
        return self.msg

