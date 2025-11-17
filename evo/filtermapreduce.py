"""
Examples of functional programming using map, filter, and reduce.
Author: Ian Solberg
"""

# === Example filter Usage ====


def even(x):
    return x % 2 == 0


vals = list(range(10))

# val_even = [x for x in val if x % 2 == 0]  # list comprehension
vals_even = list(filter(even, vals))  # filter
# vals_even = list(filter(lambda x: x % 2 == 0)) # lambda function

print(vals)
print(vals_even)

# ===== map example =====

cubes = list(map(lambda x: x**3, vals))

print(cubes)


# ==== Reduce Example =====
from functools import reduce
from collections import defaultdict

# 1, 2, 3, 4, 5, 6
total = reduce(lambda x, y,: x + y, vals)
print(total)

dna_sequence = "atcgtcgatagctgcatgctagctcgtatatttcgcatgctagctagcgcggccctctagctagctagtacgcgcgcgtcagctagcatgctagtcgatc"


def reducer(acc, base):

    acc[base] += 1
    return acc


result = reduce(reducer, dna_sequence, defaultdict(int))
print(result)
