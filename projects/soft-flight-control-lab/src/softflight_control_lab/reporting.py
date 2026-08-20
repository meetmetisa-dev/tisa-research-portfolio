"""Dependency-free JSON, CSV, and SVG evidence generation."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .benchmark import BenchmarkConfig, EpisodeTrace


def _rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 8)
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    return value


def _representative_pair(traces: list["EpisodeTrace"]) -> tuple["EpisodeTrace", "EpisodeTrace"]:
    nominal = {trace.seed: trace for trace in traces if trace.controller == "nominal"}
    learned = {trace.seed: trace for trace in traces if trace.controller == "online_residual"}
    ranked = sorted(
        (
            nominal[seed].metrics.position_rmse_m
            - learned[seed].metrics.position_rmse_m,
            seed,
        )
        for seed in nominal
    )
    _, seed = ranked[len(ranked) // 2]
    return nominal[seed], learned[seed]


def _polyline(points: list[tuple[float, float]], color: str, width: float, dash: str = "") -> str:
    path = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<polyline points="{path}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{dash_attr}/>'
    )


def _write_svg(path: Path, nominal: "EpisodeTrace", learned: "EpisodeTrace") -> None:
    width, height = 1100, 620
    left, right, top, bottom = 82, 38, 78, 78
    chart_w, chart_h = width - left - right, height - top - bottom

    all_x = [ref.x for ref in nominal.references] + [s.x for s in nominal.states] + [s.x for s in learned.states]
    all_z = [ref.z for ref in nominal.references] + [s.z for s in nominal.states] + [s.z for s in learned.states]
    x_min, x_max = min(all_x) - 0.25, max(all_x) + 0.25
    z_min, z_max = min(all_z) - 0.20, max(all_z) + 0.20

    def project(x: float, z: float) -> tuple[float, float]:
        px = left + (x - x_min) / (x_max - x_min) * chart_w
        py = top + (z_max - z) / (z_max - z_min) * chart_h
        return px, py

    stride = max(1, len(nominal.states) // 360)
    reference_points = [project(ref.x, ref.z) for ref in nominal.references[::stride]]
    nominal_points = [project(state.x, state.z) for state in nominal.states[::stride]]
    learned_points = [project(state.x, state.z) for state in learned.states[::stride]]

    grid = []
    for index in range(6):
        x = left + index * chart_w / 5
        y = top + index * chart_h / 5
        grid.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart_h}"/>')
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + chart_w}" y2="{y:.1f}"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#08131f" rx="18"/>
<style>
  text {{ font-family: Inter, ui-sans-serif, system-ui, sans-serif; fill: #dbe8f2; }}
  .small {{ font-size: 13px; fill: #94aabd; }}
  .grid {{ stroke: #173047; stroke-width: 1; }}
</style>
<text x="{left}" y="38" font-size="22" font-weight="700">Representative held-out trajectory · seed {nominal.seed}</text>
<text x="{left}" y="61" class="small">Planar soft-aircraft simulation — reference and paired controller traces</text>
<g class="grid">{''.join(grid)}</g>
<rect x="{left}" y="{top}" width="{chart_w}" height="{chart_h}" fill="none" stroke="#31506a"/>
{_polyline(reference_points, '#dbe8f2', 2.0, '8 7')}
{_polyline(nominal_points, '#ff7d6e', 3.2)}
{_polyline(learned_points, '#2dd4bf', 3.2)}
<text x="{left + chart_w / 2:.1f}" y="{height - 24}" font-size="15" text-anchor="middle">horizontal position x (m)</text>
<text x="24" y="{top + chart_h / 2:.1f}" font-size="15" text-anchor="middle" transform="rotate(-90 24 {top + chart_h / 2:.1f})">altitude z (m)</text>
<g transform="translate({left + 18} {top + 22})">
  <rect width="327" height="91" rx="10" fill="#0d2031" fill-opacity="0.93" stroke="#28475f"/>
  <line x1="15" y1="22" x2="49" y2="22" stroke="#dbe8f2" stroke-width="2" stroke-dasharray="8 7"/><text x="60" y="27" font-size="14">reference</text>
  <line x1="15" y1="47" x2="49" y2="47" stroke="#ff7d6e" stroke-width="3"/><text x="60" y="52" font-size="14">nominal · {nominal.metrics.position_rmse_m:.3f} m RMSE</text>
  <line x1="15" y1="72" x2="49" y2="72" stroke="#2dd4bf" stroke-width="3"/><text x="60" y="77" font-size="14">online residual · {learned.metrics.position_rmse_m:.3f} m RMSE</text>
</g>
<text x="{left + chart_w - 4}" y="{height - 48}" class="small" text-anchor="end">Simulation only · reduced-order model · no hardware validation</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def write_benchmark_artifacts(
    output_dir: Path,
    config: "BenchmarkConfig",
    summary: dict[str, Any],
    traces: list["EpisodeTrace"],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "benchmark_summary.json"
    summary_path.write_text(
        json.dumps(_rounded(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    csv_path = output_dir / "episode_metrics.csv"
    metric_fields = list(traces[0].metrics.to_dict())
    parameter_fields = list(traces[0].params.to_dict())
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=metric_fields + [f"plant_{name}" for name in parameter_fields]
        )
        writer.writeheader()
        for trace in traces:
            row = _rounded(trace.metrics.to_dict())
            row.update(
                {f"plant_{name}": round(value, 8) for name, value in trace.params.to_dict().items()}
            )
            writer.writerow(row)

    nominal, learned = _representative_pair(traces)
    _write_svg(output_dir / "trajectory_comparison.svg", nominal, learned)
