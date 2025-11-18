"""
profiler.py

A profiler calss that demonstrates use of decorates, static variables, and
default dictionaries to support code profiling.    In profiling our goal
is to keep track of how often we call each function (that we are profiling)
and the total elapsed time spent in that function and the
average elapsed time per call.

ITS ALL ABOUT "EFFICIENCY"  (AN IMPORTANT SOFTWARE GOAL)!!!

"""
from collections import defaultdict
import time


def profile(f):
    """ Convenience function to make decorator tags simpler
    e.g., @profile instead of @Profiler.profile """
    return Profiler.profile(f)


class Profiler:

    # class (shared) variables
    calls = defaultdict(int)  # function name --> # of calls (default 0)
    time = defaultdict(float) # function name --> total elapsed time (default 0.0)

    @staticmethod
    def profile(f):
        def wrapper(*args, **kwargs):
            start = time.time_ns()
            val = f(*args, **kwargs)
            elapsed = (time.time_ns() - start) / 10**9   # converting nanosec to sec

            fname = str(f).split()[1] # extracting the function name
            Profiler.calls[fname] += 1  # increment the call count
            # D[key] += value
            # D[key] = D[key] + value  (key error in standard dictionaries)

            Profiler.time[fname] += elapsed # accumulate the total elapsed time
            return val

        return wrapper


    @staticmethod
    def report():
        """ Summarize in a nicely formatted table: calls, total runtime
        and the time/call for each function we are profiling """

        # Report table header
        print("Function              Calls     TotSec   Sec/Call")

        # One row output per function
        for name, num in Profiler.calls.items():
            sec = Profiler.time[name] # fetch total elapsed time for that func
            print(f'{name:20s} {num:6d} {sec:10.6f} {sec / num:10.6f}')




    



