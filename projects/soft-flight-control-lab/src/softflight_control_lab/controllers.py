"""Nominal feedback and online learned-residual controllers."""

from __future__ import annotations

import math
from typing import List, Sequence

from .dynamics import (
    GRAVITY,
    NOMINAL_PARAMS,
    Control,
    State,
    clamp,
    nominal_translational_acceleration,
    wrap_angle,
)
from .trajectory import Reference, agile_reference


class NominalController:
    """Nonlinear position-to-attitude tracking around a fixed nominal model."""

    name = "nominal"

    def __init__(self) -> None:
        self.kp_x = 2.15
        self.kd_x = 2.25
        self.kp_z = 2.75
        self.kd_z = 2.55
        self.kp_theta = 15.0
        self.kd_theta = 4.8
        self.max_thrust = 2.35 * NOMINAL_PARAMS.mass * GRAVITY
        self.max_torque = 1.25
        self.last_residual_prediction = (0.0, 0.0)

    def reset(self) -> None:
        self.last_residual_prediction = (0.0, 0.0)

    def desired_acceleration(
        self, state: State, reference: Reference
    ) -> tuple[float, float]:
        ax = (
            reference.ax
            + self.kp_x * (reference.x - state.x)
            + self.kd_x * (reference.vx - state.vx)
        )
        az = (
            reference.az
            + self.kp_z * (reference.z - state.z)
            + self.kd_z * (reference.vz - state.vz)
        )
        return clamp(ax, -5.5, 5.5), clamp(az, -5.0, 5.0)

    def _map_acceleration_to_control(
        self, state: State, desired_ax: float, desired_az: float
    ) -> Control:
        # Nominal quadratic-drag feedforward expressed as an inertial force.
        fx = (
            NOMINAL_PARAMS.mass * desired_ax
            + NOMINAL_PARAMS.drag_x * state.vx * abs(state.vx)
        )
        fz = (
            NOMINAL_PARAMS.mass * (desired_az + GRAVITY)
            + NOMINAL_PARAMS.drag_z * state.vz * abs(state.vz)
        )
        desired_theta = math.atan2(fx, max(0.25, fz))
        thrust = clamp(math.hypot(fx, fz), 0.0, self.max_thrust)
        angle_error = wrap_angle(desired_theta - state.theta)
        torque = NOMINAL_PARAMS.inertia * (
            self.kp_theta * angle_error - self.kd_theta * state.omega
        )
        return Control(thrust, clamp(torque, -self.max_torque, self.max_torque))

    def command(self, time_s: float, state: State) -> Control:
        reference = agile_reference(time_s)
        desired_ax, desired_az = self.desired_acceleration(state, reference)
        return self._map_acceleration_to_control(state, desired_ax, desired_az)

    def observe(
        self, state: State, action: Control, next_state: State, dt: float
    ) -> None:
        """Hook for adaptive controllers; the nominal controller does nothing."""


class RecursiveLeastSquares:
    """Small bounded RLS estimator with an auditable pure-Python update."""

    def __init__(
        self,
        feature_count: int,
        covariance: float = 18.0,
        forgetting_factor: float = 0.998,
    ) -> None:
        self.feature_count = feature_count
        self.initial_covariance = covariance
        self.forgetting_factor = forgetting_factor
        self.weights: List[float] = []
        self.covariance: List[List[float]] = []
        self.samples = 0
        self.reset()

    def reset(self) -> None:
        self.weights = [0.0] * self.feature_count
        self.covariance = [
            [
                self.initial_covariance if row == column else 0.0
                for column in range(self.feature_count)
            ]
            for row in range(self.feature_count)
        ]
        self.samples = 0

    def predict(self, features: Sequence[float]) -> float:
        return sum(weight * feature for weight, feature in zip(self.weights, features))

    def update(self, features: Sequence[float], target: float) -> None:
        p_phi = [
            sum(self.covariance[row][column] * features[column] for column in range(self.feature_count))
            for row in range(self.feature_count)
        ]
        denominator = self.forgetting_factor + sum(
            features[index] * p_phi[index] for index in range(self.feature_count)
        )
        gain = [value / max(1e-9, denominator) for value in p_phi]
        error = target - self.predict(features)
        for index in range(self.feature_count):
            self.weights[index] = clamp(
                self.weights[index] + gain[index] * error, -8.0, 8.0
            )

        phi_t_p = [
            sum(features[row] * self.covariance[row][column] for row in range(self.feature_count))
            for column in range(self.feature_count)
        ]
        updated = [
            [
                (self.covariance[row][column] - gain[row] * phi_t_p[column])
                / self.forgetting_factor
                for column in range(self.feature_count)
            ]
            for row in range(self.feature_count)
        ]
        # Numerical symmetry keeps long deterministic runs well conditioned.
        for row in range(self.feature_count):
            for column in range(self.feature_count):
                value = 0.5 * (updated[row][column] + updated[column][row])
                self.covariance[row][column] = value
            self.covariance[row][row] = max(self.covariance[row][row], 1e-8)
        self.samples += 1


class OnlineResidualController(NominalController):
    """Nominal control plus online learned translational residual compensation.

    The two RLS models estimate x/z acceleration mismatch from observed state
    transitions. Predictions are clipped and gradually enabled. This preserves
    the nominal feedback structure and makes the learning contribution explicit.
    """

    name = "online_residual"

    def __init__(self) -> None:
        super().__init__()
        self.model_x = RecursiveLeastSquares(feature_count=8)
        self.model_z = RecursiveLeastSquares(feature_count=8)

    def reset(self) -> None:
        super().reset()
        if hasattr(self, "model_x"):
            self.model_x.reset()
            self.model_z.reset()

    @staticmethod
    def _features(state: State, action: Control) -> list[float]:
        thrust_acc = action.thrust / NOMINAL_PARAMS.mass
        return [
            1.0,
            thrust_acc * math.sin(state.theta) / 5.0,
            (thrust_acc * math.cos(state.theta) - GRAVITY) / 5.0,
            state.vx / 3.5,
            state.vz / 2.5,
            state.q / 0.30,
            state.qdot / 1.8,
            state.omega / 2.5,
        ]

    def command(self, time_s: float, state: State) -> Control:
        reference = agile_reference(time_s)
        desired_ax, desired_az = self.desired_acceleration(state, reference)

        preliminary = self._map_acceleration_to_control(state, desired_ax, desired_az)
        features = self._features(state, preliminary)
        # A short confidence ramp avoids applying underdetermined early estimates.
        confidence = min(1.0, self.model_x.samples / 45.0)
        predicted_x = confidence * clamp(self.model_x.predict(features), -2.6, 2.6)
        predicted_z = confidence * clamp(self.model_z.predict(features), -2.6, 2.6)
        self.last_residual_prediction = (predicted_x, predicted_z)
        return self._map_acceleration_to_control(
            state,
            clamp(desired_ax - predicted_x, -5.5, 5.5),
            clamp(desired_az - predicted_z, -5.0, 5.0),
        )

    def observe(
        self, state: State, action: Control, next_state: State, dt: float
    ) -> None:
        measured_ax = (next_state.vx - state.vx) / dt
        measured_az = (next_state.vz - state.vz) / dt
        nominal_ax, nominal_az = nominal_translational_acceleration(state, action)
        features = self._features(state, action)
        self.model_x.update(features, clamp(measured_ax - nominal_ax, -6.0, 6.0))
        self.model_z.update(features, clamp(measured_az - nominal_az, -6.0, 6.0))
