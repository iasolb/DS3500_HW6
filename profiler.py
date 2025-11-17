'''
Authors: Cassandra Cinzori and Ian Solberg
File: profiler.py
Description: profiling decorators/utilities
'''

import numpy as np
import pandas as pd

# Data Loading Functions
def load_tas(filename = 'assignta_data/tas.csv'):
    tas_df = pd.read_csv(filename)
    return tas_df

def load_labs(filename = '../assignta_data/labs.csv'):
    labs_df = pd.read_csv(filename)
    return labs_df

def init_assignment(num_tas, num_labs):
    """
    Create an initial assignment of num_tas, num_labs (all start as 0)
    """
    return np.zeros((num_tas, num_labs), dtype=int)


# Objective Functions


def main():
    tas_df = load_tas('tas.csv')
    labs_df = load_labs('sections.csv')
    num_tas = len(tas_df)
    num_labs = len(labs_df)
    assignment = init_assignment(num_tas, num_labs)

    print(tas_df)

    # Example: Print objective scores for current assignment
    print("Overallocation:", overallocation(assignment, tas_df))
    print("Conflicts:", conflicts(assignment, labs_df))
    print("Undersupport:", undersupport(assignment, labs_df))
    print("Unavailable:", unavailable(assignment, tas_df))
    print("Unpreferred:", unpreferred(assignment, tas_df))

if __name__ == '__main__':
    main()






























