# Illustrative MCDM weight sensitivity (Dean 2022)

This is a **standalone teaching example**, not an assessment of real CO2 storage sites and not integrated into the project's storage-capacity simulator.

**Reference:** Marco Dean (2022), *A Practical Guide to Multi-Criteria Analysis*, §5.8, pp. 69–71. Dean discusses one-parameter-at-a-time sensitivity tests on scores and weights (Figure 31) and scenario-based approaches (Table 18). The particular numerical example and proportional rescaling convention are implementation choices here, not values reported by Dean.

## Run

From the repository root:

```bash
python examples/mcdm_weight_sensitivity.py
```

This writes `examples/mcdm_sensitivity_results.csv` locally (not tracked) with 63 tests: 3 criteria × 21 tested weights (0%, 5%, ... 100%). Use any spreadsheet to plot `tested_weight` against the three site-score columns, separately for each `criterion_varied`.

To run the automated tests (requires pytest, available with the project's dev extras):

```bash
pytest tests/test_mcdm_weight_sensitivity.py
```

## Example inputs — deliberately fictional

| Site | Capacity | Injectivity | Storage cost |
| --- | ---: | ---: | ---: |
| A | 5 | 3 | 2 |
| B | 3 | 5 | 4 |
| C | 4 | 2 | 5 |
| Baseline weights | 40% | 35% | 25% |

All scores use 1–5 with **5 = most desirable**. Storage-cost scores are already inverted: 5 means low cost and 1 high cost. The baseline weighted totals are A = 3.55, B = 3.95, C = 3.55; A and C are tied.

## Method

Weighted sum: `S(site) = sum(weight[j] * score[site,j])`. For one-at-a-time sensitivity, set weight `j` to `t`, then multiply each other baseline weight by `(1-t)/(1-original_weight[j])`, preserving their relative ratio and the total of 100%.

For each test the CSV records weights, scores, display ranking, co-winners (to represent first-place ties), and whether the display ranking differs from the baseline. **Be careful:** the display ranking alphabetically breaks score ties for stable output; this ordering does not establish strict preference between tied sites.

## Limits and next steps

- Weighted sums are compensatory. Safety and regulatory veto criteria should be handled separately before ranking.
- Independence, scoring-scale comparability, and double-counting assumptions require review.
- The step size is 5 percentage points; observed change points are grid-dependent, not exact thresholds.
- This tests **weights only**, not uncertainty in geological inputs or score thresholds. Dean §5.8 also discusses changing scores and scenario-based analysis; those could be added later.
- Do not mistake these fictitious 1–5 scores for EGDI data or technical site evidence.
