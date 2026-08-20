from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from softflight_control_lab.benchmark import (  # noqa: E402
    BenchmarkConfig,
    simulate_episode,
)
from softflight_control_lab.controllers import (  # noqa: E402
    NominalController,
    OnlineResidualController,
)
from softflight_control_lab.dynamics import (  # noqa: E402
    State,
    sample_initial_state,
    sample_plant,
)


class ControllerTests(unittest.TestCase):
    def test_commands_respect_actuator_limits(self) -> None:
        for controller in (NominalController(), OnlineResidualController()):
            controller.reset()
            for state in (
                State(x=-20.0, z=-5.0, vx=-8.0, vz=4.0, theta=1.1, omega=-3.0),
                State(x=20.0, z=8.0, vx=8.0, vz=-4.0, theta=-1.1, omega=3.0),
            ):
                action = controller.command(2.0, state)
                self.assertGreaterEqual(action.thrust, 0.0)
                self.assertLessEqual(action.thrust, controller.max_thrust)
                self.assertLessEqual(abs(action.torque), controller.max_torque)

    def test_online_model_resets_between_episodes(self) -> None:
        controller = OnlineResidualController()
        controller.model_x.samples = 9
        controller.model_x.weights[0] = 1.0
        controller.reset()
        self.assertEqual(controller.model_x.samples, 0)
        self.assertEqual(controller.model_x.weights, [0.0] * 8)

    def test_online_residual_improves_mean_held_out_tail_rmse(self) -> None:
        config = BenchmarkConfig(episodes=3, seed=2401, duration_s=8.0, dt=0.02)
        nominal_errors = []
        adaptive_errors = []
        for episode_index in range(config.episodes):
            seed = config.seed + 7919 * episode_index
            params = sample_plant(seed)
            initial = sample_initial_state(seed)
            nominal_errors.append(
                simulate_episode(NominalController(), params, initial, seed, config)
                .metrics.tail_position_rmse_m
            )
            adaptive_errors.append(
                simulate_episode(OnlineResidualController(), params, initial, seed, config)
                .metrics.tail_position_rmse_m
            )
        self.assertLess(sum(adaptive_errors), sum(nominal_errors))


if __name__ == "__main__":
    unittest.main()
