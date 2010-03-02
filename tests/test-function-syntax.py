from tokenizer import Tokenizer
from dmlexceptions import DMLSyntaxError
from nose.tools import raises

def correct_function_syntax_test():
    function_string = """
!config {
output: pdf, html
table_of_contents: true
}"""
    tokenizer = Tokenizer(function_string)
    for token in tokenizer:
        if token[0] == "!":
            open_brackets = tokenizer.next()
            if open_brackets != "{":
                raise DMLSyntaxError(open_brackets, "{")

@raises(DMLSyntaxError)
def incorrect_function_syntax_1_test():
    function_string = """
!config fail_me {
output: pdf, html
table_of_contents: true
}"""
    tokenizer = Tokenizer(function_string)
    for token in tokenizer:
       if token[0] == "!":
            open_brackets = tokenizer.next()
            if open_brackets != "{":
                raise DMLSyntaxError(open_brackets, "{")
