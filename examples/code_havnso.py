"""Havnsø Scenario 1 based on GEUS Report 2023/38."""

from pathlib import Path

from storageeval import load_site_csv, simulate


site = load_site_csv(
    Path(__file__).with_name("data_havnso_s1_inputs.csv"),
    name="Havnsø – Gassum Formation – Scenario 1",
)
result = simulate(site, iterations=100_000, seed=42)
print(result.summary())
print(result.sensitivity())

