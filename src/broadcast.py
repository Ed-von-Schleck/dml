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

from src.grammar import states
from src.dmlexceptions import DMLStateTransitionError

def broadcast(metadata, sinks):
    """
    the broadcast coroutine
    
    Arguments:
    metadata -- metadata about the input file
    sinks -- the sinks selected at the command line
    
    yields:
    parser_event, token (or None)
    
    sends:
    state, event, token
    """
    state = "start"
    data = intern(b"data")
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
                    send = sink.cor.send

                    if last_state != state:
                        if state in states[last_state][0]:
                            # the new state is child of the last one
                            send((state, b"start", None))
                        elif last_state in states[state][0]:
                            # the new state is parent of the last one
                            send((last_state, b"end", None))
                        else:
                            send((last_state, b"end", None))
                            send((state, b"start", None))
                        
                    if event is data:
                        send((state, b"data", value))
                    elif event == b"macro_data":
                        send((state, b"macro_data", value))
                    
                # if the sink or any of the filters stops, we stop the whole chain
                except StopIteration:
                    sink.cor.close()
                    sink._replace(closed=True)
            
    except GeneratorExit:
        pass
    finally:
        for sink in sinks:
            tmpfilename = sink.tmpfile.name
            sink.tmpfile.close()
            filename = os.path.join(metadata.working_dir, metadata.name + "." + sink.mod.EXTENSION)
            move(sink.tmpfile.name, filename)
            print("written", filename)
            
