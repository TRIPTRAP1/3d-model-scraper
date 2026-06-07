#!/usr/bin/env python3
"""Launch the Parameter Tuning Interface for the 3D model scraper."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parameter_tuner import ParameterTuner

if __name__ == "__main__":
    tuner = ParameterTuner()
    tuner.run()
