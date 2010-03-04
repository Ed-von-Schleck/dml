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

from collections import namedtuple
from tempfile import NamedTemporaryFile
from shutil import copyfile, move
import os.path

import sinks
import src.states as states
import src.constants as constants
import src.events as events

def broadcast(metadata):
    """
    the broadcast coroutine
    
    Arguments:
    metadata -- metadata about the input file
    
    yields:
    event, key, name
    
    sends:
    state, event, key, name
    """
    MySink = namedtuple("MySink", "mod cor filters tmpfile closed")
    mysinks = []

    state_machine = states.state_tracker()
    state = state_machine.next()
    sms = state_machine.send
    try:
        while True:
            if state == states.START:   # This is a message for the broadcaster
                event, key, value = (yield)
                state = sms(event)
                if event == events.CMD_LINE_OPTION and key == constants.OUTPUT:
                    mod = sinks.__dict__[value]
                    tmpfile = NamedTemporaryFile(mode="w", delete=False)
                    cor = mod.sink(metadata, tmpfile)
                    cor.next()
                    number_of_filters = len(mod.filters)
                    myfilters = []
                    for i in range(number_of_filters):
                        target = cor if i + 1 >= number_of_filters else mod.filters[i + 1]
                        myfilter = mod.filters[i](target, mod.SHORTNAME)
                        myfilter.next()
                        myfilters.append(myfilter)
                    mysinks.append(MySink(mod, cor, myfilters, tmpfile, False))
            else:
                break
        while True:         # Now comes everything after state 'Start'
            for sink in mysinks:
                if sink.closed:
                    continue
                try:
                    if sink.filters:
                        sink.filters[0].send((state, event, key, value))
                    else:
                        sink.cor.send((state, event, key, value))
                # if the sink or any of the filters stops, we stop the whole chain
                except StopIteration:
                    sink.cor.close()
                    sink._replace(closed= True)
                    for myfilter in sink.filters:
                        myfilter.close()
            event, key, value = (yield)
            state = sms(event)
    except GeneratorExit:
        pass
    finally:
        for sink in mysinks:
            tmpfilename = sink.tmpfile.name
            sink.tmpfile.close()
            filename = os.path.join(metadata["working_dir"], metadata["name"] + "." + sink.mod.EXTENSION)
            print("written",filename)
            move(sink.tmpfile.name, filename)
            
