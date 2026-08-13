"""Small standard-library utilities shared by the demonstrations."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Sequence


def mean(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def rmse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    return math.sqrt(mean((a - p) ** 2 for a, p in zip(actual, predicted)))


def mae(actual: Sequence[float], predicted: Sequence[float]) -> float:
    return mean(abs(a - p) for a, p in zip(actual, predicted))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve Ax=b with Gaussian elimination and partial pivoting."""
    n = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        if abs(pivot_value) < 1e-12:
            pivot_value = 1e-12
            augmented[column][column] = pivot_value
        for item in range(column, n + 1):
            augmented[column][item] /= pivot_value
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            for item in range(column, n + 1):
                augmented[row][item] -= factor * augmented[column][item]
    return [augmented[row][n] for row in range(n)]


def fit_ridge(features: Sequence[Sequence[float]], targets: Sequence[float], ridge: float = 0.2) -> list[float]:
    """Fit a tiny ridge model, including an intercept, without external packages."""
    design = [[1.0, *row] for row in features]
    width = len(design[0])
    gram = [[0.0 for _ in range(width)] for _ in range(width)]
    rhs = [0.0 for _ in range(width)]
    for row, target in zip(design, targets):
        for i in range(width):
            rhs[i] += row[i] * target
            for j in range(width):
                gram[i][j] += row[i] * row[j]
    for i in range(1, width):
        gram[i][i] += ridge
    return solve_linear_system(gram, rhs)


def predict_ridge(weights: Sequence[float], features: Sequence[Sequence[float]]) -> list[float]:
    return [weights[0] + sum(w * x for w, x in zip(weights[1:], row)) for row in features]


def write_report(path: str | Path | None, report: dict) -> None:
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
