"""Gemeinsame Fixtures: das klassische Spiel 5/3/1/0, an dem jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tft_scenario import STRATEGIES, Game  # noqa: E402


@pytest.fixture
def game():
    """T = 5, R = 3, P = 1, S = 0 (Axelrod). Alle Handrechnungen in den Tests beziehen sich darauf."""
    return Game(t=5.0, r=3.0, p=1.0, s=0.0)


@pytest.fixture
def strat():
    return STRATEGIES
