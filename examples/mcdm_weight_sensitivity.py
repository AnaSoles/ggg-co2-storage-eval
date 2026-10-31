"""Illustrative weighted-sum MCDM sensitivity analysis, based on Dean (2022), section 5.8.

All site scores are fictional. Cost is reverse-scored: 5 = lower cost.
Other weights are adjusted proportionally when varying one criterion's weight.
"""
import csv
from pathlib import Path

CRITERIA = ("Storage capacity", "Injectivity", "Storage cost")
SITES = {"Site A": (5, 3, 2), "Site B": (3, 5, 4), "Site C": (4, 2, 5)}
BASE_WEIGHTS = (0.40, 0.35, 0.25)


def weighted_scores(weights, sites=SITES):
    if len(weights) != len(CRITERIA) or any(w < 0 for w in weights) or abs(sum(weights) - 1) > 1e-9:
        raise ValueError("Weights must be nonnegative, have three values, and sum to one.")
    if any(len(scores) != len(CRITERIA) for scores in sites.values()):
        raise ValueError("Each site needs one score per criterion.")
    return {site: sum(w * s for w, s in zip(weights, scores)) for site, scores in sites.items()}


def ranking(scores):
    """Descending. Ties use alphabetical order only for deterministic display."""
    return sorted(scores, key=lambda site: (-round(scores[site], 10), site))


def vary_one_weight(weights, index, new_value):
    if not 0 <= index < len(weights) or not 0 <= new_value <= 1:
        raise ValueError("Invalid index or weight.")
    remaining = sum(weights) - weights[index]
    if remaining <= 0:
        if new_value == 1:
            return tuple(1.0 if i == index else 0.0 for i in range(len(weights)))
        raise ValueError("Cannot rescale zero remaining weights.")
    return tuple(new_value if i == index else weights[i] * (1 - new_value) / remaining for i in range(len(weights)))


def sensitivity_rows(step=0.05):
    if not 0 < step <= 1:
        raise ValueError("Step must be between 0 and 1.")
    n = round(1 / step)
    if abs(n * step - 1) > 1e-9:
        raise ValueError("Step must divide 1 exactly.")
    base_order = ranking(weighted_scores(BASE_WEIGHTS))
    rows = []
    for index, criterion in enumerate(CRITERIA):
        for k in range(n + 1):
            target = k / n
            weights = vary_one_weight(BASE_WEIGHTS, index, target)
            values = weighted_scores(weights)
            order = ranking(values)
            best = max(values.values())
            winners = sorted(s for s, v in values.items() if abs(v - best) < 1e-9)
            rows.append({
                "criterion_varied": criterion,
                "tested_weight": round(target, 6),
                "storage_capacity_weight": round(weights[0], 6),
                "injectivity_weight": round(weights[1], 6),
                "storage_cost_weight": round(weights[2], 6),
                **{f"{site}_score": round(values[site], 6) for site in SITES},
                "ranking": " > ".join(order),
                "winners": " / ".join(winners),
                "same_ranking_as_baseline": order == base_order,
            })
    return rows


def main():
    baseline = weighted_scores(BASE_WEIGHTS)
    print("FICTIONAL example: scores 1 to 5 (5 = best).")
    print("Baseline weighted scores:", baseline)
    print("Baseline display order:", " > ".join(ranking(baseline)))
    print("Note: identical scores represent ties, not true ordering.")
    rows = sensitivity_rows()
    output = Path(__file__).with_name("mcdm_sensitivity_results.csv")
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for criterion in CRITERIA:
        tested = [r for r in rows if r["criterion_varied"] == criterion]
        different = [r["tested_weight"] for r in tested if not r["same_ranking_as_baseline"]]
        print(f"{criterion}: {len(different)}/{len(tested)} tested weights change the display order")
    print("CSV written:", output)


if __name__ == "__main__":
    main()
