"""Standalone onshore Gassum structure example."""

from pathlib import Path

from storageeval import load_site_csv, simulate


site = load_site_csv(
    Path(__file__).with_name("gassum_structure_inputs.csv"),
    name="Gassum structure – Gassum Formation",
)
result = simulate(site, iterations=100_000, seed=42)
print(result.summary())
