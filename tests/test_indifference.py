"""Tests of exploratory capacity distribution comparisons."""
import numpy as np
import pytest

from storageeval.simulation import SimulationResult
from storageeval.indifference import (
    compare_capacity_samples, compare_all_sites, common_q_diagnostics
)


def result(name, values):
    return SimulationResult(name, np.array(values, dtype=float), {})


def test_constant_difference_probability_and_width():
    a = result("A", [100] * 20)
    b = result("B", [120] * 20)
    d = compare_capacity_samples(a, b, seed=1)
    assert d["mean_difference_mt"] == pytest.approx(20)
    assert d["prob_second_greater"] == pytest.approx(1)
    assert d["q_pair_candidate_mt"] == pytest.approx(0)


def test_independent_sampling_reproducible():
    a = result("A", [90, 100, 110, 120])
    b = result("B", [95, 105, 115, 125])
    assert compare_capacity_samples(a, b, seed=12, draws=1000) == (
        compare_capacity_samples(a, b, seed=12, draws=1000)
    )


def test_joint_requires_suitable_lengths():
    a = result("A", [1, 2, 3])
    b = result("B", [2, 3, 4])
    d = compare_capacity_samples(a, b, independent=False)
    assert d["mean_difference_mt"] == pytest.approx(1)
    with pytest.raises(ValueError):
        compare_capacity_samples(a, result("C", [2, 3]), independent=False)


def test_all_pairs_common_diagnostic():
    sites = [result("A", [1, 2, 3]), result("B", [2, 3, 4]),
             result("C", [5, 6, 7])]
    pairs = compare_all_sites(sites, seed=7)
    assert len(pairs) == 3
    common = common_q_diagnostics(pairs, quantile=0.5)
    assert common["pair_count"] == 3
    assert common["min_pair_q_mt"] <= common["common_q_candidate_mt"] <= common["max_pair_q_mt"]
