"""
Authors: Cassandra Cinzori and Ian Solberg
File: run_optimization.py
Description: Main script to run TA assignment optimization
"""

from evo import Evo
from profiler import profile, Profiler
from assignta import AssignTa
import numpy as np


@profile
def optimize_ta_assignment():
    """
    Run optimization for 5 minutes
    Returns the summary DataFrame
    """

    # Setup
    print("Loading data...")
    a = AssignTa()
    a.assign_ta_df("assignta_data/tas.csv")
    a.assign_lab_df("assignta_data/sections.csv")
    a.get_preference_masks()

    evo = Evo()

    # Add all 5 objectives
    print("Adding objectives...")
    evo.add_objective("overallocation", lambda sol: a.overallocation(sol))
    evo.add_objective("conflicts", lambda sol: a.conflicts(sol))
    evo.add_objective("undersupport", lambda sol: a.undersupport(sol))
    evo.add_objective("unavailable", lambda sol: a.unavailable(sol))
    evo.add_objective("unpreferred", lambda sol: a.unpreferred(sol))

    # Add agents (wrap with lambda sols: ... sols[0])
    print("Adding agents...")
    evo.add_agent("random_flip", lambda sols: a.random_flip_agent(sols[0]))
    evo.add_agent("preference", lambda sols: a.preference_agent(sols[0]))

    # Add more agents if you've implemented them:
    # evo.add_agent("undersupport", lambda sols: a.undersupport_agent(sols[0]))
    # evo.add_agent("conflict_remover", lambda sols: a.conflict_remover_agent(sols[0]))

    # Initial population
    print("Creating initial population...")
    evo.add_solution(a.zeros())
    for _ in range(20):
        evo.add_solution(np.random.randint(0, 2, size=(40, 17)))

    # RUN FOR 5 MINUTES!
    print("\nStarting 5-minute optimization...\n")
    evo.evolve(time_limit=300, dom=100, status=100)

    return evo.summarize(group_name="CassIan")


if __name__ == "__main__":
    print("=" * 80)
    print("TA ASSIGNMENT OPTIMIZATION - CassIan")
    print("=" * 80)
    print()

    # Run optimization
    summary = optimize_ta_assignment()

    # Save summary (DELIVERABLE)
    summary.to_csv("CassIan_summary.csv", index=False)
    print(f"\n✅ CassIan_summary.csv saved ({len(summary)} solutions)")

    # Show preview
    print("\nTop 5 solutions:")
    print(summary.head(5).to_string(index=False))

    # Save profiling report (DELIVERABLE)
    print("\n" + "=" * 80)
    print("GENERATING PROFILING REPORT")
    print("=" * 80)
    Profiler.report(output_file="CassIan_profile.txt")
    print("✅ CassIan_profile.txt saved")

    print("\n" + "=" * 80)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  ✅ CassIan_summary.csv")
    print("  ✅ CassIan_profile.txt")
    print("\nNext: Write best_solution.txt")