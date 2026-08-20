"""Paired deterministic evaluation on randomized, held-out soft-aircraft plants."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import math
from pathlib import Path
import statistics
from typing import Any, Iterable

from .controllers import NominalController, OnlineResidualController
from .dynamics import Control, PlantParams, State, sample_initial_state, sample_plant, step
from .reporting import write_benchmark_artifacts
from .trajectory import Reference, agile_reference


@dataclass(frozen=True)
class BenchmarkConfig:
    episodes: int = 12
    seed: int = 2401
    duration_s: float = 12.0
    dt: float = 0.02

    def validate(self) -> None:
        if self.episodes < 1:
            raise ValueError("episodes must be at least 1")
        if self.duration_s <= 0.0:
            raise ValueError("duration_s must be positive")
        if not 0.002 <= self.dt <= 0.05:
            raise ValueError("dt must be between 0.002 and 0.05 seconds")


@dataclass
class EpisodeMetrics:
    seed: int
    controller: str
    position_rmse_m: float
    tail_position_rmse_m: float
    horizontal_rmse_m: float
    vertical_rmse_m: float
    max_position_error_m: float
    mean_control_effort: float
    deformation_rms: float
    max_abs_pitch_deg: float
    success: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EpisodeTrace:
    seed: int
    controller: str
    params: PlantParams
    times: list[float]
    states: list[State]
    references: list[Reference]
    controls: list[Control]
    residual_predictions: list[tuple[float, float]]
    metrics: EpisodeMetrics


def _root_mean_square(values: Iterable[float]) -> float:
    values_list = list(values)
    return math.sqrt(sum(value * value for value in values_list) / len(values_list))


def simulate_episode(
    controller: NominalController,
    params: PlantParams,
    initial_state: State,
    seed: int,
    config: BenchmarkConfig,
) -> EpisodeTrace:
    """Run one closed-loop scenario and retain an auditable trace."""

    controller.reset()
    state = initial_state
    times: list[float] = []
    states: list[State] = []
    references: list[Reference] = []
    controls: list[Control] = []
    predictions: list[tuple[float, float]] = []
    step_count = int(round(config.duration_s / config.dt))

    for index in range(step_count):
        time_s = index * config.dt
        reference = agile_reference(time_s)
        action = controller.command(time_s, state)
        next_state = step(state, action, params, time_s, config.dt)
        controller.observe(state, action, next_state, config.dt)

        times.append(time_s)
        states.append(state)
        references.append(reference)
        controls.append(action)
        predictions.append(controller.last_residual_prediction)
        state = next_state

        state_values = asdict(state).values()
        if not all(math.isfinite(value) for value in state_values):
            raise FloatingPointError(f"non-finite state in seed {seed} at t={time_s:.3f}")
        if abs(state.x) > 40.0 or abs(state.z) > 40.0:
            raise RuntimeError(f"divergent state in seed {seed} at t={time_s:.3f}")

    error_x = [reference.x - sample.x for reference, sample in zip(references, states)]
    error_z = [reference.z - sample.z for reference, sample in zip(references, states)]
    position_error = [math.hypot(ex, ez) for ex, ez in zip(error_x, error_z)]
    tail_start = len(position_error) // 3
    effort = [
        (action.thrust / (params.mass * 9.81)) ** 2
        + 0.08 * (action.torque / 1.25) ** 2
        for action in controls
    ]
    metrics = EpisodeMetrics(
        seed=seed,
        controller=controller.name,
        position_rmse_m=_root_mean_square(position_error),
        tail_position_rmse_m=_root_mean_square(position_error[tail_start:]),
        horizontal_rmse_m=_root_mean_square(error_x),
        vertical_rmse_m=_root_mean_square(error_z),
        max_position_error_m=max(position_error),
        mean_control_effort=sum(effort) / len(effort),
        deformation_rms=_root_mean_square(sample.q for sample in states),
        max_abs_pitch_deg=max(abs(math.degrees(sample.theta)) for sample in states),
        success=max(position_error) < 3.0 and min(sample.z for sample in states) > -0.5,
    )
    return EpisodeTrace(
        seed,
        controller.name,
        params,
        times,
        states,
        references,
        controls,
        predictions,
        metrics,
    )


def _aggregate(metrics: list[EpisodeMetrics]) -> dict[str, Any]:
    numeric_fields = (
        "position_rmse_m",
        "tail_position_rmse_m",
        "horizontal_rmse_m",
        "vertical_rmse_m",
        "max_position_error_m",
        "mean_control_effort",
        "deformation_rms",
        "max_abs_pitch_deg",
    )
    aggregate: dict[str, Any] = {
        "episodes": len(metrics),
        "successful_episodes": sum(int(item.success) for item in metrics),
    }
    for field_name in numeric_fields:
        values = [float(getattr(item, field_name)) for item in metrics]
        aggregate[field_name] = {
            "mean": sum(values) / len(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "median": statistics.median(values),
        }
    return aggregate


def _paired_summary(
    nominal: list[EpisodeMetrics], adaptive: list[EpisodeMetrics]
) -> dict[str, Any]:
    nominal_by_seed = {item.seed: item for item in nominal}
    adaptive_by_seed = {item.seed: item for item in adaptive}
    seeds = sorted(nominal_by_seed)

    def comparison(field_name: str) -> dict[str, Any]:
        baseline = [float(getattr(nominal_by_seed[seed], field_name)) for seed in seeds]
        learned = [float(getattr(adaptive_by_seed[seed], field_name)) for seed in seeds]
        changes = [base - new for base, new in zip(baseline, learned)]
        percentages = [100.0 * change / max(1e-12, base) for change, base in zip(changes, baseline)]
        return {
            "mean_absolute_reduction": sum(changes) / len(changes),
            "mean_relative_reduction_percent": sum(percentages) / len(percentages),
            "improved_episodes": sum(change > 0.0 for change in changes),
            "total_episodes": len(changes),
        }

    return {
        "position_rmse_m": comparison("position_rmse_m"),
        "tail_position_rmse_m": comparison("tail_position_rmse_m"),
        "max_position_error_m": comparison("max_position_error_m"),
    }


def run_benchmark(
    config: BenchmarkConfig | None = None,
    output_dir: Path | None = None,
) -> tuple[dict[str, Any], list[EpisodeTrace]]:
    """Evaluate both controllers on identical plants and optionally write evidence."""

    config = config or BenchmarkConfig()
    config.validate()
    traces: list[EpisodeTrace] = []
    controllers = (NominalController, OnlineResidualController)

    for episode_index in range(config.episodes):
        scenario_seed = config.seed + 7919 * episode_index
        params = sample_plant(scenario_seed)
        initial_state = sample_initial_state(scenario_seed)
        for controller_type in controllers:
            traces.append(
                simulate_episode(
                    controller_type(), params, initial_state, scenario_seed, config
                )
            )

    nominal_metrics = [trace.metrics for trace in traces if trace.controller == "nominal"]
    adaptive_metrics = [
        trace.metrics for trace in traces if trace.controller == "online_residual"
    ]
    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "benchmark": "paired held-out randomized simulation",
        "evidence_boundary": "simulation only; not hardware or flight validation",
        "config": asdict(config),
        "scenario_seed_rule": "seed + 7919 * episode_index",
        "controllers": {
            "nominal": _aggregate(nominal_metrics),
            "online_residual": _aggregate(adaptive_metrics),
        },
        "paired_comparison": _paired_summary(nominal_metrics, adaptive_metrics),
    }
    if output_dir is not None:
        write_benchmark_artifacts(output_dir, config, summary, traces)
    return summary, traces


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the deterministic SoftFlight paired control benchmark."
    )
    parser.add_argument("--episodes", type=int, default=12)
    parser.add_argument("--seed", type=int, default=2401)
    parser.add_argument("--duration", type=float, default=12.0, dest="duration_s")
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument(
        "--output-dir", type=Path, default=Path("artifacts"), help="artifact directory"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    config = BenchmarkConfig(args.episodes, args.seed, args.duration_s, args.dt)
    summary, _ = run_benchmark(config, args.output_dir)
    nominal = summary["controllers"]["nominal"]["position_rmse_m"]["mean"]
    adaptive = summary["controllers"]["online_residual"]["position_rmse_m"]["mean"]
    paired = summary["paired_comparison"]["position_rmse_m"]
    print("SoftFlight paired held-out simulation benchmark")
    print(f"  episodes: {config.episodes}  seed: {config.seed}")
    print(f"  nominal position RMSE:       {nominal:.4f} m")
    print(f"  online-residual RMSE:        {adaptive:.4f} m")
    print(
        "  paired mean reduction:       "
        f"{paired['mean_relative_reduction_percent']:.2f}% "
        f"({paired['improved_episodes']}/{paired['total_episodes']} episodes)"
    )
    print(f"  artifacts: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
