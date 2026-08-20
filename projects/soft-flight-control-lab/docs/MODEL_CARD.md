# Model and Evaluation Card

## Intended use

SoftFlight Control Lab is an educational and portfolio-scale benchmark for
reasoning about online residual learning under structured dynamics mismatch. It
supports reproducible controller comparisons, ablations, and research
discussion. It is not intended to command a real vehicle or certify safety.

## Plant abstraction

The simulated state is

\[
s=[x,z,v_x,v_z,\theta,\omega,q,\dot q],
\]

with inertial position and velocity, pitch and pitch rate, and one lumped
deformation mode. Effective thrust angle is

\[
\theta_\mathrm{eff}=\theta+c_Tq.
\]

Translational accelerations include thrust, gravity, quadratic drag, constant
wind bias, and a two-harmonic gust. Pitch dynamics include actuator scaling,
angular damping, and deformation feedback. The compliant mode is a forced
mass–spring–damper excited by excess thrust, turning, and wind.

The implementation is the authoritative specification:
[`src/softflight_control_lab/dynamics.py`](../src/softflight_control_lab/dynamics.py).

## Controller cards

### Nominal feedback

The nominal controller tracks an analytic reference with acceleration
feedforward and position/velocity feedback. It compensates nominal quadratic
drag, maps desired inertial force to thrust and pitch, and uses a saturated
attitude PD loop. It knows only the fixed nominal parameter set.

### Online residual compensation

The adaptive controller preserves the nominal feedback architecture. Two
recursive least-squares estimators learn horizontal and vertical acceleration
residuals from observed one-step state transitions. Eight disclosed features
cover bias, nominal thrust acceleration, velocity, compliant displacement and
rate, and angular rate. The prediction is clipped to ±2.6 m/s², confidence is
ramped across the first 45 samples, and the estimator resets before every
episode. There is no offline training, cross-episode memory, or access to true
plant parameters.

This is “learning-based” in the narrow and explicit sense of online supervised
system-residual identification. It is not reinforcement learning and does not
claim a neural policy.

## Evaluation protocol

- Default: 12 paired episodes, 12 seconds each, 20 ms integration step.
- Base seed: `2401`; scenario seed: `2401 + 7919 × episode_index`.
- Each seed defines plant parameters and the initial-state perturbation.
- Both controllers receive the identical plant and initial state.
- The controller is reset between episodes.
- Development smoke-test seeds used while constructing the example were
  `11`, `29`, and `47`; the default evaluation seeds are disjoint.
- Primary metric: two-dimensional position RMSE.
- Secondary metrics: tail RMSE (final two-thirds), axis RMSE, worst position
  error, normalized control effort, deformation RMS, and maximum pitch.
- “Success” is a coarse simulation guardrail: maximum position error below
  3 m and altitude above −0.5 m. It is not a flight-safety criterion.

### Randomization envelope

| Quantity | Range |
|---|---:|
| Mass | 1.28–2.08 kg |
| Pitch inertia | 0.058–0.112 kg·m² |
| Modal stiffness | 7.0–16.0 (reduced units) |
| Modal damping | 0.85–2.35 (reduced units) |
| Modal mass | 0.27–0.43 (reduced units) |
| Thrust/deformation coupling | 0.08–0.27 |
| Deformation/pitch coupling | 0.05–0.18 |
| Thrust effectiveness | 0.86–1.14 |
| Torque effectiveness | 0.84–1.16 |
| Horizontal wind bias | −1.25–1.25 N |
| Vertical wind bias | −0.55–0.55 N |
| Gust amplitude | 0.25–0.95 N |

Every additional randomized field is visible in `sample_plant`; every sampled
value is exported with the episode metrics.

## Reproducibility and artifacts

The simulation, learner, randomization, metrics, CSV writer, JSON writer, and SVG
renderer use only the Python standard library. Fixed seeds produce byte-stable
JSON/CSV on the same supported Python implementation. The SVG visualizes a
median-improvement episode, not a hand-selected best case.

## Limitations and evidence boundary

- **Simulation only:** no physical platform, flight test, motion capture, or
  field experiment has been used.
- **Reduced order:** a single compliant coordinate is not a finite-element or
  continuum model of a soft airframe.
- **Simplified aerodynamics:** no rotor inflow, wake interaction, ground effect,
  blade dynamics, stall, or battery model.
- **Privileged state:** the controller receives full state without estimator
  noise, delay, dropouts, calibration drift, or observability constraints.
- **Ideal compute and actuator timing:** saturation exists, but latency,
  bandwidth, rate limits, faults, and asynchronous execution do not.
- **Synthetic shift:** parameter randomization is broad but cannot establish
  transfer to an unknown real platform.
- **Small evaluation:** paired episodes are useful for code-level evidence, not
  statistical proof of generality.
- **No safety guarantee:** bounded residual predictions are a basic guardrail,
  not a control barrier function or verified assurance mechanism.
- **Not published research:** this repository is a standalone demonstrator and
  should not be represented as peer-reviewed work.

## Responsible next steps toward hardware

1. Identify a platform-specific model and actuator limits from bench data.
2. Add state estimation, latency, noise, rate limits, and fault injection.
3. Separate epistemic uncertainty from transient disturbances and evaluate
   persistent excitation requirements.
4. Place adaptation behind a safety filter and define a fallback controller.
5. Progress through software-in-the-loop, hardware-in-the-loop, tethered tests,
   protected indoor flight, and only then task-level experiments.
6. Pre-register metrics and compare against robust/adaptive non-learning
   baselines, not only the nominal controller used here.
