# -*- coding: utf-8
"""
a lexer that is unicode-aware, replaces shlex

The main problem of shlex for dml is that it only accepts ascii as wordchars.
In order to get arbitrary unicode chars work with dml, we have to turn the
concept of shlex around: Instead of defining a list of wordchars and treat
everything else als one-char tokens, we treat everything as a wordchar except
for those defined as special (one-char) tokens.
"""



from __future__ import unicode_literals

def lex(filename):
    with open(filename) as file_obj:
        while True:
            pass
        
