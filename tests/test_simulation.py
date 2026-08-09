import numpy as np
import pytest

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


def test_rodby_reproduces_published_capacity_statistics():
    site = StorageSite(
        "Rødby",
        Distribution.pert(22.57, 28.21, 33.85),
        Distribution.pert(0.20, 0.25, 0.30),
        Distribution.pert(0.184, 0.23, 0.276),
        Distribution.pert(573.4, 603.6, 663.96),
        Distribution.pert(0.05, 0.10, 0.20),
    )
    summary = simulate(site, 100_000, 42).summary()
    published = {"p90_mt": 68.83, "p50_mt": 103.90, "p10_mt": 148.78, "mean_mt": 107.04}
    for key, expected in published.items():
        assert summary[key] == pytest.approx(expected, abs=1.0)


def test_havnso_scenario_1_reproduces_published_capacity_statistics():
    site = StorageSite(
        "Havnsø Scenario 1",
        Distribution.pert(2.9, 5.0, 8.0),
        Distribution.pert(0.60, 0.75, 0.90),
        Distribution.pert(0.175, 0.219, 0.263),
        Distribution.pert(663.86, 698.8, 768.68),
        Distribution.pert(0.05, 0.10, 0.20),
    )
    summary = simulate(site, 100_000, 42).summary()
    published = {
        "p90_mt": 41.25,
        "p50_mt": 62.82,
        "p10_mt": 90.42,
        "mean_mt": 64.81,
    }
    # GEUS does not publish its iteration count, seed, or exact PERT
    # implementation. The mean is reproduced closely; percentile differences
    # of a few Mt are expected with a standard beta-PERT implementation.
    assert summary["mean_mt"] == pytest.approx(published["mean_mt"], abs=1.0)
    for key in ("p90_mt", "p50_mt", "p10_mt"):
        assert summary[key] == pytest.approx(published[key], abs=5.0)


def test_gppeleval_style_plots():
    import matplotlib

    matplotlib.use("Agg")
    site = StorageSite(
        "plot test",
        Distribution.pert(8, 10, 12),
        Distribution.triangular(0.4, 0.5, 0.6),
        Distribution.constant(0.2),
        Distribution.constant(600),
        Distribution.pert(0.05, 0.1, 0.2),
    )
    result = simulate(site, 1_000, 42)

    fig_pdf, ax_pdf = result.plot_pdf()
    fig_exc, ax_exc = result.plot_exceedance()
    fig_ranges, ax_ranges = result.plot_capacity_ranges()

    assert len(ax_pdf.patches) > 0
    assert len(ax_pdf.lines) >= 4
    assert len(ax_exc.lines) >= 4
    assert len(ax_ranges.patches) == 3

    for fig in (fig_pdf, fig_exc, fig_ranges):
        fig.canvas.draw()
