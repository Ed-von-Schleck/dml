# -*- coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple

from src.dmlexceptions import DMLStateTransitionError
from src.grammar import states

def state_tracker():
    state = "start"
    while True:
        event = (yield state)
        
