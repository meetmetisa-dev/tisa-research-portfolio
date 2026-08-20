from pathlib import Path
import math
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from softflight_control_lab.dynamics import (  # noqa: E402
    Control,
    NOMINAL_PARAMS,
    State,
    accelerations,
    sample_plant,
    step,
)


class DynamicsTests(unittest.TestCase):
    def test_parameter_sampling_is_deterministic_and_seeded(self) -> None:
        first = sample_plant(1234)
        repeated = sample_plant(1234)
        other = sample_plant(1235)
        self.assertEqual(first, repeated)
        self.assertNotEqual(first, other)
        self.assertGreaterEqual(first.mass, 1.28)
        self.assertLessEqual(first.mass, 2.08)

    def test_nominal_hover_is_an_equilibrium_at_zero_deformation(self) -> None:
        state = State()
        control = Control(NOMINAL_PARAMS.mass * 9.81, 0.0)
        acc = accelerations(state, control, NOMINAL_PARAMS, 0.0)
        self.assertAlmostEqual(acc.ax, 0.0, places=12)
        self.assertAlmostEqual(acc.az, 0.0, places=12)
        self.assertAlmostEqual(acc.alpha, 0.0, places=12)
        self.assertAlmostEqual(acc.qddot, 0.0, places=12)

    def test_step_remains_finite_under_randomized_dynamics(self) -> None:
        params = sample_plant(88)
        state = State(theta=0.1, q=0.03)
        control = Control(17.0, -0.1)
        for index in range(500):
            state = step(state, control, params, index * 0.01, 0.01)
        self.assertTrue(all(math.isfinite(value) for value in state.__dict__.values()))


if __name__ == "__main__":
    unittest.main()
