"""
Authors: Cassandra Cinzori and Ian Solberg
File: assignta.py
Description: core TA assignment logic, data prep, objectives
"""

import numpy as np
import pandas as pd
from evo import Evo
from profiler import profile
from collections import defaultdict


class AssignTa:
    def __init__(self):
        self.ta = None
        self.lab = None
        self.assignment = None
        self.unavail = None
        self.willing = None
        self.prefer = None

    # ==== Initialization // Helpers

    def _load_data(self, fp: str) -> pd.DataFrame:
        return pd.read_csv(fp)

    def assign_ta_df(self, fp: str):
        self.ta = self._load_data(fp)

    def assign_lab_df(self, fp: str):
        self.lab = self._load_data(fp)

    def zeros(self) -> np.array:
        """
        Create an initial assignment of num_tas, num_labs (all start as 0)
        """
        num_tas = len(self.ta)
        num_labs = len(self.lab)
        return np.zeros((num_tas, num_labs), dtype=int)

    def get_preference_masks(self):
        """
        returns preference masks - helper function for objectives
        """
        ta_working = self.ta.drop(columns=["ta_id", "name", "max_assigned"])
        values = ta_working.values
        # Create Mask
        self.unavail = (values == "U").astype(int)
        self.willing = (values == "W").astype(int)
        self.prefer = (values == "P").astype(int)

    def get_conflict_pairs(self, assignment: np.array) -> list:
        all_conflicts = []
        all_lab_times = self.lab["daytime"].values  # Direct numpy array from pandas
        ta_indices, lab_indices = np.where(assignment == 1)
        assigned_times = all_lab_times[lab_indices]
        for ta_idx in np.unique(ta_indices):
            ta_mask = ta_indices == ta_idx
            ta_labs = lab_indices[ta_mask]
            ta_times = assigned_times[ta_mask]
            unique_times, inverse, counts = np.unique(
                ta_times, return_inverse=True, return_counts=True
            )
            conflicting_time_mask = counts > 1
            if not conflicting_time_mask.any():
                continue
            for time_idx in np.where(conflicting_time_mask)[0]:
                conflict_mask = inverse == time_idx
                conflicting_labs = ta_labs[conflict_mask]
                conflict_locations = [(ta_idx, lab_idx) for lab_idx in conflicting_labs]
                all_conflicts.extend(conflict_locations)
        return all_conflicts

    # ==== Objective Functions

    def overallocation(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.
        tas_df : pd.DataFrame
            DataFrame containing TA information, including the 'max_assigned' column.
        Returns
        -------
        int
            Total overallocation penalty.
        Description
        -----------
        Minimize the total overallocation penalty across all TAs.

        ```
        Each TA specifies how many labs they can support (max_assigned column in tas.csv).
        If a TA requests at most 2 labs and you assign to them 5 labs, that’s an overallocation penalty of 3.
        Compute the objective by summing the overallocation penalty over all TAs.
        There is no minimum allocation
        ```
        """
        per_ta_total_assignments = assignment.sum(axis=1)
        per_ta_maximum_assignments = self.ta["max_assigned"].values
        penalty = np.maximum(
            per_ta_total_assignments - per_ta_maximum_assignments, 0
        ).sum()  # Takes the element-wise maximum between the difference and 0 (Clips negative sums to 0- no penalty for under allocation)
        return penalty

    def conflicts(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.
        labs_df : pd.DataFrame
            DataFrame containing lab information, including the 'daytime' column.
        Returns
        -------
        int
            Total number of TAs with time conflicts.
             A time conflict occurs if you assign a TA to two labs meeting at the same time.
             If a TA has multiple time conflicts, still count that as one overall time conflict for that TA.
        """
        conflict_pairs = self.get_conflict_pairs(assignment)
        penalty = len(set(ta_idx for ta_idx, lab_idx in conflict_pairs))
        return penalty

    def undersupport(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.
        labs_df : pd.DataFrame
            DataFrame containing lab information, including the 'min_ta' column.
        Returns
        -------
        int
            Total undersupport penalty.
             If a section needs at least 3 TAs and you only assign 1, count that as 2 penalty points.
             Minimize the total penalty score across all sections. There is no penalty for assigning too many TAs.
        """
        assigned_tas = assignment.sum(axis=0)  # Number of TAs assigned per lab
        required_tas = self.lab["min_ta"].values  # Minimum TAs needed per lab
        penalty = np.maximum(required_tas - assigned_tas, 0).sum()
        return penalty

    def unavailable(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.
        tas_df : pd.DataFrame
            DataFrame containing TA information, including their availability preferences.
        Returns
        -------
        int
            Total number of times TAs are assigned to sections they are unavailable for.
        """
        assigned_but_unavailable = (self.unavail == 1) & (assignment == 1)
        penalty = np.sum(assigned_but_unavailable)
        return penalty

    def unpreferred(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.
        tas_df : pd.DataFrame
            DataFrame containing TA information, including their preference levels.
        Returns
            int: Minimize the number of times you allocate a TA to a section where they said “willing” but not “preferred”. (unpreferred).
                In effect, we are trying to assign TAs to sections that they prefer. But we want to frame every objective a minimization objective.
                So, if your solution score has unwilling=0 and unpreferred=0, then all TAs are assigned to sections they prefer!
        """
        assigned_not_preferred = (self.willing == 1) & (assignment == 1)
        penalty = np.sum(assigned_not_preferred)
        return penalty

    # ==== Agent Functions

    def random_flip_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign a random value (0 or 1) to one TA-lab pair"""
        new_assignment = assignment.copy()
        ta_idx = np.random.choice(assignment.shape[0])
        lab_idx = np.random.choice(assignment.shape[1])
        if new_assignment[ta_idx, lab_idx] == 1:
            new_assignment[ta_idx, lab_idx] = 0
        else:
            new_assignment[ta_idx, lab_idx] = 1
        return new_assignment

    def preference_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign a TA to a lab they prefer"""
        new_assignment = assignment.copy()
        ta_idx = np.random.choice(assignment.shape[0])
        unassigned_preferred = (self.prefer[ta_idx] == 1) & (assignment[ta_idx] == 0)
        available_labs = np.where(unassigned_preferred)[0]
        lab_idx = np.random.choice(available_labs)
        new_assignment[lab_idx, ta_idx] = 1
        return new_assignment

    def undersupport_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign an available TA to an undersupported lab"""
        new_assignment = assignment.copy()
        allocated_per_lab = assignment.sum(axis=0)
        required_per_lab = self.lab["min_ta"].values
        undersupport = np.maximum(required_per_lab - allocated_per_lab, 0)
        max_undersupport = undersupport.max()
        if max_undersupport == 0:
            return new_assignment  # No undersupported labs
        most_undersupported_labs = np.where(undersupport == max_undersupport)[
            0
        ]  # handles ties
        lab_idx = np.random.choice(most_undersupported_labs)  # breaks ties
        available_tas = (self.unavail[:, lab_idx] == 0) & (assignment[:, lab_idx] == 0)
        available_ta_indices = np.where(available_tas)[0]
        if len(available_ta_indices) == 0:
            return new_assignment  # No available TAs for this lab
        lab_time = self.lab["daytime"].values[lab_idx]
        all_lab_times = self.lab["daytime"].values
        conflict_free_tas = []
        for ta_idx in available_ta_indices:
            # Get this TA's currently assigned labs
            assigned_labs = np.where(assignment[ta_idx] == 1)[0]
            assigned_times = all_lab_times[assigned_labs]
            if lab_time not in assigned_times:
                conflict_free_tas.append(ta_idx)
        if len(conflict_free_tas) == 0:
            return new_assignment
        ta_idx = np.random.choice(conflict_free_tas)
        new_assignment[ta_idx, lab_idx] = 1

        return new_assignment

    def conflict_remover_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Removes a scheduling conflict"""
        new_assignment = assignment.copy()
        conflicts = self.get_conflict_pairs()
        choice = np.random.choice((conflicts))
        ta_idx, lab_idx = choice
        new_assignment[lab_idx, ta_idx] = 0
        return new_assignment


# ==== Main
def main():
    # Init
    evo = Evo()
    a = AssignTa()
    a.assign_ta_df("assignta_data/tas.csv")
    a.assign_lab_df("assignta_data/sections.csv")
    a.assignment = a.zeros()

    # Debugs
    print(f"Matrix Size: {a.assignment.size}")
    print(f"Num TAs: {len(a.ta)}")
    print(f"Number of Sections: {a.lab['section'].count()}")
    u, w, p = a.get_preference_masks()
    print(u)
    print(u.size)
    print(w)
    print(w.size)
    print(p)
    print(p.size)

    # Task1
    """
    1. Minimize overallocation of TAs (overallocation): 
    Each TA specifies how many labs they can support (max_assigned column in tas.csv). 
    If a TA requests at most 2 labs and you assign to them 5 labs, that’s an overallocation penalty of 3. 
    Compute the objective by summing the overallocation penalty over all TAs. There is no minimum allocation.
    """
    print("Starting Task 1")
    task1_evolution = Evo()
    # TODO implement evolution for task 1

    print("Task 1 Complete")
    # Task 2
    """
    Minimize time conflicts (conflicts): 
    Minimize the number of TAs with one or more time conflicts. 
    A time conflict occurs if you assign a TA to two labs meeting at the same time. 
    If a TA has multiple time conflicts, still count that as one overall time conflict for that TA.
    """
    print("Starting Task 2")
    task2_evolution = Evo()
    # TODO implement evolution for task 2
    print("Task 2 Complete")

    # Task 3
    """
    Minimize Under-Support (undersupport): 
    If a section needs at least 3 TAs and you only assign 1, count that as 2 penalty points.
    Minimize the total penalty score across all sections. There is no penalty for assigning too many TAs. 
    You can never have enough TAs.
    """

    print("Starting Task 3")
    task3_evolution = Evo()
    # TODO implement evolution for task 3
    print("Task 3 Complete")

    # Task 4
    """
    Minimize the number of times you allocate a TA to a section they are unavailable to support (unavailable). 
    You could argue this is really a hard constraint, but we will treat it as an objective to be minimized instead.
    """
    print("Starting Task 4")
    task4_evolution = Evo()
    # TODO implement evolution for task 4
    print("Task 4 Complete")

    # Task 5
    """
    Minimize the number of times you allocate a TA to a section where they said “willing” but not “preferred”. (unpreferred). 
    In effect, we are trying to assign TAs to sections that they prefer. But we want to frame every objective a minimization objective. 
    So, if your solution score has unwilling=0 and unpreferred=0, then all TAs are assigned to sections they prefer! Good job!
    """

    print("Starting Task 5")
    task5_evolution = Evo()
    # TODO implement evolution for task 5
    print("Task 5 Complete")


if __name__ == "__main__":
    main()
