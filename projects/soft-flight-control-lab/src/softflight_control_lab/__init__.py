"""SoftFlight Control Lab: a dependency-free soft aerial control benchmark."""

from .benchmark import BenchmarkConfig, run_benchmark
from .controllers import NominalController, OnlineResidualController
from .dynamics import PlantParams, State, sample_plant

__all__ = [
    "BenchmarkConfig",
    "NominalController",
    "OnlineResidualController",
    "PlantParams",
    "State",
    "run_benchmark",
    "sample_plant",
]

__version__ = "0.1.0"
