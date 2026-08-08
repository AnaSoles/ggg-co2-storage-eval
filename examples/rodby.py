"""Rødby Bunter Sandstone example based on the GEUS assessment inputs."""

from storageeval import Distribution, StorageSite, simulate

site = StorageSite(
    name="Rødby – Bunter Sandstone",
    grv=Distribution.pert(22.57, 28.21, 33.85),
    net_to_gross=Distribution.pert(0.20, 0.25, 0.30),
    porosity=Distribution.pert(0.184, 0.23, 0.276),
    co2_density=Distribution.pert(573.4, 603.6, 764.0),
    storage_efficiency=Distribution.pert(0.05, 0.10, 0.20),
)

result = simulate(site, iterations=100_000, seed=42)
print(result.summary())
print(result.sensitivity())

