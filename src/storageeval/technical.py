"""Probabilistic screening of capacity, injectivity, and reservoir pressure.

The model in this module is a transparent surrogate calibrated to a published
dynamic reference case.  It is not a replacement for a numerical reservoir
simulator.
"""

from dataclasses import dataclass

import numpy as np

from .distributions import Distribution
from .simulation import SimulationResult


@dataclass(frozen=True)
class TechnicalScreeningCase:
    """Inputs for a reference-case-normalized technical screening."""

    name: str
    target_mass_mt: float
    wells: int
    rate_mtpy_per_well: float
    permeability_factor: Distribution
    initial_pressure_bar: float
    pressure_limit_bar: float
    reference_mass_mt: float
    reference_wells: int
    reference_rate_mtpy_per_well: float
    reference_net_to_gross: float


@dataclass(frozen=True)
class TechnicalScreeningResult:
    """Iteration-level technical criteria and summary helpers."""

    case_name: str
    target_mass_mt: float
    duration_years: float
    final_pressure_bar: np.ndarray
    injectivity_limit_mtpy_per_well: np.ndarray
    capacity_pass: np.ndarray
    injectivity_pass: np.ndarray
    pressure_pass: np.ndarray
    success: np.ndarray
    inputs: dict[str, np.ndarray]

    def summary(self) -> dict[str, float]:
        return {
            "success_probability": float(np.mean(self.success)),
            "failure_probability": float(1.0 - np.mean(self.success)),
            "capacity_pass_probability": float(np.mean(self.capacity_pass)),
            "injectivity_pass_probability": float(np.mean(self.injectivity_pass)),
            "pressure_pass_probability": float(np.mean(self.pressure_pass)),
            "p90_final_pressure_bar": float(np.percentile(self.final_pressure_bar, 90)),
            "p50_final_pressure_bar": float(np.percentile(self.final_pressure_bar, 50)),
            "p10_final_pressure_bar": float(np.percentile(self.final_pressure_bar, 10)),
        }

    def plot_criteria(self):
        """Plot pass probability for each technical criterion and all combined."""
        import matplotlib.pyplot as plt

        labels = ["Capacity", "Injectivity", "Pressure", "All criteria"]
        probabilities = [
            np.mean(self.capacity_pass),
            np.mean(self.injectivity_pass),
            np.mean(self.pressure_pass),
            np.mean(self.success),
        ]
        colors = ["#4c78a8", "#59a14f", "#f28e2b", "#8f63b8"]
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.bar(labels, probabilities, color=colors)
        for bar, probability in zip(bars, probabilities):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                probability + 0.02,
                f"{probability:.1%}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
        ax.set(
            ylabel="Probability of passing",
            ylim=(0, 1.08),
            title=f"{self.case_name}\nTechnical screening criteria",
        )
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        return fig, ax


def simulate_technical_screening(
    case: TechnicalScreeningCase,
    capacity_result: SimulationResult,
    seed: int | None = None,
) -> TechnicalScreeningResult:
    """Combine static capacity with a normalized pressure/injectivity surrogate.

    The reference case is exactly reproduced when target mass, well count,
    per-well rate, permeability factor, and N/G equal their reference values.
    Pressure demand is scaled by cumulative mass, total field rate, inverse
    permeability factor, and inverse N/G.  The per-well injectivity limit is
    scaled linearly by permeability factor and N/G.
    """
    if case.target_mass_mt <= 0:
        raise ValueError("target_mass_mt must be positive")
    if case.wells <= 0 or case.reference_wells <= 0:
        raise ValueError("well counts must be positive")
    if case.rate_mtpy_per_well <= 0 or case.reference_rate_mtpy_per_well <= 0:
        raise ValueError("injection rates must be positive")
    if not case.initial_pressure_bar < case.pressure_limit_bar:
        raise ValueError("pressure_limit_bar must exceed initial_pressure_bar")
    if case.reference_mass_mt <= 0 or case.reference_net_to_gross <= 0:
        raise ValueError("reference mass and N/G must be positive")

    capacity = np.asarray(capacity_result.capacity_mt, dtype=float)
    if capacity.size == 0:
        raise ValueError("capacity_result must contain iterations")
    try:
        net_to_gross = np.asarray(capacity_result.inputs["net_to_gross"], dtype=float)
    except KeyError as exc:
        raise ValueError("capacity_result must include net_to_gross samples") from exc
    if net_to_gross.shape != capacity.shape or np.any(net_to_gross <= 0):
        raise ValueError("net_to_gross samples must be positive and match capacity")

    rng = np.random.default_rng(seed)
    permeability_factor = case.permeability_factor.sample(rng, capacity.size)
    if np.any(permeability_factor <= 0):
        raise ValueError("permeability_factor samples must be positive")

    field_rate = case.wells * case.rate_mtpy_per_well
    reference_field_rate = case.reference_wells * case.reference_rate_mtpy_per_well
    pressure_demand_ratio = (
        (case.target_mass_mt / case.reference_mass_mt)
        * (field_rate / reference_field_rate)
        / permeability_factor
        * (case.reference_net_to_gross / net_to_gross)
    )
    pressure_increase_reference = case.pressure_limit_bar - case.initial_pressure_bar
    final_pressure = case.initial_pressure_bar + pressure_increase_reference * pressure_demand_ratio

    injectivity_limit = (
        case.reference_rate_mtpy_per_well
        * permeability_factor
        * (net_to_gross / case.reference_net_to_gross)
    )
    capacity_pass = capacity >= case.target_mass_mt
    injectivity_pass = case.rate_mtpy_per_well <= injectivity_limit
    pressure_pass = final_pressure <= case.pressure_limit_bar
    success = capacity_pass & injectivity_pass & pressure_pass

    return TechnicalScreeningResult(
        case_name=case.name,
        target_mass_mt=case.target_mass_mt,
        duration_years=case.target_mass_mt / field_rate,
        final_pressure_bar=final_pressure,
        injectivity_limit_mtpy_per_well=injectivity_limit,
        capacity_pass=capacity_pass,
        injectivity_pass=injectivity_pass,
        pressure_pass=pressure_pass,
        success=success,
        inputs={
            "capacity_mt": capacity,
            "net_to_gross": net_to_gross,
            "permeability_factor": permeability_factor,
        },
    )
