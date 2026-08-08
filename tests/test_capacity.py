import pytest

from storageeval import capacity_mt


def test_capacity_units_cancel_to_mt():
    assert capacity_mt(28.21, 0.25, 0.23, 603.6, 0.10) == pytest.approx(97.908447)


def test_fraction_validation():
    with pytest.raises(ValueError):
        capacity_mt(28.21, 25, 0.23, 603.6, 0.10)
