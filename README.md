# CO2 Storage Eval

`storageeval` is a small Python package for deterministic and probabilistic
CO2 storage-capacity assessment, followed by transparent technical screening.

## Run in Google Colab

### Havnsø – Main Storage Capacity Study

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/colab_havnso_capacity.ipynb)

Use this notebook for the **main Havnsø Scenario 1 assessment of the Gassum
Formation**, based on the updated GEUS 2023/38 inputs. It follows the same
tables, Monte Carlo workflow and plots as the Rødby notebook.

### Havnsø – Pressure and Injectivity Screening

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/colab_havnso_pressure_injectivity.ipynb)

Use this notebook for the **next Havnsø decision gate**. It combines every
static-capacity iteration with pressure and per-well injectivity criteria
normalized to the preliminary dynamic simulation in GEUS Report 2020/48.
The output is a screening probability of technical success, not an Eclipse
reservoir-simulation result.

### Rødby – Storage Capacity Assessment

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/colab_storage_capacity.ipynb)

Use this notebook for the **Rødby / general single-site storage-capacity assessment**.

### Inez – Storage Capacity Assessment

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AnaSoles/ggg-co2-storage-eval/blob/main/examples/colab_inez_capacity.ipynb)

Use this notebook for the **Inez assessment covering Haldager Sand, Gassum and Skagerrak reservoirs**.

Click a button above, then choose **Runtime → Run all**. No local Python or
Codespace setup is required. Edit the values in the notebook's input cell to
assess another storage site.

## Capacity equation

$$
SC = GRV \times (N/G) \times \phi \times \rho_{CO_2} \times S_{eff}
$$

If GRV is in km3, density is in kg/m3, and the other inputs are decimal
fractions, the result is numerically in million tonnes of CO2 (Mt).

### Bibliographic References

The equation implemented here is the static volumetric storage-capacity equation
presented by Fyhn et al. (2023) in Section 5.4, *Storage capacity modelling*
(report page 19), of [GEUS Report 2022/29: *CCS2022-2024 WP1: The Inez
structure*](https://doi.org/10.22008/gpub/34664). GEUS describes this as a
widely accepted saline-aquifer storage equation and cites Goodman et al.
(2011) as its methodological source:

- Goodman, A., Hakala, J. A., Bromhal, G., Deel, D., Rodosta, T., Frailey, S.,
  et al. (2011). [*U.S. DOE methodology for the development of geologic storage
  potential for carbon dioxide at the national and regional
  scale*](https://doi.org/10.1016/j.ijggc.2011.03.010). *International Journal
  of Greenhouse Gas Control*, 5(4), 952-965.

For the wider methodological basis of volumetric CO2 storage-capacity
estimation, see Bachu et al. (2007), [*CO2 storage capacity estimation:
Methodology and gaps*](https://doi.org/10.1016/S1750-5836(07)00086-2),
*International Journal of Greenhouse Gas Control*, 1(4), 430-443.

### Input-Data References

The example input files and published validation values come from these official
GEUS reports:

- **Rødby:** Abramovitz et al. (2024),
  [GEUS Report 2024/18](https://doi.org/10.22008/gpub/34739), input Table 8.4.1
  and results Table 8.5.1.
- **Havnsø:** Gregersen et al. (2023),
  [GEUS Report 2023/38](https://doi.org/10.22008/gpub/34705), Scenario 1 input
  Table 8.2.3 (report page 152) and results Table 8.3.1 (report page 154).
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

## Havnsø main-study example

```python
from storageeval import Distribution, StorageSite, simulate

site = StorageSite(
    name="Havnsø – Gassum Formation – Scenario 1",
    grv=Distribution.pert(2.9, 5.0, 8.0),
    net_to_gross=Distribution.pert(0.60, 0.75, 0.90),
    porosity=Distribution.pert(0.175, 0.219, 0.263),
    co2_density=Distribution.pert(663.86, 698.8, 768.68),
    storage_efficiency=Distribution.pert(0.05, 0.10, 0.20),
)

result = simulate(site, iterations=100_000, seed=42)
print(result.summary())
```

GEUS Report 2023/38 publishes P90 41.25, P50 62.82, P10 90.42 and mean
64.81 Mt CO2 for Scenario 1. The package reproduces the mean closely. Its
percentiles differ by a few Mt because the report does not state the iteration
count, random seed or exact PERT implementation. The updated static assessment
must not be confused with the preliminary Havnsø dynamic model in GEUS Report
2020/48.

## Havnsø pressure and injectivity example

```python
from storageeval import (
    Distribution,
    TechnicalScreeningCase,
    simulate_technical_screening,
)

technical_case = TechnicalScreeningCase(
    name="Havnsø – 60 Mt technical screening",
    target_mass_mt=60.0,
    wells=3,
    rate_mtpy_per_well=1.0,
    permeability_factor=Distribution.pert(0.5, 1.0, 2.0),
    initial_pressure_bar=130.0,
    pressure_limit_bar=240.0,
    reference_mass_mt=270.0,
    reference_wells=3,
    reference_rate_mtpy_per_well=1.0,
    reference_net_to_gross=0.5,
)

technical_result = simulate_technical_screening(
    technical_case, result, seed=43
)
print(technical_result.summary())
```

The 60 Mt target is an editable project requirement selected near the updated
GEUS 2023/38 P50 of 62.82 Mt; it is not a GEUS project-design target. The
pressure calculation is a normalized surrogate anchored to the 2020 reference
case (130 bar initial pressure, 3 wells at 1 Mt/year each, 90 years and 270 Mt
at the reported pressure endpoint). Permeability factors 0.5 and 2 reproduce
the direction of the published sensitivities. This workflow is useful for
screening and software development but must be replaced or calibrated with an
updated site-specific dynamic model before project decisions.

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

Run `examples/code_inez.py` to simulate the three Inez reservoirs independently
and add their capacity samples trial by trial. Run
`examples/code_gassum_structure.py` for the standalone Gassum assessment. See
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

site = load_site_csv("examples/data_rodby_inputs.csv", name="Rødby – Bunter Sandstone")
result = simulate(site, iterations=100_000, seed=42)
```

## Scope

Version 0.1 covers static volumetric capacity and a reference-case-normalized
pressure/injectivity screening gate. It does not perform numerical reservoir
simulation, plume migration, geomechanics, well design, leakage-consequence
analysis, or economics.

## License

MIT
