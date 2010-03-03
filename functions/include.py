from __future__ import print_function

from os.path import exists, join

from src.dmlexceptions import DMLError
import src.constants as constants
import src.events as events

def function(broadcaster, metadata, push, source):
    try:
        while True:
            token = (yield)
            if token in "\n\t\r ":
                continue
            if exists(join(metadata["working_dir"], metadata["filepath"], token)):
                full_filename = join(metadata["working_dir"], metadata["filepath"], token)
            elif exists(join(metadata["working_dir"], token)):
                full_filename = join(metadata["working_dir"], token)
            else:
                raise DMLIncludeIOError(token,
                    join(metadata["working_dir"], metadata["filepath"], token),
                    join(metadata["working_dir"], token))
            while True:
                token = (yield)
    except GeneratorExit:
        push("\n")
        source(open(full_filename), full_filename)

class DMLIncludeSyntaxError(DMLError):
    """Exception raised if a syntax error in a include function occurs

    Attributes:
        msg -- message
    """

class DMLIncludeIOError(DMLError):
    """Exception raised if the file to be included does not exist

    Attributes:
        msg -- message
    """
    def __init__(self, filename, filepath, working_dir):
        self.name = filename
        self.filepath = filepath
        self.working_dir = working_dir
        
    def __str__(self):
        return "file '{0}' was not found (looked in '{1}' and '{2}')".format(self.name, self.filepath, self.working_dir)
