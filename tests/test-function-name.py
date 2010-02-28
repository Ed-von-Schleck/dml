import functions

def correct_function_name_test():
    function_string = """
!config {
output: pdf, html
table_of_contents: true
}"""
    tokenizer = Tokenizer(function_string)
    for token in tokenizer:
        if token[0] == "!":
            if token[1:] not in functions.functions:
                raise DMLFunctionNameError(token[1:])
