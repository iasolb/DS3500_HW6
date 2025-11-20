"""
Authors: Cassandra Cinzori and Ian Solberg
File: test_assignta.py
Description: unit tests for each objective
"""

import pandas as pd
import numpy as np
from assignta import AssignTa
import pytest


# @pytest.fixture
def test1():
    """
    Expected Objective Vals:
    Overallocation:
    Conflicts:
    Undersupport:
    Unavailable:
    Unpreferred:
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = (a._load_data("../assignta_data/test1.csv")).to_numpy()
    # TODO make a setup with a known assignment matrix
    return a


def test2():
    """
    Expected Objective Vals:
    Overallocation:
    Conflicts:
    Undersupport:
    Unavailable:
    Unpreferred:
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = (a._load_data("../assignta_data/test2.csv")).to_numpy()
    # TODO make a setup with a known assignment matrix
    return a


def test3():
    """
    Expected Objective Vals:
    Overallocation:
    Conflicts:
    Undersupport:
    Unavailable:
    Unpreferred:
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = (a._load_data("../assignta_data/test3.csv")).to_numpy()
    # TODO make a setup with a known assignment matrix
    return a


def get_test_states() -> function:

    state1, state2, state3 = test1(), test2(), test3()

    return state1, state2, state3


def test_overallocation(test_states: tuple[function, function, function]):
    test1, test2, test3 = test_states()
    assert test1.assignment.overallocation() == 0  # replace 0 with expected value
    assert test2.assignment.overallocation() == 0  # replace 0 with expected value
    assert test3.assignment.overallocation() == 0  # replace 0 with expected value
    pass


def test_conflicts(test_state: np.array):
    assert test_state.conflicts() == 0  # replace 0 with expected value
    pass


def test_undersupport(test_state: np.array):
    assert test_state.undersupport() == 0  # replace 0 with expected value
    pass


def test_unavailable(test_state: np.array):
    assert test_state.unavailable() == 0  # replace 0 with expected value


def main():
    pass


if __name__ == "__main__":
    main()
