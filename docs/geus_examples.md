# GEUS storage-capacity examples

The input CSV files reproduce the static volumetric assessments in two GEUS
reports using independent beta-PERT distributions:

```text
SC = GRV × N/G × porosity × CO2 density × storage efficiency
```

## Havnsø main study

The main Havnsø example uses **Scenario 1** for the Gassum Formation from
[GEUS Report 2023/38](https://doi.org/10.22008/gpub/34705), input Table 8.2.3
(report page 152) and results Table 8.3.1 (report page 154). It is the updated
static assessment based on the 2022 seismic survey and replaces the older 2020
static inputs as the project's primary Havnsø capacity case.

The published inputs are independent PERT distributions:

| Parameter | Minimum | Mode | Maximum |
|---|---:|---:|---:|
| GRV (km3) | 2.9 | 5.0 | 8.0 |
| Net-to-gross | 0.60 | 0.75 | 0.90 |
| Porosity | 0.175 | 0.219 | 0.263 |
| CO2 density (kg/m3) | 663.86 | 698.8 | 768.68 |
| Storage efficiency | 0.05 | 0.10 | 0.20 |

GEUS publishes P90 41.25, P50 62.82, P10 90.42 and mean 64.81 Mt CO2. A
standard beta-PERT implementation closely reproduces the mean, while the
percentiles differ by a few Mt because the report does not document its exact
PERT implementation, iteration count or random seed.

Report 2023/38 also defines Scenarios 2 and 3. Scenario 3's input Table 8.2.5
prints net-to-gross as `0.60 / 0.33 / 0.90`, which is not a valid PERT ordering
and conflicts with the report's stated approximately ±20% rule. The main
notebook therefore uses Scenario 1 only and does not silently correct or sample
the Scenario 3 typo.

The preliminary dynamic simulation in
[GEUS Report 2020/48](https://data.geus.dk/pure-pdf/GEUS-R_2020_48_web.pdf)
is retained as separate evidence for the later technical-risk workflow. Its
approximately 270 Mt result belongs to a different version-0 model and must not
be used as the validation target for this updated static notebook.

## Inez

Inez has three assessed reservoirs: Haldager Sand, Gassum Formation, and
Skagerrak Formation. Each reservoir is simulated independently. The three
capacity samples are then added trial by trial to form the combined Inez
distribution. Percentiles must be calculated from that combined distribution;
the individual P90/P50/P10 values must not be added.

Source: [GEUS Report 2022/29](https://data.geus.dk/pure-pdf/GEUS-R_2022-29_web.pdf),
input Tables 8.1.5.1–8.1.5.3 (report page 44) and results Tables 8.2.1–8.2.4
(report page 46).

The reservoir-specific Gassum input table gives storage efficiency as
`PERT(0.05, 0.07, 0.15)`. Here, `0.07` is the mode—the most likely input—not a
capacity percentile and not a factor applied after the simulation. The general
method text mentions 10%, but using the table-specific 7% mode reproduces the
published reservoir result; using 10% does not.

The detailed combined results table reports a mean of 224.8 Mt CO2. This is
used as the validation target rather than the earlier summary value near
214 Mt CO2.

## Standalone Gassum structure

This example is the onshore Gassum structure, not the Gassum Formation interval
inside Inez.

Source: [GEUS Report 2024/25](https://data.geus.dk/pure-pdf/GEUS-R_2024-25_web.pdf),
input Table 8.4.1 (report page 130) and results Table 8.5.1 (report page 131).

## Meaning of the PERT mode

For `PERT(minimum, mode, maximum)`, the mode is the most likely value and shapes
where sampled values concentrate. Every Monte Carlo trial samples each input,
uses the sampled values in the capacity equation, and produces one capacity.
After all trials, the capacity results are sorted to derive P90, P50, and P10.
