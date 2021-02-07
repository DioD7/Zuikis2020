from functools import wraps
from time import perf_counter

##
#Utilities
##


def time_it(func):
    """Wraps func such that it returns func result as well as calculation time"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        time = perf_counter() - start
        return result, time
    return wrapped


def timer(f, prec = 4):
    """Wraps f such that calculation time is printed after execution"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        start_time = perf_counter()
        rez = f(*args, *kwargs)
        time = perf_counter() - start_time
        print('[Finished in','{:.' + str(prec) + 'f}'.format(time),'s]')
        return rez
    return wrapped


class Timer():
    """Timer class"""
    def __init__(self):
        self.time = perf_counter()
        self.init_time = self.time

    def start(self):
        """Starts timer"""
        self.time = perf_counter()

    def get_time(self):
        """Returns time from the last inquiry into Timer and resets internal time"""
        t = perf_counter()-self.time
        self.time = perf_counter()
        return t

    def get_total_time(self):
        return perf_counter() - self.init_time

    def output(self, msg):
        print('[{}'.format(msg),'{:.4f}'.format(self.get_time()),'s]')