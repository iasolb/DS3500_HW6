"""
Authors: Cassandra Cinzori and Ian Solberg
File: assignta.py
Description: core TA assignment logic, data prep, objectives
"""

import numpy as np
import pandas as pd
from bokeh.colors.named import peachpuff

# TODO: see if tas.csv runs because it is not running for me

# Data Loading Functions
def load_tas(filename="assignta_data/tas.csv"):
    tas_df = pd.read_csv(filename)
    return tas_df


def load_labs(filename="assignta_data/sections.csv"):
    labs_df = pd.read_csv(filename)
    return labs_df


def init_assignment(num_tas, num_labs):
    """
    Create an initial assignment of num_tas, num_labs (all start as 0)
    """
    return np.zeros((num_tas, num_labs), dtype=int)

#--------------------------------------------------------------
# Objective Functions
def overallocation(assignment, tas_df):
    """
    Each TA specifies how many labs they can support (max_assigned column in tas.csv).
    If a TA requests at most 2 labs and you assign to them 5 labs, that’s an overallocation penalty of 3.
    Compute the objective by summing the overallocation penalty over all TAs.
    There is no minimum allocation
    """
    assigned = assignment.sum(axis=1)  # Number of labs assigned to each TA
    max_labs = tas_df['max_assigned'].values  # Allowed labs per TA
    penalties = np.maximum(assigned - max_labs, 0).sum()
    return penalties


def conflicts(assignment, labs_df):
    """
    Minimize the number of TAs with one or more time conflicts.
    A time conflict occurs if you assign a TA to two labs meeting at the same time.
    If a TA has multiple time conflicts, still count that as one overall time conflict for that TA.
    """
    penalties = 0
    lab_time = labs_df['daytime']  # Lab meeting times
    for assigned_row in assignment:
        assigned_lab_indices = np.where(assigned_row == 1)[0]  # Assigned lab
        times = lab_time[assigned_lab_indices]   # Lab time
        if len(times) != len(set(times)) and len(times) > 0:
            penalties += 1
        return penalties



def undersupport(assignment, labs_df):
    """
    If a section needs at least 3 TAs and you only assign 1, count that as 2 penalty points.
    Minimize the total penalty score across all sections.
    There is no penalty for assigning too many TAs.
    You can never have enough TAs.
    """
    assigned = assignment.sum(axis=0)  # Number of TAs assigned per lab
    required = labs_df['min_ta'].values  # Minimum TAs needed per lab
    penalties = np.maximum(required - assigned, 0).sum()
    return penalties


def unavailable(assignment, tas_df):
    """
    Minimize the number of times you allocate a TA to a section they are unavailable to support (unavailable).
    You could argue this is really a hard constraint, but we will treat it as an objective to be minimized instead.
    """
    pref_matrix = tas_df.loc[:, [str(i) for i in range(assignment.shape[1])]].values   # TA preferences
    mask = (pref_matrix == "U") & (assignment == 1)  # True when TAs are unavailable and assigned
    penalties = np.sum(mask)
    return penalties


def unpreferred(assignment, tas_df):
    """
    Minimize the number of times you allocate a TA to a section where they said “willing” but not “preferred”. (unpreferred).
    In effect, we are trying to assign TAs to sections that they prefer.
    But we want to frame every objective a minimization objective.
    So, if your solution score has
    unwilling=0
    unpreferred=0
    """
    pref_matrix = tas_df.loc[:, [str(i) for i in range(assignment.shape[1])]].values  # TA preferences
    mask = (pref_matrix == 'W') & (assignment == 1)   # True when TAs are willing and assigned
    penalties = np.sum(mask)
    return penalties


#--------------------------------------------------------------
# Agent Functions
def random_agent(assignment, tas_df, labs_df):
    """Assign a random value (0 or 1) to one TA-lab pair"""
    new_assignment = assignment.copy()

    # TODO: write logic

    return new_assignment


def preference_agent(assignment, tas_df, labs_df):
    """Assign a TA to a lab they prefer"""
    new_assignment = assignment.copy()

    # TODO: write logic

    return new_assignment


def undersupport_agent(assignment, tas_df, labs_df):
    """Assign an available TA to an undersupported lab"""
    new_assignment = assignment.copy()

    # TODO: write logic

    return new_assignment


def conflict_remover_agent(assignment, tas_df, labs_df):
    """Removes a scheduling conflict"""
    new_assignment = assignment.copy()

    # TODO: write logic

    return new_assignment

#--------------------------------------------------------------
# Main Function
def main():
    tas_df = load_tas("tas.csv")
    labs_df = load_labs("sections.csv")
    num_tas = len(tas_df)
    num_labs = len(labs_df)
    assignment = init_assignment(num_tas, num_labs)

    # Example Usage! --
    # Print objective scores for current assignment

    print("Overallocation:", overallocation(assignment, tas_df))
    print("Conflicts:", conflicts(assignment, labs_df))
    print("Unavailable:", unavailable(assignment, tas_df))
    print("Unpreferred:", unpreferred(assignment, tas_df))

if __name__ == "__main__":
    main()
