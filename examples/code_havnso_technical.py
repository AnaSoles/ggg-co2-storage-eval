"""Havnsø capacity + pressure + injectivity screening example."""

from storageeval import (
    Distribution,
    StorageSite,
    TechnicalScreeningCase,
    simulate,
    simulate_technical_screening,
)


site = StorageSite(
    name="Havnsø – Gassum Formation – Scenario 1",
    grv=Distribution.pert(2.9, 5.0, 8.0),
    net_to_gross=Distribution.pert(0.60, 0.75, 0.90),
    porosity=Distribution.pert(0.175, 0.219, 0.263),
    co2_density=Distribution.pert(663.86, 698.8, 768.68),
    storage_efficiency=Distribution.pert(0.05, 0.10, 0.20),
)
capacity_result = simulate(site, iterations=100_000, seed=42)

case = TechnicalScreeningCase(
    name="Havnsø – 60 Mt technical screening",
    target_mass_mt=60.0,
    wells=3,
    rate_mtpy_per_well=1.0,
    permeability_factor=Distribution.pert(0.5, 1.0, 2.0),
    initial_pressure_bar=130.0,
    pressure_limit_bar=240.0,
    reference_mass_mt=270.0,
    reference_wells=3,
    reference_rate_mtpy_per_well=1.0,
    reference_net_to_gross=0.5,
)
technical_result = simulate_technical_screening(case, capacity_result, seed=43)
print(capacity_result.summary())
print(technical_result.summary())
