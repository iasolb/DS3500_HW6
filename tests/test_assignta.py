"""
Authors: Cassandra Cinzori and Ian Solberg
File: test_assignta.py
Description: unit tests for each objective
"""

from assignta import AssignTa
import pytest


def instance():
    a = AssignTa()
    a.assign_ta_df("assignta_data/tas.csv")
    a.assign_lab_df("assignta_data/sections.csv")
    a.init_assignment(len(a.ta), len(a.lab))
    # TODO make a setup with a known assignment matrix
    return a


def wrapper(f: function) -> function:

    state = instance()

    return state


def test_overallocation():
    pass


def test_conflicts():
    pass


def test_undersupport():
    pass


def test_unavailable():
    pass


def main():
    test_overallocation()
    test_conflicts()
    test_undersupport()
    test_undersupport()


if __name__ == "__main__":
    main()
