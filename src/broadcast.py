from __future__ import print_function

from collections import namedtuple

import sinks
import states

def broadcast(path, filename):
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
    MySink = namedtuple("MySink", "mod cor filters")
    mysinks = []
    for sink_name in sinks.__all__:
        filters = []
        mod = sinks.__dict__[sink_name]
        cor = mod.sink(path, filename)
        cor.next()
        number_of_filters = len(mod.filters)
        for i in range(number_of_filters):
            target = cor if i + 1 >= number_of_filters else mod.filters[i + 1]
            filter = mod.filters[i](target, mod.SHORTNAME)
            filter.next()
            filters.append(filter)
        mysinks.append(MySink(mod, cor, filters))

    state_machine = states.state_tracker()
    sms = state_machine.send
    state = state_machine.next()
    while True:
        event, key, value = (yield)
        state = sms(event)
        #print(".", end="")
        closed_sinks = []
        for sink in mysinks:
            try:
                if sink.filters:
                    sink.filters[0].send((state, event, key, value))
                else:
                    sink.cor.send((state, event, key, value))
            # if the sink or any of the filters stops, we stop the whole chain
            except StopIteration:
                sink.cor.close()
                for filter in sink.filters:
                    filter.close()
                closed_sinks.append(sink)
        # garbage collection
        if closed_sinks:
            for sink in closed_sinks:
                mysinks.remove(sink)
            closed_sinks = []
