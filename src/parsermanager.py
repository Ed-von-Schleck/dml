from contextlib import contextmanager

@contextmanager
def parser_manager(coroutine, *args, **kwargs):
    c = coroutine(*args, **kwargs)
    c.next()
    try:
        yield c.send
    except StopIteration:
        pass
    finally:
        c.close()
        
