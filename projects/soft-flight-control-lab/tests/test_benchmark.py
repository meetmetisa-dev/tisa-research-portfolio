from pathlib import Path
import json
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from softflight_control_lab.benchmark import BenchmarkConfig, run_benchmark  # noqa: E402


class BenchmarkTests(unittest.TestCase):
    def test_paired_scenarios_share_parameters_and_initial_state(self) -> None:
        config = BenchmarkConfig(episodes=2, seed=701, duration_s=1.0, dt=0.02)
        _, traces = run_benchmark(config)
        for episode_index in range(config.episodes):
            nominal = traces[2 * episode_index]
            adaptive = traces[2 * episode_index + 1]
            self.assertEqual(nominal.seed, adaptive.seed)
            self.assertEqual(nominal.params, adaptive.params)
            self.assertEqual(nominal.states[0], adaptive.states[0])

    def test_artifacts_are_created_with_scope_statement(self) -> None:
        config = BenchmarkConfig(episodes=2, seed=99, duration_s=1.0, dt=0.02)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            run_benchmark(config, output)
            expected = {
                "benchmark_summary.json",
                "episode_metrics.csv",
                "trajectory_comparison.svg",
            }
            self.assertEqual(expected, {path.name for path in output.iterdir()})
            summary = json.loads((output / "benchmark_summary.json").read_text())
            self.assertIn("simulation only", summary["evidence_boundary"])
            svg = (output / "trajectory_comparison.svg").read_text()
            self.assertIn("no hardware validation", svg)

    def test_fixed_seed_produces_identical_metrics(self) -> None:
        config = BenchmarkConfig(episodes=2, seed=313, duration_s=2.0, dt=0.02)
        first, _ = run_benchmark(config)
        second, _ = run_benchmark(config)
        self.assertEqual(first, second)

    def test_invalid_config_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_benchmark(BenchmarkConfig(episodes=0))


if __name__ == "__main__":
    unittest.main()
