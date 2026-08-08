"""Deterministic storage-capacity calculations."""


def capacity_mt(
    grv_km3: float,
    net_to_gross: float,
    porosity: float,
    co2_density_kg_m3: float,
    storage_efficiency: float,
) -> float:
    """Return static CO2 storage capacity in million tonnes (Mt).

    With GRV in km3 and density in kg/m3, the 1e9 volume conversion and
    1e9 kg/Mt mass conversion cancel numerically.
    """
    values = {
        "grv_km3": grv_km3,
        "net_to_gross": net_to_gross,
        "porosity": porosity,
        "co2_density_kg_m3": co2_density_kg_m3,
        "storage_efficiency": storage_efficiency,
    }
    if any(value < 0 for value in values.values()):
        raise ValueError("Capacity inputs must be non-negative")
    for name in ("net_to_gross", "porosity", "storage_efficiency"):
        if values[name] > 1:
            raise ValueError(f"{name} must be a decimal fraction between 0 and 1")

    return grv_km3 * net_to_gross * porosity * co2_density_kg_m3 * storage_efficiency

