from functools import wraps
from time import perf_counter

def time_it(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        time = perf_counter() - start
        return result, time
    return wrapped


def timer(f, prec = 4):
    @wraps(f)
    def wrapped(*args, **kwargs):
        start_time = perf_counter()
        rez = f(*args, *kwargs)
        time = perf_counter() - start_time
        print('[Finished in','{:.' + str(prec) + 'f}'.format(time),'s]')
        return rez
    return wrapped


class Timer():
    def __init__(self):
        self.time = perf_counter()

    def start(self):
        self.time = perf_counter()

    def get_time(self):
        return perf_counter()-self.time
