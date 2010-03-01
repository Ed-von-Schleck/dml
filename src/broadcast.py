from __future__ import print_function

import sinks
import states

def broadcast():
    sinc_cos = [sink_func() for sink_func in sinks.sinks]
    for sink in sinc_cos:
        sink.next()
    state_machine = states.state_tracker()
    state = state_machine.next()
    while True:
        event, key, value = (yield)
        state = state_machine.send(event)
        closed_sinks = []
        for sink in sinc_cos:
            try:
                sink.send((state, event, key, value))
            except StopIteration:
                sink.close()
                closed_sinks.append(sink)
        if closed_sinks:
            for sink in closed_sinks:
                sinc_cos.remove(sink)
            closed_sinks = []
