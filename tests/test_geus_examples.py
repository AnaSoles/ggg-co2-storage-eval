from pathlib import Path

import numpy as np

from storageeval import load_site_csv, simulate


EXAMPLES = Path("examples")


def test_gassum_structure_reproduces_geus_capacity():
    site = load_site_csv(EXAMPLES / "data_gassum_structure_inputs.csv")
    summary = simulate(site, iterations=200_000, seed=42).summary()

    assert abs(summary["p90_mt"] - 325.36) < 10
    assert abs(summary["p50_mt"] - 485.77) < 10
    assert abs(summary["p10_mt"] - 688.98) < 10
    assert abs(summary["mean_mt"] - 498.44) < 10


def test_inez_combined_reproduces_geus_capacity():
    filenames = [
        "data_inez_haldager_inputs.csv",
        "data_inez_gassum_inputs.csv",
        "data_inez_skagerrak_inputs.csv",
    ]
    capacities = []
    for offset, filename in enumerate(filenames):
        site = load_site_csv(EXAMPLES / filename)
        capacities.append(simulate(site, iterations=200_000, seed=42 + offset).capacity_mt)

    combined = np.sum(capacities, axis=0)
    q10, q50, q90 = np.percentile(combined, [10, 50, 90])

    assert abs(q10 - 148.6) < 8
    assert abs(q50 - 216.2) < 8
    assert abs(q90 - 310.2) < 8
    assert abs(np.mean(combined) - 224.8) < 8
