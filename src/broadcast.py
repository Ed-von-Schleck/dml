# -*- coding: utf-8
"""
This coroutine gets the events from the parser and sends them, the
corresponding states, keys, and tokens to all sinks via the requested
filters.

Besides the main loop, this is really the heart of dml. It
 * tracks the current state (the parsing is oblivious of states)
 * sets up a list of all sinks
 * sets up filter chains for all sinks
 * sends state, event, key (or None) and token (or None) to the entrypoint
   in the filter chain (or to the sink directly if no filter is requested)
 * removes sinks out of the list where the sink or any of the filters
   stopped
"""

from __future__ import print_function
from __future__ import unicode_literals

from shutil import copyfile, move
import os.path
from collections import deque

from src.states import state_tracker
from src.grammar import states
from src.dmlexceptions import DMLStateTransitionError

stack = deque()

def state_change(last_state, state, send):
    if state in states[last_state][0]:
        stack.append(last_state)
        send((state, "start", None))
    elif stack:
        send((last_state, "end", None))
        pop_state = stack.pop()
        if pop_state != state:
            state_change(pop_state, state, send)    # to understand recursion ...
    else:
        send((last_state, "end", None))
        send((state, "start", None))

def broadcast(metadata, sinks):
    """
    the broadcast coroutine
    
    Arguments:
    metadata -- metadata about the input file
    sinks -- the sinks selected at the command line
    
    yields:
    event, key, name
    
    sends:
    state, event, key, name
    """
    state_machine = state_tracker()
    state_machine.next()
    state = "start"
    sms = state_machine.send
    
    try:
        while True:
            event, value = (yield)
            last_state = state
            try:
                state = states[state][1][event]
            except KeyError:
                raise DMLStateTransitionError(state, event)
            for sink in sinks:
                if sink.closed:
                    continue
                try:
                    if sink.filters:
                        send = sink.filters[0].send
                    else:
                        send = sink.cor.send

                    if last_state != state:
                        state_change(last_state, state, send)
                        
                    if event == "data":
                        send((state, "data", value))
                    elif event == "macro_data":
                        send((state, "macro_data", value))
                    
                # if the sink or any of the filters stops, we stop the whole chain
                except StopIteration:
                    sink.cor.close()
                    sink._replace(closed= True)
                    for myfilter in sink.filters:
                        myfilter.close()
            
    except GeneratorExit:
        pass
    finally:
        for sink in sinks:
            tmpfilename = sink.tmpfile.name
            sink.tmpfile.close()
            filename = os.path.join(metadata.working_dir, metadata.name + "." + sink.mod.EXTENSION)
            move(sink.tmpfile.name, filename)
            print("written", filename)
            
