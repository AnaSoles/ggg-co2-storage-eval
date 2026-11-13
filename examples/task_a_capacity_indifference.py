"""Research demo: compare Rødby, Havnsø and Inez/Haldager MC capacities.

Run from repository root after: python -m pip install -e .
  python examples/task_a_capacity_indifference.py

All capacity inputs come from pre-existing example CSV files. This exercise
is *not* a recommendation of a final q for CO2SITE.
"""
from pathlib import Path
import csv

from storageeval import load_site_csv, simulate
from storageeval.indifference import compare_all_sites, common_q_diagnostics

ROOT = Path(__file__).parent
SITES = {
    "Rødby – Bunter": "data_rodby_inputs.csv",
    "Havnsø – Gassum": "data_havnso_s1_inputs.csv",
    "Inez – Haldager": "data_inez_haldager_inputs.csv",
}

def main():
    results = []
    for k, (name, filename) in enumerate(SITES.items()):
        result = simulate(load_site_csv(ROOT / filename, name=name),
                          iterations=20_000, seed=42 + k)
        results.append(result)
        capacities = result.capacity_mt
        print(f"{name}: mean={capacities.mean():.2f} Mt; "
              f"std={capacities.std(ddof=1):.2f} Mt")
    comparisons = compare_all_sites(results, confidence=0.95, seed=2026)
    for result in comparisons:
        print(f"{result['second_site']} - {result['first_site']}: "
              f"mean difference={result['mean_difference_mt']:.2f} Mt, "
              f"P(second>first)={result['prob_second_greater']:.1%}, "
              f"candidate pair q={result['q_pair_candidate_mt']:.2f} Mt")
    print("Exploratory common-q diagnostic:", common_q_diagnostics(comparisons))
    target = ROOT / "task_a_pair_comparisons.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    print("Results CSV:", target)

if __name__ == "__main__":
    main()
