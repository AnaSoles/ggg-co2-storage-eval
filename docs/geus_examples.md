# GEUS Inez and Gassum examples

The input CSV files reproduce the static volumetric assessments in two GEUS
reports using independent beta-PERT distributions:

```text
SC = GRV × N/G × porosity × CO2 density × storage efficiency
```

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
