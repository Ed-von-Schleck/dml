# -*- coding: utf-8

from __future__ import unicode_literals

import macros

def correct_macro_name_test():
    macro_string = """
!config {
output: pdf, html
table_of_contents: true
}"""
    tokenizer = Tokenizer(macro_string)
    for token in tokenizer:
        if token[0] == "!":
            if token[1:] not in macros.macros:
                raise DMLMacroNameError(token[1:])
