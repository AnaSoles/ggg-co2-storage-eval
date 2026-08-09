# CO2 Storage Eval

`storageeval` is a small Python package for deterministic and probabilistic
static CO2 storage-capacity assessment.

## Run in Google Colab

[![Open Rødby in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/storage_capacity_colab.ipynb)

[![Open Inez in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/inez_capacity_colab.ipynb)

Click a button above, then choose **Runtime -> Run all**. No local Python or
Codespace setup is required. Edit the values in the notebook's input cell to
assess another storage site.

## Capacity equation

```text
SC = GRV × N/G × porosity × CO2 density × storage efficiency
```

If GRV is in km3, density is in kg/m3, and the other inputs are decimal
fractions, the result is numerically in million tonnes of CO2 (Mt).

### Bibliographic References

The equation implemented here is the static volumetric storage-capacity equation
presented by Fyhn et al. (2023) in Section 5.4, *Storage capacity modelling*
(report page 19), of [GEUS Report 2022/29: *CCS2022-2024 WP1: The Inez
structure*](https://doi.org/10.22008/gpub/34664). For the wider methodological
basis of volumetric CO2 storage-capacity estimation, see Bachu et al. (2007),
[*CO2 storage capacity estimation: Methodology and
gaps*](https://doi.org/10.1016/S1750-5836(07)00086-2), *International Journal
of Greenhouse Gas Control*, 1(4), 430-443.

### Input-Data References

The example input files and published validation values come from these official
GEUS reports:

- **Rødby:** Abramovitz et al. (2024),
  [GEUS Report 2024/18](https://doi.org/10.22008/gpub/34739), input Table 8.4.1
  and results Table 8.5.1.
- **Inez (Haldager Sand, Gassum and Skagerrak reservoirs):** Fyhn et al. (2023),
  [GEUS Report 2022/29](https://doi.org/10.22008/gpub/34664), input Tables
  8.1.5.1-8.1.5.3 (report page 44) and results Tables 8.2.1-8.2.4
  (report page 46).
- **Standalone Gassum structure:** Keiding et al. (2024),
  [GEUS Report 2024/25](https://doi.org/10.22008/gpub/34746), input Table 8.4.1
  (report page 130) and results Table 8.5.1 (report page 131).

See [GEUS example documentation and references](docs/geus_examples.md) for the
complete source notes, input-value provenance, report inconsistencies and
validation comparisons.

## Install

```bash
python -m pip install -e .
```

For plots and tests:

```bash
python -m pip install -e ".[plots,dev]"
pytest
```

## Rødby example

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

## Inez and Gassum examples

The `examples` folder also contains official GEUS input tables for:

- Inez – Haldager Sand Formation
- Inez – Gassum Formation
- Inez – Skagerrak Formation
- Standalone onshore Gassum structure

Run `examples/inez.py` to simulate the three Inez reservoirs independently
and add their capacity samples trial by trial. Run
`examples/gassum_structure.py` for the standalone Gassum assessment. See
[`docs/geus_examples.md`](docs/geus_examples.md) for sources, published
validation values, and the explanation of the 7% storage-efficiency mode in
the Inez Gassum reservoir.

In a PERT input, the mode is the most likely input value. It is sampled during
Monte Carlo together with the other parameters. P90, P50 and P10 are calculated
afterwards from the resulting capacity distribution; the mode is not applied
to those percentiles after the calculation.

The first three Rødby plots mirror the familiar `gppeval` presentation: a
simulated PDF with a fitted curve and P90/P50/P10 markers, an exceedance curve,
and a linear confidence-range bar. For CO2 storage, the ranges are labelled as
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
