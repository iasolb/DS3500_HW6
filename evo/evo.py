"""
@author: John Rachlin
@file: evo_simplified.py: An evolutionary computing framework (version 10)
       No removal of contraint violations or support for parallel island optimization.
       No timing support
"""

import random as rnd
import copy
from functools import reduce
import numpy as np


class Evo:

    def __init__(self):
        """Population constructor"""
        self.pop = (
            {}
        )  # The solution population: Evaluation (s1, s2, ..., sn) -> solution
        self.objectives = []  # Registered objectives: [(n1, obj1), (n2, obj2), ....]
        self.agents = (
            []
        )  # Registered agents:  [(n1, func1, input1), (n2, func2, input2)....]

    def size(self):
        """The size of the current population"""
        return len(self.pop)

    def add_objective(self, name, f):
        """Register a fitness criterion (objective) with the
        environment. Any solution added to the environment is scored
        according to this objective"""
        self.objectives.append((name, f))

    def add_agent(self, name, f, k=1):
        """Register a named agent with the population.
        The function fa defines what the agent does.
        k defines the number of solutions the agent operates on."""
        self.agents.append((name, f, k))

    def get_random_solutions(self, k=1):
        """Pick k random solutions from the population
        Return a list of solution copies (pre-mutated)
        Leave original parent solutions unchanged"""
        if self.size() == 0:  # No solutions in population
            return []
        else:
            solutions = tuple(self.pop.values())  # All solutions in the population
            return [copy.deepcopy(rnd.choice(solutions)) for _ in range(k)]

    def add_solution(self, sol):
        """Add a solution to the population"""
        scores = tuple([f(sol) for _, f in self.objectives])
        self.pop[scores] = sol

    def run_random_agent(self):
        """Invoke an agent against the population"""
        _, f, k = rnd.choice(self.agents)  # pick random agent unpack necessary info
        sols = self.get_random_solutions(k)
        new_solution = f(sols)
        self.add_solution(new_solution)

    @staticmethod
    def dominates(p, q):
        """p = evaluation of solution: (score1, score2, ..., scoren)
        p dominates q if for all i, pi <= qi and there exists i, pi < qi"""
        score_diffs = np.array(p) - np.array(q)
        return all(d <= 0 for d in score_diffs) and any(d < 0 for d in score_diffs)

    @staticmethod
    def reduce_nds(S, p):
        return S - {q for q in S if Evo.dominates(p, q)}

    def remove_dominated(self):
        """Remove dominated solutions"""
        nds = reduce(Evo.reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {scores: self.pop[scores] for scores in nds}

    def evolve(self, n=1, dom=100):
        """Run n random agents (default=1)

        n:    number of generations

        dom:  defines how often we remove dominated (unfit) solutions
        status defines how often we display the current population
        """

        for i in range(n):
            self.run_random_agent()
            if i % dom == 0:
                self.remove_dominated()
                print("Iteration:", i)
                print("Population size:", self.size())
                print(self)

        # final clean up
        self.remove_dominated()

    def __str__(self):
        """Output the solutions in the population"""
        rslt = ""
        for scores, sol in self.pop.items():
            rslt += str(scores) + ":\t" + str(sol) + "\n"
        return rslt
