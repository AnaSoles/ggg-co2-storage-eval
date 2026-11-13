"""Task A: exploratory uncertainty diagnostics for PROMETHEE capacity q.

This module does NOT claim that statistical uncertainty uniquely determines a
decision-maker's indifference threshold. All q values are candidate rules.
"""
from __future__ import annotations

from itertools import combinations
import numpy as np

from .simulation import SimulationResult


def _capacities(result: SimulationResult) -> np.ndarray:
    a = np.asarray(result.capacity_mt, dtype=float)
    if a.ndim != 1 or len(a) < 2 or not np.all(np.isfinite(a)):
        raise ValueError("Each site needs at least two finite simulated capacities.")
    return a


def compare_capacity_samples(
    first: SimulationResult,
    second: SimulationResult,
    *,
    independent: bool = True,
    seed: int = 2026,
    draws: int | None = None,
    confidence: float = 0.95,
) -> dict[str, float | str]:
    """Compare capacity distributions; difference = second minus first (Mt).

    independent=True randomly samples *independently with replacement* from
    each site's empirical Monte Carlo distribution, using a reproducible seed.
    independent=False pairs indices and therefore requires equal-length,
    deliberately JOINTLY generated samples preserving dependence. Never use
    that mode simply because simulations happened to share a random seed.

    q_pair_candidate_mt is an illustrative uncertainty-width rule: half the
    central confidence interval width of the difference distribution. It is
    NOT a statistical confidence interval for the mean difference, a
    hypothesis test, nor a uniquely justified PROMETHEE q.
    """
    if first.site_name == second.site_name:
        raise ValueError("Compare distinct named sites.")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1).")
    a, b = _capacities(first), _capacities(second)
    if draws is None:
        draws = max(len(a), len(b))
    if not isinstance(draws, int) or draws < 2:
        raise ValueError("draws must be an integer >= 2.")
    if independent:
        rng = np.random.default_rng(seed)
        # Independent resampling also avoids spurious association from a shared seed.
        diffs = b[rng.integers(0, len(b), draws)] - a[rng.integers(0, len(a), draws)]
    else:
        if len(a) != len(b) or draws != len(a):
            raise ValueError("Joint draws require equal arrays and draws equal to their length.")
        diffs = b - a
    alpha = (1 - confidence) / 2
    lower, upper = np.quantile(diffs, [alpha, 1 - alpha])
    return {
        "first_site": first.site_name,
        "second_site": second.site_name,
        "draws": draws,
        "assumption": "independent empirical resampling" if independent else "jointly paired draws",
        "mean_difference_mt": float(diffs.mean()),
        "std_difference_mt": float(diffs.std(ddof=1)),
        "lower_difference_mt": float(lower),
        "upper_difference_mt": float(upper),
        "prob_second_greater": float(np.mean(diffs > 0)),
        "prob_first_greater": float(np.mean(diffs < 0)),
        "prob_equal": float(np.mean(diffs == 0)),
        "q_pair_candidate_mt": float((upper - lower) / 2),
    }


def compare_all_sites(
    results: list[SimulationResult],
    *,
    confidence: float = 0.95,
    seed: int = 2026,
) -> list[dict[str, float | str]]:
    """All site pairs: names must be unique. Default assumes independent sites."""
    if len({r.site_name for r in results}) != len(results):
        raise ValueError("Site names must be unique.")
    return [
        compare_capacity_samples(a, b, confidence=confidence, seed=seed + k)
        for k, (a, b) in enumerate(combinations(results, 2))
    ]


def common_q_diagnostics(
    pair_results: list[dict[str, float | str]],
    *,
    quantile: float = 0.75,
) -> dict[str, float]:
    """Exploratory common q: selected quantile of per-pair half interval widths.

    Data-derived heuristic, NOT an established general rule for PROMETHEE.
    This choice must be justified, tested for sensitivity and validated with
    expert preferences. May be unsuitable for heterogeneous storage sites.
    """
    if not pair_results or not 0 <= quantile <= 1:
        raise ValueError("Need pairs and quantile in [0, 1].")
    q = np.array([float(r["q_pair_candidate_mt"]) for r in pair_results])
    return {
        "pair_count": int(len(q)),
        "quantile_used": float(quantile),
        "common_q_candidate_mt": float(np.quantile(q, quantile)),
        "min_pair_q_mt": float(q.min()),
        "max_pair_q_mt": float(q.max()),
    }
