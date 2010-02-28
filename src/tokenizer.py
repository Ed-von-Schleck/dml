import shlex

class Tokenizer(object):
    def __init__(self, dml):
        self._lex_file = shlex.shlex(dml)
        self._lex_file.whitespace_split = True

    def __iter__(self):
        return self
        
    def next(self):
        token = self._lex_file.get_token()
        if token is self._lex_file.eof:
            raise StopIteration
        return token
        
    def get_tokens_until(self, end_token):
        tokens = []
        while True:
            token = self._lex_file.get_token()
            tokens.append(token)
            if token == end_token:
                return tokens
            if token is self._lex_file.eof:
                raise EOFError("'{0}' was not found before EOF was hit".format(end_token))
