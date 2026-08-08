"""Input probability distributions."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Distribution:
    """A scalar constant, triangular, PERT, normal, or lognormal input."""

    kind: str
    minimum: float | None = None
    mode: float | None = None
    maximum: float | None = None
    mean: float | None = None
    std: float | None = None
    value: float | None = None
    shape: float = 4.0

    @classmethod
    def constant(cls, value: float) -> "Distribution":
        return cls("constant", value=value)

    @classmethod
    def triangular(cls, minimum: float, mode: float, maximum: float) -> "Distribution":
        return cls("triangular", minimum=minimum, mode=mode, maximum=maximum)

    @classmethod
    def pert(
        cls, minimum: float, mode: float, maximum: float, shape: float = 4.0
    ) -> "Distribution":
        return cls("pert", minimum=minimum, mode=mode, maximum=maximum, shape=shape)

    @classmethod
    def normal(cls, mean: float, std: float) -> "Distribution":
        return cls("normal", mean=mean, std=std)

    @classmethod
    def lognormal(cls, mean: float, std: float) -> "Distribution":
        """Create a lognormal using mean/std in natural-log space."""
        return cls("lognormal", mean=mean, std=std)

    def sample(self, rng: np.random.Generator, size: int) -> np.ndarray:
        kind = self.kind.lower()
        if kind == "constant":
            if self.value is None:
                raise ValueError("constant requires value")
            return np.full(size, self.value, dtype=float)
        if kind in {"triangular", "pert"}:
            if self.minimum is None or self.mode is None or self.maximum is None:
                raise ValueError(f"{kind} requires minimum, mode, and maximum")
            if not self.minimum <= self.mode <= self.maximum:
                raise ValueError("Expected minimum <= mode <= maximum")
            if self.minimum == self.maximum:
                return np.full(size, self.minimum, dtype=float)
            if kind == "triangular":
                return rng.triangular(self.minimum, self.mode, self.maximum, size)
            if self.shape <= 0:
                raise ValueError("PERT shape must be positive")
            span = self.maximum - self.minimum
            alpha = 1 + self.shape * (self.mode - self.minimum) / span
            beta = 1 + self.shape * (self.maximum - self.mode) / span
            return self.minimum + rng.beta(alpha, beta, size) * span
        if kind in {"normal", "lognormal"}:
            if self.mean is None or self.std is None or self.std < 0:
                raise ValueError(f"{kind} requires mean and a non-negative std")
            sampler = rng.normal if kind == "normal" else rng.lognormal
            return sampler(self.mean, self.std, size)
        raise ValueError(f"Unsupported distribution: {self.kind}")

