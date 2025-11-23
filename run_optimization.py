"""
Authors: Cassandra Cinzori and Ian Solberg
File: run_optimization.py
Description: Main script to run TA assignment optimization
"""

from evo import Evo
from profiler import profile, Profiler
from assignta import AssignTa
import numpy as np
import os
from datetime import datetime

# Output directory
OUTPUT_DIR = "outputs"


def ensure_output_dir():
    """Create outputs directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created directory: {OUTPUT_DIR}/")


def save_readable_assignment(assignment, assignta, filepath):
    """
    Save assignment in human-readable format with TA and lab names

    Parameters
    ----------
    assignment : np.ndarray
        Assignment matrix
    assignta : AssignTa
        AssignTa object with TA and lab data
    filepath : str
        Path to save the readable assignment
    """
    import pandas as pd

    # Get TA names and lab sections
    ta_names = assignta.ta["name"].values
    lab_sections = assignta.lab["daytime"].values

    # Create list of assignments
    assignments = []
    for ta_idx in range(assignment.shape[0]):
        ta_name = ta_names[ta_idx]
        assigned_labs = np.where(assignment[ta_idx] == 1)[0]

        if len(assigned_labs) == 0:
            assignments.append({"TA": ta_name, "Assigned_Labs": "None", "Count": 0})
        else:
            lab_list = ", ".join(
                [f"Lab {i} ({lab_sections[i]})" for i in assigned_labs]
            )
            assignments.append(
                {"TA": ta_name, "Assigned_Labs": lab_list, "Count": len(assigned_labs)}
            )

    df = pd.DataFrame(assignments)
    df.to_csv(filepath, index=False)


@profile
def optimize_ta_assignment(time_limit=300):
    """
    Run TA assignment optimization

    Parameters
    ----------
    time_limit : int
        Time limit in seconds (default: 300 = 5 minutes)

    Returns
    -------
    tuple
        (summary DataFrame, Evo object, AssignTa object)
    """
    # Initialize
    print("Loading data...")
    a = AssignTa()
    a.assign_ta_df("assignta_data/tas.csv")
    a.assign_lab_df("assignta_data/sections.csv")

    evo = Evo()

    # Add objectives
    print("Adding objectives...")
    evo.add_objective("overallocation", lambda sol: a.overallocation(sol))
    evo.add_objective("conflicts", lambda sol: a.conflicts(sol))
    evo.add_objective("undersupport", lambda sol: a.undersupport(sol))
    evo.add_objective("unavailable", lambda sol: a.unavailable(sol))
    evo.add_objective("unpreferred", lambda sol: a.unpreferred(sol))
    evo.add_objective("aggregatescore", lambda sol: a.aggregate_objective(sol))

    # Add agents
    print("Adding agents...")
    evo.add_agent("random_flip", lambda sols: a.random_flip_agent(sols[0]))
    evo.add_agent("preference", lambda sols: a.preference_agent(sols[0]))
    evo.add_agent("schedule_swap", lambda sols: a.schedule_swapping_agent(sols[0]))
    evo.add_agent("conflict_remover", lambda sols: a.conflict_remover_agent(sols[0]))
    evo.add_agent("undersupport", lambda sols: a.undersupport_agent(sols[0]))

    # Create initial population
    print("Creating initial population...")
    evo.add_solution(a.zeros())  # Start with empty assignment
    for _ in range(20):
        evo.add_solution(np.random.randint(0, 2, size=(40, 17)))

    # Run optimization
    print(f"\n🚀 Starting {time_limit}-second optimization...\n")
    evo.evolve(time_limit=time_limit, dom=100, status=100)

    return evo.summarize(group_name="CassIan"), evo, a


def save_best_solution(summary, evo, assignta, output_dir=OUTPUT_DIR):
    """
    Save the best solution in a readable format

    Parameters
    ----------
    summary : pd.DataFrame
        Summary DataFrame from optimization
    evo : Evo
        Evo object containing solutions
    assignta : AssignTa
        AssignTa object with TA and lab data
    output_dir : str
        Directory to save output files
    """
    best_row = summary.iloc[0]

    # Get the best solution from the population dictionary
    # The keys are tuples of objective values, find the one matching best_row
    best_key = tuple(
        best_row[obj] for obj, _ in evo.objectives if obj != "aggregatescore"
    )
    best_solution = evo.pop.get(best_key)

    # If not found, try getting any solution from pop as fallback
    if best_solution is None and len(evo.pop) > 0:
        best_solution = next(iter(evo.pop.values()))

    if best_solution is not None:
        # Save the raw assignment matrix as CSV
        matrix_path = os.path.join(output_dir, "best_assignment_matrix.csv")
        np.savetxt(matrix_path, best_solution, delimiter=",", fmt="%d")
        print(f"✅ {matrix_path}")

        # Save human-readable assignment
        readable_path = os.path.join(output_dir, "best_assignment_readable.csv")
        save_readable_assignment(best_solution, assignta, readable_path)
        print(f"✅ {readable_path}")

    # Save metrics report
    filepath = os.path.join(output_dir, "best_solution.txt")
    with open(filepath, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("BEST TA ASSIGNMENT SOLUTION\n")
        f.write("=" * 80 + "\n\n")

        f.write("Solution Metrics:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Overallocation:   {best_row['overallocation']}\n")
        f.write(f"Conflicts:        {best_row['conflicts']}\n")
        f.write(f"Undersupport:     {best_row['undersupport']}\n")
        f.write(f"Unavailable:      {best_row['unavailable']}\n")
        f.write(f"Unpreferred:      {best_row['unpreferred']}\n")
        f.write(f"Aggregate Score:  {best_row['aggregatescore']:.2f}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("INTERPRETATION\n")
        f.write("=" * 80 + "\n\n")

        # Hard constraints
        f.write("Hard Constraints (Must be 0):\n")
        f.write("-" * 40 + "\n")
        if best_row["conflicts"] == 0:
            f.write("✅ Conflicts: NONE - No TAs assigned to overlapping time slots\n")
        else:
            f.write(
                f"❌ Conflicts: {best_row['conflicts']} TAs have scheduling conflicts\n"
            )

        if best_row["unavailable"] == 0:
            f.write("✅ Unavailable: NONE - No TAs assigned when unavailable\n")
        else:
            f.write(
                f"⚠️  Unavailable: {best_row['unavailable']} assignments to unavailable TAs\n"
            )

        # Medium constraints
        f.write("\nMedium Priority:\n")
        f.write("-" * 40 + "\n")
        if best_row["overallocation"] == 0:
            f.write("✅ Overallocation: NONE - All TAs within max assignments\n")
        else:
            f.write(
                f"⚠️  Overallocation: {best_row['overallocation']} excess assignments\n"
            )

        if best_row["undersupport"] == 0:
            f.write("✅ Undersupport: NONE - All labs have minimum TA coverage\n")
        else:
            f.write(f"⚠️  Undersupport: {best_row['undersupport']} labs need more TAs\n")

        # Soft constraints
        f.write("\nSoft Preferences:\n")
        f.write("-" * 40 + "\n")
        if best_row["unpreferred"] == 0:
            f.write("✅ Unpreferred: NONE - All TAs assigned to preferred sections\n")
        else:
            f.write(
                f"📋 Unpreferred: {best_row['unpreferred']} assignments to willing (not preferred) sections\n"
            )

        f.write("\n" + "=" * 80 + "\n")

    print(f"✅ {filepath}")


def main():
    """Main execution function"""
    # Ensure output directory exists
    ensure_output_dir()

    # Header
    print("=" * 80)
    print("TA ASSIGNMENT OPTIMIZATION - CassIan")
    print("=" * 80)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Run started: {timestamp}")
    print()

    # Run optimization
    summary, evo, assignta = optimize_ta_assignment(time_limit=300)

    # Save summary CSV
    summary_path = os.path.join(OUTPUT_DIR, "CassIan_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"\n✅ {summary_path} ({len(summary)} solutions)")

    # Display top solutions
    print("\n" + "=" * 80)
    print("TOP 5 SOLUTIONS")
    print("=" * 80)
    print(summary.head(5).to_string(index=False))

    # Save best solution interpretation
    print("\n" + "=" * 80)
    print("SAVING BEST SOLUTION")
    print("=" * 80)
    save_best_solution(summary, evo, assignta)

    # Generate profiling report
    print("\n" + "=" * 80)
    print("GENERATING PROFILING REPORT")
    print("=" * 80)
    profile_path = os.path.join(OUTPUT_DIR, "CassIan_profile.txt")
    Profiler.report(output_file=profile_path)
    print(f"✅ {profile_path}")

    # Final summary
    print("\n" + "=" * 80)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 80)
    print(f"\n📁 All outputs saved to: {OUTPUT_DIR}/")
    print("\nGenerated files:")
    print(f"  ✅ CassIan_summary.csv           - All {len(summary)} solutions")
    print("  ✅ CassIan_profile.txt           - Performance profiling data")
    print("  ✅ best_solution.txt             - Detailed metrics report")
    print("  ✅ best_assignment_matrix.csv    - Raw assignment matrix (40x17)")
    print("  ✅ best_assignment_readable.csv  - Human-readable assignments")

    # Show best solution summary
    best = summary.iloc[0]
    print("\n🏆 Best Solution:")
    print(f"   Aggregate Score: {best['aggregatescore']:.2f}")
    print(f"   Conflicts: {best['conflicts']} | Unavailable: {best['unavailable']}")
    print(
        f"   Overalloc: {best['overallocation']} | Undersupport: {best['undersupport']} | Unpreferred: {best['unpreferred']}"
    )

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
