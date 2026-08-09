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

## Install

```bash
python -m pip install -e .
```

For plots and tests:

```bash
python -m pip install -e ".[plots,dev]"
pytest
```

## Libraries used

The project is written in Python 3.10+ and uses a small set of libraries:

| Library | How it is used | Installation |
|---|---|---|
| [NumPy](https://numpy.org/) | Monte Carlo sampling, array calculations, percentiles, summary statistics, and rank-correlation sensitivity | Core dependency |
| [Matplotlib](https://matplotlib.org/) | Probability-distribution, exceedance, capacity-range, and sensitivity plots | Optional `plots` dependency |
| [pandas](https://pandas.pydata.org/) | Input, source, and GEUS comparison tables in the Colab notebooks | Included in Google Colab; install separately for local notebook use |
| [pytest](https://pytest.org/) | Automated tests and checks against published GEUS capacity results | Optional `dev` dependency |
| Python standard library | CSV reading, file paths, and data classes through `csv`, `pathlib`, and `dataclasses` | Included with Python |

NumPy is the only required third-party dependency for the core calculation
package. Matplotlib is loaded only when plots are requested. pandas is used for
the interactive notebook tables and is not required by the core
`storageeval` API.

For local notebook use, the complete environment can be installed with:

```bash
python -m pip install -e ".[plots,dev]" pandas
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

## Recommendation for future storage-efficiency evaluations

Storage efficiency is not a universal constant, so a mode such as 7% or 10%
may not be representative of every reservoir. For future prospective
assessments, the following considerations may help guide the selection:

1. The storage setting could be classified using the available geology,
   including lithology, depositional environment, reservoir heterogeneity,
   and open, semi-closed, or closed boundary conditions.
2. The relevant efficiency-factor ranges in
   [DOE/NETL CO2-SCREEN](https://edx.netl.doe.gov/dataset/co2-screen) may
   provide a useful initial screening reference.
3. It may be helpful to document the selected PERT minimum, mode, and maximum,
   together with the source and geological rationale for each value.
   CO2-SCREEN can support this selection, although it does not provide one
   universal mode for every site.
4. Where the available evidence does not clearly distinguish between
   plausible modes (for example, 7% and 10%), both values could be explored as
   sensitivity scenarios.
5. As site-specific well, core, pressure, seismic, and dynamic
   reservoir-simulation results become available, they may be used to refine
   or narrow the initial screening assumptions.

These ranges may be useful for estimating a prospective static storage
resource. However, they do not by themselves demonstrate injectivity,
operational capacity, or commercial viability. See the
[CO2-SCREEN User's Manual](https://www.netl.doe.gov/projects/files/CO2SCREENUsersManualPythonV4.1_040822.pdf)
for the DOE/NETL methodology.

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
