from __future__ import print_function

from tokenizer import Tokenizer
from dmlexceptions import DMLSyntaxError, DMLFunctionNameError
import functions

def main(dml_file, options):
    def _dummy_out(*args):
        pass
    out = print if options.verbose else _dummy_out
    with open(dml_file) as dml:
        out("opening", dml_file, "...")
        tokenizer = Tokenizer(dml)
        for token in tokenizer:
            #out(token)
            if token[0] == "!":
                if token[1:] in functions.functions:
                    open_brackets = tokenizer.next()
                    if open_brackets != "{":
                        raise DMLSyntaxError(open_brackets, "{")
             else:
                 raise DMLFunctionNameError(token[1:])
