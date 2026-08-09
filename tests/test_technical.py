import numpy as np
import pytest

from storageeval import (
    Distribution,
    SimulationResult,
    TechnicalScreeningCase,
    simulate_technical_screening,
)


def _capacity_result(capacity_mt=300.0, net_to_gross=0.5, iterations=100):
    return SimulationResult(
        "test",
        np.full(iterations, capacity_mt),
        {"net_to_gross": np.full(iterations, net_to_gross)},
    )


def _havnso_reference(permeability_factor=1.0, target_mass_mt=270.0):
    return TechnicalScreeningCase(
        name="Havnsø reference",
        target_mass_mt=target_mass_mt,
        wells=3,
        rate_mtpy_per_well=1.0,
        permeability_factor=Distribution.constant(permeability_factor),
        initial_pressure_bar=130.0,
        pressure_limit_bar=240.0,
        reference_mass_mt=270.0,
        reference_wells=3,
        reference_rate_mtpy_per_well=1.0,
        reference_net_to_gross=0.5,
    )


def test_havnso_reference_case_reaches_reported_endpoint():
    result = simulate_technical_screening(
        _havnso_reference(), _capacity_result(), seed=42
    )
    assert result.duration_years == pytest.approx(90.0)
    assert np.all(result.final_pressure_bar == pytest.approx(240.0))
    assert np.all(result.injectivity_limit_mtpy_per_well == pytest.approx(1.0))
    assert result.summary()["success_probability"] == pytest.approx(1.0)


def test_half_permeability_fails_pressure_and_injectivity_at_reference_load():
    result = simulate_technical_screening(
        _havnso_reference(permeability_factor=0.5), _capacity_result(), seed=42
    )
    assert np.all(result.final_pressure_bar > 240.0)
    assert not np.any(result.injectivity_pass)
    assert not np.any(result.success)


def test_smaller_target_has_pressure_margin():
    result = simulate_technical_screening(
        _havnso_reference(target_mass_mt=60.0),
        _capacity_result(capacity_mt=65.0, net_to_gross=0.75),
        seed=42,
    )
    assert np.all(result.final_pressure_bar < 240.0)
    assert result.summary()["capacity_pass_probability"] == pytest.approx(1.0)


def test_invalid_pressure_limit_is_rejected():
    case = _havnso_reference()
    invalid = TechnicalScreeningCase(**{**case.__dict__, "pressure_limit_bar": 120.0})
    with pytest.raises(ValueError, match="pressure_limit_bar"):
        simulate_technical_screening(invalid, _capacity_result())
