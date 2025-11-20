"""
Authors: Cassandra Cinzori and Ian Solberg
File: profiler.py
Description: A profiler calss that demonstrates use of decorates, static variables, and
             default dictionaries to support code profiling. In profiling our goal is to
             keep track of how often we call each function (that we are profiling) and
             the total elapsed time spent in that function and the average elapsed time per call.

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
    def report(output_file=None):
        """
        Summarize in a nicely formatted table: calls, total runtime
        and the time/call for each function we are profiling

        Parameters
        ----------
        output_file : str, optional
            If provided, write report to this file. Otherwise print to console.
        """

        # Build report lines
        lines = []
        lines.append("=" * 80)
        lines.append("PROFILING REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Calculate totals
        total_time = sum(Profiler.time.values())
        total_calls = sum(Profiler.calls.values())

        lines.append(f"Total Runtime: {total_time:.6f} seconds")
        lines.append(f"Total Function Calls: {total_calls}")
        lines.append("")

        # Report table header
        lines.append("Function              Calls     TotSec   Sec/Call")
        lines.append("-" * 60)

        # One row output per fucntion
        sorted_func = sorted(Profiler.calls.items(),
                             key=lambda x: Profiler.time[x[0]],
                             reverse=True)

        for name, num in sorted_func:
            sec = Profiler.time[name]
            lines.append(f'{name:20s} {num:6d} {sec:10.6f} {sec / num:10.6f}')

        lines.append("-" * 60)
        lines.append("")

        # Verification for 5 min time limit
        if total_time <=300:
            lines.append(f"✅ VERIFICATION: Runtime {total_time:.4f}s  <= 300s (5 minutes)")
        else:
            lines.append(f"❌ WARNING: Runtime {total_time:.4f}s > 300s (exceeds the time limti)")


        lines.append("=" * 80)

        # Output
        report_text = "/n".join(lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)
            print(f"Profiling report written to {output_file}")
        else:
            print(report_text)

        return report_text

    @staticmethod
    def reset():
        """
        Clear all profiling data
        """
        Profiler.calls.clear()
        Profiler.time.clear()







