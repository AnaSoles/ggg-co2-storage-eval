"""Monte Carlo engine and result summaries."""

from dataclasses import dataclass

import numpy as np

from .site import StorageSite


@dataclass(frozen=True)
class SimulationResult:
    site_name: str
    capacity_mt: np.ndarray
    inputs: dict[str, np.ndarray]

    def summary(self) -> dict[str, float]:
        """Return mean and exceedance probabilities used in storage studies.

        P90 is the low (10th-percentile) estimate and P10 is the high
        (90th-percentile) estimate.
        """
        q10, q50, q90 = np.percentile(self.capacity_mt, [10, 50, 90])
        return {
            "mean_mt": float(np.mean(self.capacity_mt)),
            "p90_mt": float(q10),
            "p50_mt": float(q50),
            "p10_mt": float(q90),
        }

    def sensitivity(self) -> dict[str, float]:
        """Return rank correlations between each input and capacity."""
        output_rank = np.argsort(np.argsort(self.capacity_mt))
        correlations: dict[str, float] = {}
        for name, values in self.inputs.items():
            input_rank = np.argsort(np.argsort(values))
            correlations[name] = float(np.corrcoef(input_rank, output_rank)[0, 1])
        return correlations

    def plot_distribution(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.hist(self.capacity_mt, bins=50, density=True, alpha=0.8)
        ax.set(xlabel="Storage capacity (Mt CO2)", ylabel="Probability density", title=self.site_name)
        return fig, ax

    def plot_exceedance(self):
        import matplotlib.pyplot as plt

        capacity = np.sort(self.capacity_mt)
        exceedance = 1 - np.arange(1, capacity.size + 1) / (capacity.size + 1)
        fig, ax = plt.subplots()
        ax.plot(capacity, exceedance * 100)
        ax.set(xlabel="Storage capacity (Mt CO2)", ylabel="Exceedance probability (%)", title=self.site_name)
        ax.grid(alpha=0.25)
        return fig, ax

    def plot_sensitivity(self):
        """Plot rank-correlation sensitivities as a horizontal tornado chart."""
        import matplotlib.pyplot as plt

        correlations = self.sensitivity()
        names, values = zip(*sorted(correlations.items(), key=lambda item: abs(item[1])))
        colors = ["#2a6fbb" if value >= 0 else "#c75146" for value in values]
        fig, ax = plt.subplots()
        ax.barh(names, values, color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set(
            xlabel="Spearman rank correlation",
            title=f"{self.site_name} input sensitivity",
            xlim=(-1, 1),
        )
        fig.tight_layout()
        return fig, ax


def simulate(site: StorageSite, iterations: int = 10_000, seed: int | None = None) -> SimulationResult:
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    rng = np.random.default_rng(seed)
    distributions = {
        "grv_km3": site.grv,
        "net_to_gross": site.net_to_gross,
        "porosity": site.porosity,
        "co2_density_kg_m3": site.co2_density,
        "storage_efficiency": site.storage_efficiency,
    }
    inputs = {name: distribution.sample(rng, iterations) for name, distribution in distributions.items()}
    capacity = (
        inputs["grv_km3"]
        * inputs["net_to_gross"]
        * inputs["porosity"]
        * inputs["co2_density_kg_m3"]
        * inputs["storage_efficiency"]
    )
    return SimulationResult(site.name, capacity, inputs)
