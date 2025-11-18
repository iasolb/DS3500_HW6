"""
Sort a Random List of Random Integers in ascending order without implementing a sort algorithm or built-in sorting fxns

ONLY EVOLUTIONARY COMPUTING
"""

from evo import Evo
import random as rnd
from profile import Profile


def unsorted(L: list):
    """
    Objective which counts total sum of steps dowm
    Input Solution -> Single Number
    """
    return sum([x - y for x, y in zip(L, L[1:]) if y < x])  # Get each pair


def sumratio(L):
    """ratio of the sum of first-half values to the second half values"""
    return round(sum(L[: len(L) // 2]) / sum(L[len(L) // 2 :]), 5)


def swapper(solutions: list):
    """Agents always accept a list, modifies input solution to create a single new solution"""
    L = solutions[0]
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    return L


def main():

    # create framework / population
    E = Evo()
    E.add_objective("unsorted", unsorted)
    E.add_objective("sum-ratio", sumratio)
    E.add_agent("swapper", swapper, 1)
    N = 35
    L = [rnd.randrange(1, 99) for _ in range(N)]
    E.add_solution(L)
    print(E)
    E.evolve(n=1000000, dom=1000)
    print(E)


if __name__ == "__main__":
    main()
