# -*- coding: utf-8

from __future__ import print_function
from __future__ import unicode_literals

from os.path import exists, join

from src.dmlexceptions import DMLError
import src.constants as constants
import src.events as events

def macro(broadcaster, metadata, buffer, lexer):
    try:
        buffer.remove("\n")
    except ValueError:
        pass
    name = buffer.popleft()
    
    if exists(join(metadata["working_dir"], metadata["filepath"], name)):
        full_filename = join(metadata["working_dir"], metadata["filepath"], name)
    elif exists(join(metadata["working_dir"], name)):
        full_filename = join(metadata["working_dir"], name)
    else:
        raise DMLIncludeIOError(token,
            join(metadata["working_dir"], metadata["filepath"], tonameken),
            join(metadata["working_dir"], name))
    
    lexer.push_source(open(full_filename), full_filename)


class DMLIncludeSyntaxError(DMLError):
    """Exception raised if a syntax error in a include macro occurs

    Attributes:
    msg -- message
    """
    def __init__(self, filename, filepath, working_dir):
        self.error_name = "include syntax error"
        self.name = filename
        self.filepath = filepath
        self.working_dir = working_dir
        
    def __str__(self):
        return "file '{0}' was not found (looked in '{1}' and '{2}')".format(self.name, self.filepath, self.working_dir)

class DMLIncludeIOError(DMLError):
    """Exception raised if the file to be included does not exist

    Attributes:
    name -- the filename to be included
    filepath -- search path one
    working_dir -- search path two
    """
    def __init__(self, filename, filepath, working_dir):
        self.error_name = "include IO error"
        self.name = filename
        self.filepath = filepath
        self.working_dir = working_dir
        
    def __str__(self):
        return "file '{0}' was not found (looked in '{1}' and '{2}')".format(self.name, self.filepath, self.working_dir)
