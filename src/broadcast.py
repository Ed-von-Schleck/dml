from __future__ import print_function

from collections import namedtuple

import sinks
import states

def broadcast():
    MySink = namedtuple("MySink", "mod cor filters")
    mysinks = []
    for sink_name in sinks.__all__:
        filters = []
        mod = sinks.__dict__[sink_name]
        cor = mod.sink()
        cor.next()
        number_of_filters = len(mod.filters)
        for i in range(number_of_filters):
            target = cor if i + 1 >= number_of_filters else mod.filters[i + 1]
            filter = mod.filters[i](target, mod.SHORTNAME)
            filter.next()
            filters.append(filter)
        mysinks.append(MySink(mod, cor, filters))

    state_machine = states.state_tracker()
    state = state_machine.next()
    while True:
        event, key, value = (yield)
        state = state_machine.send(event)
        closed_sinks = []
        for sink in mysinks:
            try:
                sink.filters[0].send((state, event, key, value))
            except StopIteration:
                sink.cor.close()
                for filter in sink.filters:
                    filter.close()
                closed_sinks.append(sink)
        if closed_sinks:
            for sink in closed_sinks:
                mysinks.remove(sink)
            closed_sinks = []
