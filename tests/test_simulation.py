import numpy as np

from storageeval import Distribution, StorageSite, simulate


def test_constant_simulation():
    site = StorageSite(
        "constant",
        Distribution.constant(10),
        Distribution.constant(0.5),
        Distribution.constant(0.2),
        Distribution.constant(600),
        Distribution.constant(0.1),
    )
    result = simulate(site, iterations=100, seed=7)
    assert np.all(result.capacity_mt == 60)
    assert result.summary() == {"mean_mt": 60.0, "p90_mt": 60.0, "p50_mt": 60.0, "p10_mt": 60.0}


def test_seed_is_reproducible():
    site = StorageSite(
        "test",
        Distribution.pert(8, 10, 12),
        Distribution.triangular(0.4, 0.5, 0.6),
        Distribution.constant(0.2),
        Distribution.constant(600),
        Distribution.constant(0.1),
    )
    assert np.array_equal(simulate(site, 100, 42).capacity_mt, simulate(site, 100, 42).capacity_mt)

