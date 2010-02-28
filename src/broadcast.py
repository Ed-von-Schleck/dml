from __future__ import print_function

import sinks

def broadcast():
    sinc_cos = [sink_func() for sink_func in sinks.sinks]
    for sink in sinc_cos:
        sink.next()
    while True:
        event_key_value = (yield)
        for sink in sinc_cos:
            sink.send(event_key_value)
