"""Inez capacity: simulate three reservoirs and add matching trials."""

from pathlib import Path

import numpy as np

from storageeval import SimulationResult, load_site_csv, simulate


HERE = Path(__file__).parent
ITERATIONS = 100_000
SEED = 42

reservoir_files = {
    "Haldager Sand": "inez_haldager_inputs.csv",
    "Gassum Formation": "inez_gassum_inputs.csv",
    "Skagerrak Formation": "inez_skagerrak_inputs.csv",
}

results = {}
for offset, (name, filename) in enumerate(reservoir_files.items()):
    site = load_site_csv(HERE / filename, name=f"Inez – {name}")
    results[name] = simulate(site, iterations=ITERATIONS, seed=SEED + offset)

# Sum iteration i from each reservoir. Do not add their P90/P50/P10 values.
combined_capacity = np.sum(
    [result.capacity_mt for result in results.values()], axis=0
)
combined = SimulationResult("Inez – combined reservoirs", combined_capacity, {})

for name, result in results.items():
    print(name, result.summary())
print("Combined Inez", combined.summary())
