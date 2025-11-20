"""
Authors: Cassandra Cinzori and Ian Solberg
File: evo.py
Description: evolutionary search framework
"""
import time
import copy
import numpy as np
import pandas as pd
import random as rnd
from functools import reduce




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

    def evolve(self, n=1, dom=100, time_limit=None, status=0):
        """Run n random agents (default=1)

        n: number of generations (ignored if time_limit is set)
        dom: defines how often we remove dominated (unfit) solutions
        time_limit: maximum time to run in seconds (e.g., 300 for 5 minutes)
                    If set, n is ignored and evolution runs until time limit
        status: defines how often we display the current population (0=never)
        """

        if time_limit is not None:
            # Time-limited evo
            start_time = time.time()
            i = 0

            print(f"Starting evolution with {time_limit} seconds time limit...")
            print(f"Initial population size: {self.size()}")
            print("-" * 60)

            while True:
                # Check time limit
                elapsed = time.time() - start_time
                if elapsed >= time_limit:
                    print(f"\nTime limit reached: {elapsed:.2f} seconds")
                    break

                # Run agent
                self.run_random_agent()

                # Remove dominated solution periodically
                if i % dom == 0:
                    self.remove_dominated()
                    if status > 0 and i % status == 0:
                        print(f"Iteration: {i} | Time: {elapsed:.2f}s | Population: {self.size()}")
                i += 1

            # Final cleanup
            self.remove_dominated()
            print("-" * 60)
            print(f"Evolution complete!")
            print(f"Total time: {elapsed:.2f} seconds")
            print(f"Total iterations: {i}")
            print(f"Population size: {self.size()}")
            print("-" * 60)

        else:
            for i in range(n):
                self.run_random_agent()
                if i % dom == 0:
                    self.remove_dominated()
                    if status > 0 and i % status == 0:
                        print("Iteration:", i)
                        print("Population size:", self.size())
                        if status > 1:
                           print(self)

            # Final cleanup
            self.remove_dominated()


    def summarize(self, group_name="Cass&Ian"):
        """
        Create a summary DataFrame of the current population (Pareto front)

        Parameters
        ----------
        group_name : str
            Your team/group name (max 8 characters, no spaces)

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: groupname, followed by objective names
            For TA assignment: groupname, overallocation, conflicts,
            undersupport, unavailable, unpreferred
        """

        # Build summary data
        summary_data = []

        for scores, solution in self.pop.items():
            row = {"groupname": group_name}

            # Add objective scores
            for i, (obj_name, _) in enumerate(self.objectives):
                row[obj_name] = scores[i]

            summary_data.append(row)

        # Create df
        df = pd.DataFrame(summary_data)

        # Sort by total scores
        objective_cols = [name for name, _ in self.objectives]
        df["_total"] = df[objective_cols].sum(axis=1)
        df = df.sort_values("_total")
        df = df.drop(columns=["_total"])
        df = df.reset_index(drop=True)

        return df


    def __str__(self):
        """Output the solutions in the population"""
        rslt = ""
        for scores, sol in self.pop.items():
            rslt += str(scores) + ":\t" + str(sol) + "\n"
        return rslt




