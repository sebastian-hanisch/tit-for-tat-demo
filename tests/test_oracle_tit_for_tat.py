"""Orakel-Tests tit-for-tat-demo: der Kern wird gegen UNABHÄNGIGE Rechenwege geprüft (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

Drei Orakel, jeweils ein anderer Weg als der des Kerns:

1. Wert eines Paares: abgeschnittene Summe über 400 simulierte Runden gegen das lineare System des Kerns.
2. Bestantwort: (a) Aufzählung aller stationären Politiken mit je einem linearen System, (b) Wertiteration mit Abbruchtoleranz,
   beide gegen die Politikiteration des Kerns.
3. Schwelle: die geschlossene Formel von Axelrod (1984) über alle Auszahlungs-Kombinationen der Regler gegen die rechnerisch
   bestimmte Schwelle des Kerns."""

import itertools

import numpy as np
import pytest

import tft_algorithm as A
import tft_constants as C
from tft_scenario import ALTERNATE, ONE_SHOT, STRATEGIES, Game, make_game

GAME = Game(5.0, 3.0, 1.0, 0.0)
ALL = list(STRATEGIES.values()) + [ALTERNATE, ONE_SHOT]


def truncated_value(a, b, game, delta, rounds=400):
    """Orakel 1: Σ δ^t u_t über die simulierte Spur (Rest < δ^400 · T / (1 − δ), bei δ ≤ 0,9 unter 1e-17)."""
    return sum(delta ** t * game.stage(x, y) for t, (x, y) in enumerate(A.play(a, b, rounds)))


def enumerated_best_response(opp, game, delta):
    """Orakel 2a: jede stationäre Politik (Zustand des Gegners -> Aktion) einzeln bewerten, das Maximum nehmen."""
    n = opp.size
    best = -np.inf
    for policy in itertools.product((0, 1), repeat=n):
        mat, rhs = np.eye(n), np.zeros(n)
        for s in range(n):
            x, y = policy[s], opp.act(s)
            rhs[s] = game.stage(x, y)
            mat[s, opp.step(s, x)] -= delta
        best = max(best, float(np.linalg.solve(mat, rhs)[0]))
    return best


def value_iteration_best_response(opp, game, delta):
    """Orakel 2b: klassische Wertiteration W ← max_x [u + δ W'] bis zur Toleranz 1e-13."""
    w = np.zeros(opp.size)
    for _ in range(20000):
        new = np.array([max(game.stage(x, opp.act(s)) + delta * w[opp.step(s, x)] for x in (0, 1)) for s in range(opp.size)])
        done = np.max(np.abs(new - w)) < 1e-13
        w = new
        if done:
            break
    return float(w[0])


@pytest.mark.parametrize("delta", [0.3, 0.6, 0.9])
def test_pair_value_matches_the_truncated_sum_for_all_pairs(delta):
    for a, b in itertools.product(ALL, ALL):
        assert A.discounted_value(a, b, GAME, delta) == pytest.approx(truncated_value(a, b, GAME, delta), abs=1e-6), (a.key, b.key)


@pytest.mark.parametrize("game", [GAME, make_game(4.0, 2.0, -1.0), make_game(3.5, 1.5, 0.5)])
def test_best_response_matches_both_oracles(game):
    for opp in ALL:
        for delta in (0.2, 0.5, 0.67, 0.9):
            core = A.best_response_value(opp, game, delta)
            assert core == pytest.approx(enumerated_best_response(opp, game, delta), abs=1e-8), (opp.key, delta)
            assert core == pytest.approx(value_iteration_best_response(opp, game, delta), abs=1e-8), (opp.key, delta)


def test_threshold_matches_the_closed_form_for_every_slider_combination():
    ts = np.arange(C.T_MIN, C.T_MAX + 1e-9, C.T_STEP)
    ps = np.arange(C.P_MIN, C.P_MAX + 1e-9, C.P_STEP)
    ss = np.arange(C.S_MIN, C.S_MAX + 1e-9, C.S_STEP)
    checked = 0
    for t, p, s in itertools.product(ts, ps, ss):
        game = make_game(t, p, s)
        for key in ("TFT", "GRIM"):
            found = A.equilibrium_threshold(STRATEGIES[key], STRATEGIES[key], game, step=0.01)
            expected = A.axelrod_threshold(game, key)
            assert found is not None, (key, t, p, s)
            assert expected - 1e-9 <= found <= expected + 0.01 + 1e-9, (key, t, p, s, found, expected)
            checked += 1
    assert checked == 2 * len(ts) * len(ps) * len(ss)


def test_tft_threshold_is_the_larger_of_the_two_deviations():
    """Beide Abweichungen einzeln nachgerechnet: Immer-D braucht δ ≥ (T−R)/(T−P), Abwechseln braucht δ ≥ (T−R)/(R−S)."""
    for t, p, s in itertools.product((4.0, 5.0), (1.0, 2.0), (-1.0, 0.0)):
        game = make_game(t, p, s)
        tft = STRATEGIES["TFT"]
        always_d = (game.t - game.r) / (game.t - game.p)
        alternate = (game.t - game.r) / (game.r - game.s)
        for delta in np.arange(0.05, 0.96, 0.05):
            base = A.discounted_value(tft, tft, game, delta)
            beats_d = A.discounted_value(STRATEGIES["ALLD"], tft, game, delta) > base + 1e-9
            beats_alt = A.discounted_value(ALTERNATE, tft, game, delta) > base + 1e-9
            assert beats_d == (delta < always_d - 1e-9), (t, p, s, delta)
            assert beats_alt == (delta < alternate - 1e-9), (t, p, s, delta)


def test_edge_cases_single_state_automata_and_extreme_delta():
    assert A.discounted_value(STRATEGIES["ALLC"], STRATEGIES["ALLC"], GAME, 0.95) == pytest.approx(3.0 / 0.05)
    assert A.best_response_value(STRATEGIES["ALLC"], GAME, C.DELTA_MIN) == pytest.approx(5.0 / 0.95)
    # δ → 0: nur die erste Runde zählt, Defektion ist immer die Bestantwort
    for opp in STRATEGIES.values():
        assert A.is_equilibrium(STRATEGIES["ALLD"], STRATEGIES["ALLD"], GAME, 1e-6)
        policy, _ = A.best_response_policy(opp, GAME, 1e-6)
        assert policy[0] == C.DEFECT
