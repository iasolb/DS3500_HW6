"""
Authors: Cassandra Cinzori and Ian Solberg
File: assignta.py
Description: core TA assignment logic, data prep, objectives
"""

import numpy as np
import pandas as pd
from evo import Evo
from profiler import profile


class AssignTa:
    def __init__(self):
        self.ta = None
        self.lab = None
        self.assignment = None

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

    def get_preference_masks(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        returns preference masks - helper function for objectives
        """
        ta_working = self.ta.drop(columns=["ta_id", "name", "max_assigned"])
        values = ta_working.values
        # Create Mask
        unavailable = (values == "U").astype(int)
        willing = (values == "W").astype(int)
        preferred = (values == "P").astype(int)

        return unavailable, willing, preferred

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

        per_ta_total_assignments = assignment.sum(
            axis=1
        )  # Number of labs assigned to each TA
        per_ta_maximum_labs = self.ta["max_assigned"].values  # Allowed labs per TA
        penalty = np.maximum(
            per_ta_total_assignments - per_ta_maximum_labs, 0
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
        penalty = 0
        lab_time = self.lab["daytime"]  # Lab meeting times
        for assigned_row in assignment:
            assigned_lab_indices = np.where(assigned_row == 1)[0]  # Assigned lab
            times = lab_time[assigned_lab_indices]  # Lab time
            if len(times) != len(set(times)) and len(times) > 0:
                penalty += 1
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
        assigned = assignment.sum(axis=0)  # Number of TAs assigned per lab
        required = self.lab["min_ta"].values  # Minimum TAs needed per lab
        penalty = np.maximum(required - assigned, 0).sum()
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
        unavailable, _, _ = self.get_preference_masks()
        mask = (unavailable == 1) & (assignment == 1)
        penalty = np.sum(mask)
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
            int:    Each TA specifies how many labs they can support (max_assigned column in tas.csv).
                    If a TA requests at most 2 labs and you assign to them 5 labs, that’s an overallocation penalty of 3.
                    Compute the objective by summing the overallocation penalty over all TAs.
        """
        _, willing, _ = self.get_preference_masks()
        mask = (willing == 1) & (assignment == 1)
        penalty = np.sum(mask)
        return penalty

    # ==== Agent Functions

    def random_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign a random value (0 or 1) to one TA-lab pair"""
        new_assignment = assignment.copy()

        # Assign a random value (0 or 1) to one TA-lab pair

        return new_assignment

    def preference_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign a TA to a lab they prefer"""
        new_assignment = assignment.copy()
        _, _, preferred = self.get_preference_masks()
        # TODO: write logic
        # random choice ta
        # get all preferred labs (that are not assigned already)
        # pick a random object from that list
        # flip to 1
        # return new assignment matrix
        return new_assignment

    def undersupport_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Assign an available TA to an undersupported lab"""
        new_assignment = assignment.copy()

        # TODO: write logic

        return new_assignment

    def conflict_remover_agent(self, assignment: np.ndarray) -> np.ndarray:
        """Removes a scheduling conflict"""
        new_assignment = assignment.copy()

        # TODO: write logic

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
