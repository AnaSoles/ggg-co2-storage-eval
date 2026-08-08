# CO2 Storage Eval

`storageeval` is a small Python package for deterministic and probabilistic
static CO2 storage-capacity assessment.

## Run in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/storage_capacity_colab.ipynb)

Click the button above, then choose **Runtime -> Run all**. No local Python or
Codespace setup is required. Edit the values in the notebook's **Editable
inputs** cell to assess another storage site.

## Capacity equation

```text
SC = GRV × N/G × porosity × CO2 density × storage efficiency
```

If GRV is in km3, density is in kg/m3, and the other inputs are decimal
fractions, the result is numerically in million tonnes of CO2 (Mt).

## Install

```bash
python -m pip install -e .
```

For plots and tests:

```bash
python -m pip install -e ".[plots,dev]"
pytest
```

## Example

```python
from storageeval import Distribution, StorageSite, simulate

site = StorageSite(
    name="Rødby – Bunter Sandstone",
    grv=Distribution.pert(22.57, 28.21, 33.85),
    net_to_gross=Distribution.pert(0.20, 0.25, 0.30),
    porosity=Distribution.pert(0.184, 0.23, 0.276),
    co2_density=Distribution.pert(573.4, 603.6, 663.96),
    storage_efficiency=Distribution.pert(0.05, 0.10, 0.20),
)

result = simulate(site, iterations=100_000, seed=42)
print(result.summary())
result.plot_distribution()
result.plot_exceedance()
result.plot_capacity_ranges()
result.plot_sensitivity()
```

The Rødby notebook includes a live input table and a comparison with GEUS
Report 2024/18, Table 8.5.1. Table 8.2.1 prints the maximum GRV as 23.9 km3,
while Table 8.4.1 and the stated +/-20% method support 33.85 km3. Table 8.4.1
also prints the maximum CO2 density as 764.0 kg/m3, while Section 8.2.4 defines
it as 10% above the 603.6 kg/m3 mode (663.96 kg/m3). The example uses the
internally consistent 33.85 and 663.96 values, which closely reproduce the
published capacity statistics.

The first three plots mirror the familiar `gppeval` presentation: a simulated
PDF with a fitted curve and P90/P50/P10 markers, an exceedance curve, and a
linear confidence-range bar. For CO2 storage, the ranges are labelled as
capacity estimates rather than reserves.

The summary follows storage-industry exceedance notation: P90 is the 10th
percentile (a conservative capacity), P50 is the median, and P10 is the 90th
percentile (an upside capacity).

Inputs can also be loaded from the included CSV format:

```python
from storageeval import load_site_csv, simulate

site = load_site_csv("examples/rodby_inputs.csv", name="Rødby – Bunter Sandstone")
result = simulate(site, iterations=100_000, seed=42)
```

## Scope

Version 0.1 covers static volumetric capacity. It does not yet model pressure
constraints, injectivity, plume migration, dynamic simulation, or economics.

## License

MIT
