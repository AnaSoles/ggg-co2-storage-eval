"""CSV input helpers."""

from __future__ import annotations

import csv
from pathlib import Path

from .distributions import Distribution
from .site import StorageSite


_PARAMETER_NAMES = {
    "gross_rock_volume": "grv",
    "grv": "grv",
    "net_to_gross": "net_to_gross",
    "porosity": "porosity",
    "co2_density": "co2_density",
    "storage_efficiency": "storage_efficiency",
}


def _optional_float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "").strip()
    return float(value) if value else None


def _distribution_from_row(row: dict[str, str]) -> Distribution:
    kind = row["distribution"].strip().lower()
    if kind in {"pert", "triangular"}:
        values = (_optional_float(row, "minimum"), _optional_float(row, "mode"), _optional_float(row, "maximum"))
        if any(value is None for value in values):
            raise ValueError(f"{kind} requires minimum, mode, and maximum")
        constructor = Distribution.pert if kind == "pert" else Distribution.triangular
        return constructor(*values)  # type: ignore[arg-type]
    if kind == "constant":
        value = _optional_float(row, "value")
        if value is None:
            value = _optional_float(row, "mode")
        if value is None:
            raise ValueError("constant requires value (or mode)")
        return Distribution.constant(value)
    if kind in {"normal", "lognormal"}:
        mean, std = _optional_float(row, "mean"), _optional_float(row, "std")
        if mean is None or std is None:
            raise ValueError(f"{kind} requires mean and std")
        constructor = Distribution.normal if kind == "normal" else Distribution.lognormal
        return constructor(mean, std)
    raise ValueError(f"Unsupported distribution: {kind}")


def load_site_csv(path: str | Path, name: str | None = None) -> StorageSite:
    """Load the five required storage-capacity inputs from a CSV file."""
    parameters: dict[str, Distribution] = {}
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source_name = row.get("parameter", "").strip().lower()
            try:
                parameter_name = _PARAMETER_NAMES[source_name]
            except KeyError as exc:
                raise ValueError(f"Unknown parameter: {source_name}") from exc
            parameters[parameter_name] = _distribution_from_row(row)

    required = {"grv", "net_to_gross", "porosity", "co2_density", "storage_efficiency"}
    missing = sorted(required - parameters.keys())
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    return StorageSite(name or Path(path).stem, **parameters)
