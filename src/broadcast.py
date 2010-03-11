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

from src.states import state_tracker
from src.constants import events, states, sink_events

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
    state = states.START
    sms = state_machine.send
    try:
        while True:
            event, value = (yield)
            last_state = state
            state = sms(event)
            for sink in sinks:
                if sink.closed:
                    continue
                try:
                    if sink.filters:
                        send = sink.filters[0].send
                    else:
                        send = sink.cor.send

                    if last_state != state:
                        send((last_state, sink_events.END, None))
                        send((state, sink_events.START, None))
                    if event == events.DATA:
                        send((state, sink_events.DATA, value))
                    elif event == events.MACRO_DATA:
                        send((state, sink_events.MACRO_DATA, value))
                    
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
            print("written",filename)
            move(sink.tmpfile.name, filename)
            
