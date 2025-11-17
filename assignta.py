'''
Authors: Cassandra Cinzori and Ian Solberg
File: assignta.py
Description: core TA assignment logic, data prep, objectives
'''

import numpy as np
import pandas as pd

# Data Loading Functions
def load_tas(filename = 'assignta_data/tas.csv'):
    tas_df = pd.read_csv(filename)
    return tas_df

def load_labs(filename = 'assignta_data/labs.csv'):
    labs_df = pd.read_csv(filename)
    return labs_df

def init_assignment(num_tas, num_labs):
    """
    Create an initial assignment of num_tas, num_labs (all start as 0)
    """
    return np.zeros((num_tas, num_labs), dtype=int)


# Objective Functions
def overallocation(assignment, tas_df):
    penalties = 0
    #TODO: add logic
    return penalties

def conflicts(assignment, labs_df):
    penalties = 0
    # TODO: add logic
    return penalties

def undersupport(assignment, labs_df):
    penalties = 0
    # TODO: add logic
    return penalties

def unavailable(assignment, tas_df):
    penalties = 0
    # TODO: add logic
    return penalties

def unpreferred(assignment, tas_df):
    penalties = 0
    # TODO: add logic
    return penalties

# Agent Functions
def random_agent(assignment, tas_df, labs_df):
    """Assign a random value (0 or 1) to one TA-lab pair"""
    new_assignment = assignment.copy()

    #TODO: write logic

    return new_assignment


def preference_agent(assignment, tas_df, labs_df):
    """Assign a TA to a lab they prefer"""
    new_assignment = assignment.copy()

    #TODO: write logic

    return new_assignment


def undersupport_agent(assignment, tas_df, labs_df):
    """Assign an available TA to an undersupported lab"""
    new_assignment = assignment.copy()

    #TODO: write logic

    return new_assignment

def conflict_remover_agent(assignment, tas_df, labs_df):
    """Removes a scheduling conflict"""
    new_assignment = assignment.copy()

    #TODO: write logic

    return new_assignment


# Main Function
def main():
    tas_df = load_tas('tas.csv')
    labs_df = load_labs('sections.csv')
    num_tas = len(tas_df)
    num_labs = len(labs_df)
    assignment = init_assignment(num_tas, num_labs)


    # Example Usage! --
    # Print objective scores for current assignment
   # print("Overallocation:", overallocation(assignment, tas_df))
   # print("Conflicts:", conflicts(assignment, labs_df))
   # print("Unavailable:", unavailable(assignment, tas_df))
   # print("Unpreferred:", unpreferred(assignment, tas_df))

if __name__ == '__main__':
    main()








