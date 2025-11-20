"""
Authors: Cassandra Cinzori and Ian Solberg
File: test_assignta.py
Description: unit tests for each objective
"""
import pandas as pd
import numpy as np
from assignta import AssignTa
import pytest


# Import profiler to time tests
try:
    from profiler import profile, Profiler
    PROFILING_ENABLED = True
except ImportError:
    # If profiler not available, create dummy decorator
    def profile(f):
        return f
    PROFILING_ENABLED = False


@profile
def test1():
    """
    Expected Objective Vals:
    Overallocation: 34
    Conflicts: 7
    Undersupport: 1
    Unavailable: 59
    Unpreferred: 10
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = pd.read_csv("../assignta_data/test1.csv", header=None).to_numpy()
    a.get_preference_masks()
    return a

@profile
def test2():
    """
    Expected Objective Vals:
    Overallocation: 37
    Conflicts: 5
    Undersupport: 0
    Unavailable: 57
    Unpreferred: 16
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = pd.read_csv("../assignta_data/test2.csv", header=None).to_numpy()
    a.get_preference_masks()
    return a

@profile
def test3():
    """
    Expected Objective Vals:
    Overallocation: 19
    Conflicts: 2
    Undersupport: 11
    Unavailable: 34
    Unpreferred: 17
    """
    a = AssignTa()
    a.assign_ta_df("../assignta_data/tas.csv")
    a.assign_lab_df("../assignta_data/sections.csv")
    a.assignment = pd.read_csv("../assignta_data/test3.csv", header=None).to_numpy()
    a.get_preference_masks()
    return a


def get_test_states():
    """
    Helper function to get all three test states
    """
    state1, state2, state3 = test1(), test2(), test3()
    return state1, state2, state3

# ==== Overallocation Tests
@profile
def test_overallocation():
    """
    Test overallocation objective on all three test cases
    """
    state1, state2, state3 = get_test_states()

    # Test 1: Expected 34
    result1 = state1.overallocation(state1.assignment)
    assert result1 == 34, f"Test1 overallocation: expected 34, got {result1}"

    # Test 2: Expected 37
    result2 = state2.overallocation(state2.assignment)
    assert result2 == 37, f"Test2 overallocation: expected 37, got {result2}"

    # Test 3 Expected 19
    result3 = state3.overallocation(state3.assignment)
    assert result3 == 19, f"Test3 overallocation: expected 19, got {result3}"


# ==== Conflict Tests
@profile
def test_conflicts():
    """
    Test conflicts objective on all three test cases
    """
    state1, state2, state3 = get_test_states()

    # Test 1: Expected 7
    result1 = state1.conflicts(state1.assignment)
    assert result1 == 7, f"Test1 conflicts: expected 7, got {result1}"

    # Test 2: Expected 5
    result2 = state2.conflicts(state2.assignment)
    assert result2 == 5, f"Test2 conflicts: expected 5, got {result2}"

    # Test 3: Expected 2
    result3 = state3.conflicts(state3.assignment)
    assert result3 == 2, f"Test3 conflicts: expected 2, got {result3}"


# ==== Undersupport Tests
@profile
def test_undersupport():
    """
    Test undersupport objective on all three test cases
    """
    state1, state2, state3 = get_test_states()

    # Test 1: Expected 1
    result1 = state1.undersupport(state1.assignment)
    assert result1 == 1, f"Test1 undersupport: expected 1, got {result1}"

    # Test 2: Expected 0
    result2 = state2.undersupport(state2.assignment)
    assert result2 == 0, f"Test2 undersupport: expected 0, got {result2}"

    # Test 3: Expected 11
    result3 = state3.undersupport(state3.assignment)
    assert result3 == 11, f"Test3 undersupport: expected 11, got {result3}"


# ==== Unavailable Tests
@profile
def test_unavailable():
    """
    Test unavailable objective on all three test cases
    """
    state1, state2, state3 = get_test_states()

    # Test 1: Expected 59
    result1 = state1.unavailable(state1.assignment)
    assert result1 == 59, f"Test1 unavailable: expected 59, got {result1}"

    # Test 2: Expected 57
    result2 = state2.unavailable(state2.assignment)
    assert result2 == 57, f"Test2 unavailable: expected 57, got {result2}"

    # Test 3: Expected 34
    result3 = state3.unavailable(state3.assignment)
    assert result3 == 34, f"Test3 unavailable: expected 34, got {result3}"


# ==== Unpreferred Tests
@profile
def test_unpreferred():
    """
    Test unpreferred objective on all three test cases
    """
    state1, state2, state3 = get_test_states()

    # Test 1: Expected 10
    result1 = state1.unpreferred(state1.assignment)
    assert result1 == 10, f"Test1 unpreferred: expected 10, got {result1}"

    # Test 2: Expected 16
    result2 = state2.unpreferred(state2.assignment)
    assert result2 == 16, f"Test2 unpreferred: expected 16, got {result2}"

    # Test 3: Expected 17
    result3 = state3.unpreferred(state3.assignment)
    assert result3 == 17, f"Test3 unpreferred: expected 17, got {result3}"

# ==== Main Function
def main():
    print("Running manual tests...")

    # Overallocation
    print("\n=== Testing Overallocation ===")
    try:
        test_overallocation()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Overallocation test failed: {e}")


    # Conflicts
    print("\n=== Testing Conflicts ===")
    try:
        test_conflicts()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Conflict test failed: {e}")

    # Undersupport
    print("\n=== Testing Undersupport ===")
    try:
        test_undersupport()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Undersupport test failed: {e}")

    # Unavailable
    print("\n=== Testing Unavailable ===")
    try:
        test_unavailable()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Unavailable test failed: {e}")

    # Unpreferred
    print("\n=== Testing Unpreferred ===")
    try:
        test_unpreferred()
        print("✅ All tests passed")
    except AssertionError as e:
        print(f"❌ Unpreferred test failed: {e}")

    # Print profiling report if enabled
    if PROFILING_ENABLED:
        print("\n" + "=" * 60)
        print("TEST PROFILING REPORT")
        print("=" * 60)
        Profiler.report()

if __name__ == "__main__":
    main()
