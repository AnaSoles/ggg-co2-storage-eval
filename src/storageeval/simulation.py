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

    def plot_distribution(self, bins: int = 50, fitted: bool = True):
        """Plot the simulated capacity PDF and an optional lognormal fit.

        The percentile markers follow storage-industry exceedance notation:
        P90 is conservative, P50 is the median, and P10 is the upside case.
        """
        import matplotlib.pyplot as plt

        values = np.asarray(self.capacity_mt, dtype=float)
        summary = self.summary()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(
            values,
            bins=bins,
            density=True,
            color="#35b779",
            edgecolor="white",
            linewidth=0.35,
            alpha=0.9,
            label="Simulated",
        )

        if fitted and np.all(values > 0):
            log_values = np.log(values)
            sigma = float(np.std(log_values, ddof=1))
            if sigma > 0:
                mu = float(np.mean(log_values))
                x = np.linspace(float(np.min(values)), float(np.max(values)), 500)
                density = np.exp(-0.5 * ((np.log(x) - mu) / sigma) ** 2) / (
                    x * sigma * np.sqrt(2 * np.pi)
                )
                ax.plot(x, density, color="#e63946", linewidth=2.2, label="Fitted lognormal")

        markers = [
            ("P90", summary["p90_mt"], "#e76f51"),
            ("P50", summary["p50_mt"], "#3a86ff"),
            ("P10", summary["p10_mt"], "#d4a900"),
        ]
        for label, value, color in markers:
            ax.axvline(value, color=color, linestyle="--", linewidth=1.6)
            ax.annotate(
                f"{label} = {value:.1f} Mt",
                xy=(value, 0.96),
                xycoords=("data", "axes fraction"),
                xytext=(4, 0),
                textcoords="offset points",
                color=color,
                rotation=90,
                va="top",
                ha="left",
            )

        ax.set(
            xlabel="Storage capacity (Mt CO₂)",
            ylabel="Probability density",
            title=f"{self.site_name}\nStorage-capacity probability distribution",
        )
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        return fig, ax

    def plot_pdf(self, bins: int = 50, fitted: bool = True):
        """Alias for :meth:`plot_distribution`, matching the gppeval style."""
        return self.plot_distribution(bins=bins, fitted=fitted)

    def plot_exceedance(self):
        import matplotlib.pyplot as plt

        capacity = np.sort(np.asarray(self.capacity_mt, dtype=float))
        exceedance = 1 - np.arange(1, capacity.size + 1) / (capacity.size + 1)
        summary = self.summary()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.step(capacity, exceedance, where="post", color="#e63946", linewidth=1.8, label="Simulated")
        for probability, key, color in [
            (0.90, "p90_mt", "#e76f51"),
            (0.50, "p50_mt", "#3a86ff"),
            (0.10, "p10_mt", "#d4a900"),
        ]:
            value = summary[key]
            label = key[:3].upper()
            ax.vlines(value, 0, probability, color=color, linestyle="--", linewidth=1.5)
            ax.hlines(probability, capacity[0], value, color=color, linestyle=":", linewidth=1.0)
            ax.plot(value, probability, "o", color=color, markersize=5)
            ax.annotate(
                f"{label} = {value:.1f} Mt",
                (value, probability),
                xytext=(6, 6),
                textcoords="offset points",
                color=color,
            )
        ax.set(
            xlabel="Storage capacity (Mt CO₂)",
            ylabel="Probability capacity is exceeded",
            title=f"{self.site_name}\nStorage-capacity exceedance curve",
            ylim=(0, 1),
        )
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        return fig, ax

    def plot_capacity_ranges(self):
        """Plot conservative, central, and upside capacity ranges linearly."""
        import matplotlib.pyplot as plt

        summary = self.summary()
        p90, p50, p10 = summary["p90_mt"], summary["p50_mt"], summary["p10_mt"]
        segments = [
            (0.0, p90, "#2e7d32", "Conservative\n≥90% exceedance"),
            (p90, p50, "#f5a000", "Central range\n50–90% exceedance"),
            (p50, p10, "#ff654f", "Upside range\n10–50% exceedance"),
        ]

        fig, ax = plt.subplots(figsize=(12, 2.8))
        for left, right, color, label in segments:
            width = right - left
            ax.barh(0, width, left=left, height=0.55, color=color, edgecolor="#333333")
            ax.text(left + width / 2, 0, label, ha="center", va="center", fontsize=9)

        for label, value in [("P90", p90), ("P50", p50), ("P10", p10)]:
            ax.axvline(value, ymin=0.12, ymax=0.88, color="#333333", linewidth=1)
            ax.text(value, -0.43, f"{label}\n{value:.1f} Mt", ha="center", va="top", fontsize=9)

        ax.set(
            xlabel="Storage capacity (Mt CO₂)",
            title=f"{self.site_name} – capacity confidence ranges",
            yticks=[],
            xlim=(0, p10 * 1.04),
            ylim=(-0.65, 0.65),
        )
        for spine in ("left", "right", "top"):
            ax.spines[spine].set_visible(False)
        fig.tight_layout()
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
