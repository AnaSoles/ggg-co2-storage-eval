"""Storage-site input model."""

from dataclasses import dataclass

from .distributions import Distribution


@dataclass(frozen=True)
class StorageSite:
    name: str
    grv: Distribution
    net_to_gross: Distribution
    porosity: Distribution
    co2_density: Distribution
    storage_efficiency: Distribution

