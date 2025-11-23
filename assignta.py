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

        # Cached values
        self.unavail = None
        self.willing = None
        self.prefer = None
        self.max_assigned = None
        self.min_ta = None
        self.lab_times = None

        # Conflict caching
        self._conflict_cache = {}

    # ==== Initialization // Helpers

    def _load_data(self, fp: str) -> pd.DataFrame:
        return pd.read_csv(fp)

    def assign_ta_df(self, fp: str):
        self.ta = self._load_data(fp)
        self.max_assigned = self.ta["max_assigned"].values
        self.get_preference_masks()

    def assign_lab_df(self, fp: str):
        self.lab = self._load_data(fp)
        self.min_ta = self.lab["min_ta"].values
        self.lab_times = self.lab["daytime"].values

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
        self.unavail = (values == "U").astype(int)
        self.willing = (values == "W").astype(int)
        self.prefer = (values == "P").astype(int)

    @profile
    def get_conflict_count(self, assignment: np.array) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total number of TAs with time conflicts.

        Description
        -----------
        Optimized version with caching that only counts TAs with conflicts without building the full conflict list.
        """
        # Create hashable key from assignment
        key = assignment.tobytes()

        # Check cache first
        if key in self._conflict_cache:
            return self._conflict_cache[key]

        # Calculate conflicts
        ta_indices, lab_indices = np.where(assignment == 1)

        if len(ta_indices) == 0:
            self._conflict_cache[key] = 0
            return 0

        assigned_times = self.lab_times[lab_indices]
        tas_with_conflicts = set()

        for ta_idx in np.unique(ta_indices):
            ta_mask = ta_indices == ta_idx
            ta_times = assigned_times[ta_mask]

            if len(ta_times) != len(np.unique(ta_times)):
                tas_with_conflicts.add(ta_idx)

        result = len(tas_with_conflicts)
        self._conflict_cache[key] = result
        return result

    @profile
    def get_conflict_pairs(self, assignment: np.array) -> list:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        list
            List of (ta_idx, lab_idx) tuples representing all conflicting assignments.

        Description
        -----------
        Returns actual conflict locations. Only used by conflict_remover_agent where specific conflict pairs are needed.
        """
        ta_indices, lab_indices = np.where(assignment == 1)

        if len(ta_indices) == 0:
            return []

        assigned_times = self.lab_times[lab_indices]
        all_conflicts = []

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
    @profile
    def overallocation(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total overallocation penalty.

        Description
        -----------
        Minimize the total overallocation penalty across all TAs.
        Each TA specifies how many labs they can support (max_assigned column in tas.csv).
        If a TA requests at most 2 labs and you assign to them 5 labs, that's an overallocation penalty of 3.
        Compute the objective by summing the overallocation penalty over all TAs.
        There is no minimum allocation.
        """
        per_ta_total_assignments = assignment.sum(axis=1)
        penalty = np.maximum(per_ta_total_assignments - self.max_assigned, 0).sum()
        return penalty

    @profile
    def conflicts(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total number of TAs with time conflicts.

        Description
        -----------
        A time conflict occurs if you assign a TA to two labs meeting at the same time.
        If a TA has multiple time conflicts, still count that as one overall time conflict for that TA.
        """
        return self.get_conflict_count(assignment)

    @profile
    def undersupport(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total undersupport penalty.

        Description
        -----------
        If a section needs at least 3 TAs and you only assign 1, count that as 2 penalty points.
        Minimize the total penalty score across all sections. There is no penalty for assigning too many TAs.
        """
        assigned_tas = assignment.sum(axis=0)
        penalty = np.maximum(self.min_ta - assigned_tas, 0).sum()
        return penalty

    @profile
    def unavailable(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total number of times TAs are assigned to sections they are unavailable for.
        """
        penalty = np.sum((self.unavail == 1) & (assignment == 1))
        return penalty

    @profile
    def unpreferred(self, assignment: np.ndarray) -> int:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        int
            Total number of times TAs are assigned to willing but not preferred sections.

        Description
        -----------
        Minimize the number of times you allocate a TA to a section where they said "willing" but not "preferred" (unpreferred).
        In effect, we are trying to assign TAs to sections that they prefer. But we want to frame every objective a minimization objective.
        So, if your solution score has unwilling=0 and unpreferred=0, then all TAs are assigned to sections they prefer!
        """
        penalty = np.sum((self.willing == 1) & (assignment == 1))
        return penalty

    @profile
    def aggregate_objective(self, assignment: np.ndarray) -> float:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs.

        Returns
        -------
        float
            Weighted total penalty score.

        Description
        -----------
        Aggregate objective function with weighted penalties. Hard constraints heavily penalized.
        Lower scores are better - helps organize solutions list.
        """
        return (
            10 * self.overallocation(assignment)  # Medium priority
            + 100 * self.conflicts(assignment)  # HARD constraint
            + 10 * self.undersupport(assignment)  # Medium priority
            + 1000 * self.unavailable(assignment)  # HARD constraint
            + 1 * self.unpreferred(assignment)  # Soft preference
        ) / 100

    # ==== Agent Functions
    @profile
    def random_flip_agent(self, assignment: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        np.ndarray
            Modified assignment array with one TA-lab pair flipped.

        Description
        -----------
        Randomly select one TA-lab pair and flip its assignment value (0 to 1 or 1 to 0).
        """
        new_assignment = assignment.copy()
        ta_idx = np.random.choice(assignment.shape[0])
        lab_idx = np.random.choice(assignment.shape[1])
        new_assignment[ta_idx, lab_idx] = 1 - new_assignment[ta_idx, lab_idx]
        return new_assignment

    @profile
    def preference_agent(self, assignment: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        np.ndarray
            Modified assignment array with multiple TAs assigned to preferred labs.

        Description
        -----------
        Assigns multiple TAs (up to 5) to their preferred, unassigned labs in a single operation.
        Since preferred assignments satisfy availability and align with objectives, batch assignment is efficient.
        """
        new_assignment = assignment.copy()
        num_assignments = min(5, self.prefer.shape[0])

        for _ in range(num_assignments):
            unassigned_preferred = (self.prefer == 1) & (new_assignment == 0)
            available_slots = np.argwhere(unassigned_preferred)

            if len(available_slots) == 0:
                break

            choice = np.random.choice(len(available_slots))
            ta_idx, lab_idx = available_slots[choice]
            new_assignment[ta_idx, lab_idx] = 1

        return new_assignment

    @profile
    def schedule_swapping_agent(self, assignment: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        np.ndarray
            Modified assignment array with two TAs' schedules swapped.

        Description
        -----------
        Randomly select two TAs and swap their entire schedules (swap two rows in the array).
        """
        new_assignment = assignment.copy()
        ta_idx1, ta_idx2 = np.random.choice(assignment.shape[0], size=2, replace=False)
        new_assignment[[ta_idx1, ta_idx2]] = new_assignment[[ta_idx2, ta_idx1]]
        return new_assignment

    @profile
    def conflict_remover_agent(self, assignment: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        np.ndarray
            Modified assignment array with all conflicts removed.

        Description
        -----------
        Identify all scheduling conflicts and remove them by unassigning TAs from conflicting labs.
        For each TA with conflicts, keeps only one randomly selected lab at each conflicting time.
        """
        new_assignment = assignment.copy()
        conflicts = self.get_conflict_pairs(new_assignment)

        if len(conflicts) == 0:
            return new_assignment

        ta_conflicts = defaultdict(list)
        for ta_idx, lab_idx in conflicts:
            ta_conflicts[ta_idx].append(lab_idx)

        for ta_idx, conflicting_labs in ta_conflicts.items():
            lab_times = self.lab_times[conflicting_labs]
            time_to_labs = defaultdict(list)

            for lab_idx, time in zip(conflicting_labs, lab_times):
                time_to_labs[time].append(lab_idx)

            for time, labs_at_time in time_to_labs.items():
                if len(labs_at_time) > 1:
                    keep_lab = np.random.choice(labs_at_time)
                    for lab_idx in labs_at_time:
                        if lab_idx != keep_lab:
                            new_assignment[ta_idx, lab_idx] = 0

        return new_assignment

    @profile
    def undersupport_agent(self, assignment: np.ndarray) -> np.ndarray:
        """
        Parameters
        ----------
        assignment : np.ndarray
            2D array where rows are TAs and columns are labs. A value of 1 indicates the TA is assigned to that lab, 0 otherwise.

        Returns
        -------
        np.ndarray
            Modified assignment array with a TA assigned to an undersupported lab.

        Description
        -----------
        Assign an available, conflict-free TA to the most undersupported lab.
        """
        new_assignment = assignment.copy()
        allocated_per_lab = assignment.sum(axis=0)
        undersupport = np.maximum(self.min_ta - allocated_per_lab, 0)
        max_undersupport = undersupport.max()

        if max_undersupport == 0:
            return new_assignment

        most_undersupported_labs = np.where(undersupport == max_undersupport)[0]
        lab_idx = np.random.choice(most_undersupported_labs)

        available_tas = (self.unavail[:, lab_idx] == 0) & (assignment[:, lab_idx] == 0)
        available_ta_indices = np.where(available_tas)[0]

        if len(available_ta_indices) == 0:
            return new_assignment

        lab_time = self.lab_times[lab_idx]
        conflict_free_tas = []

        for ta_idx in available_ta_indices:
            assigned_labs = np.where(assignment[ta_idx] == 1)[0]
            assigned_times = self.lab_times[assigned_labs]
            if lab_time not in assigned_times:
                conflict_free_tas.append(ta_idx)

        if len(conflict_free_tas) == 0:
            return new_assignment

        ta_idx = np.random.choice(conflict_free_tas)
        new_assignment[ta_idx, lab_idx] = 1

        return new_assignment
