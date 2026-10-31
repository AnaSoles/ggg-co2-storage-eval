"""Tests for the independent MCDM example."""
import importlib.util
from pathlib import Path
import pytest

path = Path(__file__).resolve().parents[1] / "examples" / "mcdm_weight_sensitivity.py"
spec = importlib.util.spec_from_file_location("mcdm_weight_sensitivity", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_baseline():
    values = m.weighted_scores(m.BASE_WEIGHTS)
    assert values["Site A"] == pytest.approx(3.55)
    assert values["Site B"] == pytest.approx(3.95)
    assert values["Site C"] == pytest.approx(3.55)
    assert m.ranking(values) == ["Site B", "Site A", "Site C"]


@pytest.mark.parametrize("index", range(3))
@pytest.mark.parametrize("new_weight", [0.0, 0.2, 0.5, 1.0])
def test_weight_sums(index, new_weight):
    weights = m.vary_one_weight(m.BASE_WEIGHTS, index, new_weight)
    assert sum(weights) == pytest.approx(1.0)
    assert weights[index] == pytest.approx(new_weight)
    assert all(w >= 0 for w in weights)


def test_grid():
    rows = m.sensitivity_rows()
    assert len(rows) == 63
    assert any(not row["same_ranking_as_baseline"] for row in rows)
