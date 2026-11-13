# Task A — uncertainty-based *candidate* indifference threshold q

## Research objective

**How to derive scientifically justified indifference (q) and preference (p) thresholds for CO₂ storage capacity in PROMETHEE.**

We aim to establish a reproducible procedure that can be applied to multiple CO₂ storage sites and assess whether it is sufficiently robust for implementation in the CO2SITE platform.

## What the repository already computes

`simulate(site, iterations, seed)` generates a `SimulationResult` whose
`capacity_mt` array contains one possible static storage-capacity value per
Monte Carlo realisation. The model uses the site's GRV, net-to-gross, porosity,
CO₂ density and storage efficiency input distributions. We **do not** alter it.

## Task A workflow

1. Run each site's original static-capacity Monte Carlo model.
2. Preserve every site's `capacity_mt` array, **not only** P90/P50/P10.
3. For each pair of sites A and B, estimate the probability distribution of
   `difference = capacity_B - capacity_A`.
4. Estimate `P(B > A)` as the proportion of positive differences and
   `P(A > B)` analogously. These are *model-implied probabilities*, conditional
   on the input assumptions, not empirical evidence of geological superiority.
5. Summarise the difference distribution's mean, standard deviation and a
   central interval (default 95%). The exploratory per-pair uncertainty width
   is **half the width of this interval**.
6. For many sites, list all per-pair widths and compute a clearly labelled
   illustrative common-q diagnostic (default 75th percentile). A common q
   becomes a proposal only after sensitivity analysis and domain validation.

### Simple hand calculation

Illustrative simulated pairs (Mt):

| Draw | Site A | Site B | B − A |
|---|---:|---:|---:|
| 1 | 95 | 110 | 15 |
| 2 | 108 | 102 | -6 |
| 3 | 100 | 120 | 20 |
| 4 | 112 | 105 | -7 |
| 5 | 90 | 115 | 25 |

Here `P(B>A) = 3/5 = 60%`. These five draws are not sufficient to
calibrate a real threshold.

### Important assumptions and limitations

- The default comparison assumes **independent site distributions** and
  independently resamples each site's existing Monte Carlo values. Pairwise
  subtraction of the same original iteration index is only valid when samples
  were explicitly generated jointly and preserve the intended cross-site
  dependence; a shared random seed alone does not establish that.
- If sites share systematic geological uncertainty (e.g., storage efficiency
  assumptions), specify and simulate their joint dependence before using the
  paired-draw mode.
- A simulated capacity distribution describes **model/input uncertainty**
  and is not automatically a measurement-error distribution or a sampling
  distribution for an estimated mean.
- The central difference interval is not a classical *confidence interval for
  the mean*. A 95% interval can be interpreted as a model-based uncertainty
  interval only if the underlying Monte Carlo inputs justify that.
- In PROMETHEE, q is a *decision indifference threshold*, **not a statistical
  standard deviation, significance cutoff, or confidence limit**. The
  interval-half-width and common-q quantile implemented here are exploratory
  rules only; their physical interpretation and acceptability require
  additional evidence, expert elicitation and sensitivity analysis.
- In particular, q derived separately for site pairs does not directly fit
  the ordinary PROMETHEE model with a single q per criterion. A common q may
  misrepresent strongly heterogeneous uncertainty across sites.
- This is Task A only; it does not calculate the preference threshold **p**.
  The q/p choice requires Task B and subsequent robustness tests.
- Static volumetric capacity does not substitute for dynamic, pressure- or
  injectivity-constrained storage capacity.

## Run

```bash
python -m pip install -e ".[dev]"
python examples/task_a_capacity_indifference.py
pytest tests/test_indifference.py
```

Outputs `examples/task_a_pair_comparisons.csv` (generated locally) and prints
per-site SDs, pairwise probabilities and provisional candidate q diagnostics.
The CSV is intentionally not committed. All examples use existing GEUS-derived
CSV inputs and constitute *demonstration analyses*, not a final CO2SITE decision
rule.
