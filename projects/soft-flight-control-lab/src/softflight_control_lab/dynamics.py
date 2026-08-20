"""Reduced-order planar dynamics for a deformable thrust-vectoring aircraft.

The equations deliberately expose model mismatch while remaining small enough
to audit. They are a synthetic benchmark, not an identified vehicle model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Dict


GRAVITY = 9.81


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


@dataclass(frozen=True)
class State:
    x: float = 0.0
    z: float = 1.5
    vx: float = 0.0
    vz: float = 0.0
    theta: float = 0.0
    omega: float = 0.0
    q: float = 0.0
    qdot: float = 0.0


@dataclass(frozen=True)
class Control:
    thrust: float
    torque: float


@dataclass(frozen=True)
class PlantParams:
    """Physical and disturbance parameters for one deterministic scenario."""

    mass: float
    inertia: float
    stiffness: float
    damping: float
    mode_mass: float
    thrust_deformation_coupling: float
    deformation_pitch_coupling: float
    thrust_scale: float
    torque_scale: float
    drag_x: float
    drag_z: float
    angular_damping: float
    wind_bias_x: float
    wind_bias_z: float
    gust_amplitude: float
    gust_frequency: float
    gust_phase: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


NOMINAL_PARAMS = PlantParams(
    mass=1.65,
    inertia=0.080,
    stiffness=11.0,
    damping=1.55,
    mode_mass=0.34,
    thrust_deformation_coupling=0.15,
    deformation_pitch_coupling=0.10,
    thrust_scale=1.0,
    torque_scale=1.0,
    drag_x=0.14,
    drag_z=0.18,
    angular_damping=0.075,
    wind_bias_x=0.0,
    wind_bias_z=0.0,
    gust_amplitude=0.0,
    gust_frequency=0.8,
    gust_phase=0.0,
)


def sample_plant(seed: int) -> PlantParams:
    """Sample one scenario from the disclosed held-out evaluation envelope."""

    rng = random.Random(seed)
    return PlantParams(
        mass=rng.uniform(1.28, 2.08),
        inertia=rng.uniform(0.058, 0.112),
        stiffness=rng.uniform(7.0, 16.0),
        damping=rng.uniform(0.85, 2.35),
        mode_mass=rng.uniform(0.27, 0.43),
        thrust_deformation_coupling=rng.uniform(0.08, 0.27),
        deformation_pitch_coupling=rng.uniform(0.05, 0.18),
        thrust_scale=rng.uniform(0.86, 1.14),
        torque_scale=rng.uniform(0.84, 1.16),
        drag_x=rng.uniform(0.08, 0.24),
        drag_z=rng.uniform(0.10, 0.29),
        angular_damping=rng.uniform(0.035, 0.125),
        wind_bias_x=rng.uniform(-1.25, 1.25),
        wind_bias_z=rng.uniform(-0.55, 0.55),
        gust_amplitude=rng.uniform(0.25, 0.95),
        gust_frequency=rng.uniform(0.45, 1.35),
        gust_phase=rng.uniform(-math.pi, math.pi),
    )


def sample_initial_state(seed: int) -> State:
    """Generate a small, reproducible launch-state perturbation."""

    rng = random.Random(seed ^ 0x5A17)
    return State(
        x=rng.uniform(-0.10, 0.10),
        z=1.5 + rng.uniform(-0.08, 0.08),
        vx=rng.uniform(-0.08, 0.08),
        vz=rng.uniform(-0.08, 0.08),
        theta=rng.uniform(-0.035, 0.035),
        omega=rng.uniform(-0.04, 0.04),
        q=rng.uniform(-0.025, 0.025),
        qdot=rng.uniform(-0.04, 0.04),
    )


@dataclass(frozen=True)
class Accelerations:
    ax: float
    az: float
    alpha: float
    qddot: float
    wind_x: float
    wind_z: float


def accelerations(
    state: State, control: Control, params: PlantParams, time_s: float
) -> Accelerations:
    """Evaluate the continuous accelerations at a state and input."""

    # Two incommensurate harmonics make a reproducible but nontrivial gust.
    phase = params.gust_frequency * time_s + params.gust_phase
    wind_x = params.wind_bias_x + params.gust_amplitude * (
        0.72 * math.sin(phase) + 0.28 * math.sin(2.17 * phase + 0.4)
    )
    wind_z = params.wind_bias_z + 0.55 * params.gust_amplitude * (
        math.cos(0.83 * phase - 0.2) + 0.18 * math.sin(1.71 * phase)
    )

    thrust = max(0.0, control.thrust) * params.thrust_scale
    effective_angle = state.theta + params.thrust_deformation_coupling * state.q
    fx = thrust * math.sin(effective_angle)
    fz = thrust * math.cos(effective_angle)

    drag_force_x = params.drag_x * state.vx * abs(state.vx)
    drag_force_z = params.drag_z * state.vz * abs(state.vz)
    ax = (fx - drag_force_x + wind_x) / params.mass
    az = (fz - drag_force_z + wind_z) / params.mass - GRAVITY

    deformation_torque = params.deformation_pitch_coupling * state.q
    alpha = (
        params.torque_scale * control.torque
        - params.angular_damping * state.omega
        - deformation_torque
    ) / params.inertia

    # The compliant mode is excited by excess lift, turning, and lateral gusts.
    hover_force = params.mass * GRAVITY
    shape_forcing = (
        0.20 * (thrust - hover_force)
        + 0.11 * thrust * abs(math.sin(state.theta))
        + 0.075 * state.omega
        + 0.055 * wind_x
    )
    qddot = (
        shape_forcing - params.stiffness * state.q - params.damping * state.qdot
    ) / params.mode_mass
    return Accelerations(ax, az, alpha, qddot, wind_x, wind_z)


def step(
    state: State,
    control: Control,
    params: PlantParams,
    time_s: float,
    dt: float,
) -> State:
    """Advance one step using deterministic semi-implicit Euler integration."""

    acc = accelerations(state, control, params, time_s)
    vx = state.vx + dt * acc.ax
    vz = state.vz + dt * acc.az
    omega = state.omega + dt * acc.alpha
    qdot = state.qdot + dt * acc.qddot
    return State(
        x=state.x + dt * vx,
        z=state.z + dt * vz,
        vx=vx,
        vz=vz,
        theta=wrap_angle(state.theta + dt * omega),
        omega=omega,
        q=state.q + dt * qdot,
        qdot=qdot,
    )


def nominal_translational_acceleration(state: State, control: Control) -> tuple[float, float]:
    """Acceleration predicted by the controller's fixed nominal rigid model."""

    thrust = max(0.0, control.thrust)
    fx = thrust * math.sin(state.theta)
    fz = thrust * math.cos(state.theta)
    ax = (
        fx - NOMINAL_PARAMS.drag_x * state.vx * abs(state.vx)
    ) / NOMINAL_PARAMS.mass
    az = (
        fz - NOMINAL_PARAMS.drag_z * state.vz * abs(state.vz)
    ) / NOMINAL_PARAMS.mass - GRAVITY
    return ax, az
