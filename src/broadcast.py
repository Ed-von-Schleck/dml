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
        for sink in sinc_cos:
            sink.send((state, event, key, value))
