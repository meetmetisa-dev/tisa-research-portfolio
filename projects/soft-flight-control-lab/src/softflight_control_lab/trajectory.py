"""Analytic reference trajectories used by the benchmark."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Reference:
    x: float
    z: float
    vx: float
    vz: float
    ax: float
    az: float


def agile_reference(time_s: float) -> Reference:
    """A smooth horizontal sweep with a double-frequency vertical component."""

    amplitude_x = 1.75
    amplitude_z = 0.48
    frequency = 0.58
    wt = frequency * time_s
    x = amplitude_x * math.sin(wt)
    z = 1.5 + amplitude_z * math.sin(2.0 * wt)
    vx = amplitude_x * frequency * math.cos(wt)
    vz = 2.0 * amplitude_z * frequency * math.cos(2.0 * wt)
    ax = -amplitude_x * frequency**2 * math.sin(wt)
    az = -4.0 * amplitude_z * frequency**2 * math.sin(2.0 * wt)
    return Reference(x, z, vx, vz, ax, az)
