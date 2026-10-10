"""Mini-Instanz-Tests je Einheit (DEMO-PLAYBOOK §1b): alles von Hand gerechnet am Spiel T/R/P/S = 5/3/1/0."""

import itertools

import numpy as np
import pytest

import tft_algorithm as A
import tft_constants as C
from tft_scenario import ALTERNATE, ONE_SHOT, Game, make_game

CC, CD, DC, DD = (0, 0), (0, 1), (1, 0), (1, 1)


# --- Spiel ---------------------------------------------------------------------------------------------------------------------------------

def test_stage_payoffs(game):
    assert game.stage(0, 0) == 3 and game.stage(0, 1) == 0 and game.stage(1, 0) == 5 and game.stage(1, 1) == 1


@pytest.mark.parametrize("t,r,p,s", [(5, 3, 3, 0), (3, 3, 1, 0), (5, 3, 1, 1), (6, 3, 1, 0), (5, 3, 2, 3)])
def test_game_rejects_non_dilemma_payoffs(t, r, p, s):
    with pytest.raises(ValueError):
        Game(t=t, r=r, p=p, s=s)


def test_every_slider_combination_is_a_dilemma():
    """Reglergrenzen so gewählt, dass keine Kombination T > R > P > S oder 2R > T + S verletzt (kein berechneter Bereich)."""
    ts = np.arange(C.T_MIN, C.T_MAX + 1e-9, C.T_STEP)
    ps = np.arange(C.P_MIN, C.P_MAX + 1e-9, C.P_STEP)
    ss = np.arange(C.S_MIN, C.S_MAX + 1e-9, C.S_STEP)
    for t, p, s in itertools.product(ts, ps, ss):
        make_game(t, p, s)


# --- Spielverlauf --------------------------------------------------------------------------------------------------------------------------

def test_tft_against_alld_cooperates_once_then_defects(strat):
    assert A.play(strat["TFT"], strat["ALLD"], 4) == [CD, DD, DD, DD]


def test_tft_against_tft_cooperates_forever(strat):
    assert A.play(strat["TFT"], strat["TFT"], 5) == [CC] * 5


def test_grim_never_forgives_a_single_defection(strat):
    # ALT defektiert in Runde 1, kooperiert in Runde 2: Grim bleibt danach bei D, TFT kehrt zur Kooperation zurück.
    assert A.play(strat["GRIM"], ALTERNATE, 4) == [CD, DC, DD, DC]
    assert A.play(strat["TFT"], ALTERNATE, 4) == [CD, DC, CD, DC]


def test_tf2t_defects_only_after_two_defections_in_a_row(strat):
    assert A.play(strat["TF2T"], strat["ALLD"], 4) == [CD, CD, DD, DD]
    assert A.play(strat["TF2T"], ALTERNATE, 6) == [CD, CC, CD, CC, CD, CC]


def test_pavlov_shifts_after_a_loss_and_stays_after_a_win(strat):
    assert A.play(strat["PAVLOV"], strat["ALLD"], 4) == [CD, DD, CD, DD]
    assert A.play(strat["PAVLOV"], strat["ALLC"], 3) == [CC, CC, CC]
    assert A.play(strat["ALLD"], strat["PAVLOV"], 4) == [DC, DD, DC, DD]


def test_stage_payoffs_of_a_history(game):
    assert A.stage_payoffs(game, [CC, CD, DC, DD]) == [(3, 3), (0, 5), (5, 0), (1, 1)]


# --- diskontierter Wert --------------------------------------------------------------------------------------------------------------------

def test_discounted_values_by_hand(game, strat):
    d = 0.5
    # beide TFT: R / (1 - d) = 3 / 0,5
    assert A.discounted_value(strat["TFT"], strat["TFT"], game, d) == pytest.approx(6.0)
    # beide ALLD: P / (1 - d) = 1 / 0,5
    assert A.discounted_value(strat["ALLD"], strat["ALLD"], game, d) == pytest.approx(2.0)
    # TFT gegen ALLD: S + d·P/(1-d) = 0 + 0,5 · 2 ; ALLD gegen TFT: T + d·P/(1-d) = 5 + 1
    assert A.discounted_value(strat["TFT"], strat["ALLD"], game, d) == pytest.approx(1.0)
    assert A.discounted_value(strat["ALLD"], strat["TFT"], game, d) == pytest.approx(6.0)
    # ALLC gegen ALLD: S/(1-d) = 0 ; ALLD gegen ALLC: T/(1-d) = 10
    assert A.discounted_value(strat["ALLC"], strat["ALLD"], game, d) == pytest.approx(0.0)
    assert A.discounted_value(strat["ALLD"], strat["ALLC"], game, d) == pytest.approx(10.0)


def test_alternating_deviation_against_tft_by_hand(game, strat):
    # D, C, D, C ... gegen TFT bringt T, S, T, S ...: (T + d·S) / (1 - d²) = 5 / 0,75
    assert A.discounted_value(ALTERNATE, strat["TFT"], game, 0.5) == pytest.approx(5.0 / 0.75)


def test_average_value_is_value_times_one_minus_delta(game, strat):
    assert A.average_value(strat["TFT"], strat["TFT"], game, 0.8) == pytest.approx(3.0)
    assert A.average_value(strat["TFT"], strat["ALLD"], game, 0.5) == pytest.approx(0.5)


def test_expected_rounds():
    assert A.expected_rounds(0.5) == pytest.approx(2.0)
    assert A.expected_rounds(0.8) == pytest.approx(5.0)


# --- Bestantwort ---------------------------------------------------------------------------------------------------------------------------

def test_best_response_values_by_hand(game, strat):
    d = 0.5
    assert A.best_response_value(strat["ALLC"], game, d) == pytest.approx(10.0)   # immer D
    assert A.best_response_value(strat["ALLD"], game, d) == pytest.approx(2.0)    # immer D
    assert A.best_response_value(strat["TFT"], game, d) == pytest.approx(5.0 / 0.75)  # abwechselnd D, C


def test_best_response_policy_against_alld_is_always_defect(game, strat):
    policy, value = A.best_response_policy(strat["ALLD"], game, 0.9)
    assert policy == (1,) and value == pytest.approx(10.0)


def test_best_response_is_never_worse_than_any_strategy(game, strat):
    for opp, own in itertools.product(strat.values(), list(strat.values()) + [ALTERNATE, ONE_SHOT]):
        for d in (0.2, 0.5, 0.9):
            assert A.best_response_value(opp, game, d) >= A.discounted_value(own, opp, game, d) - 1e-9


def test_deviation_gain_is_zero_for_a_best_response(game, strat):
    # ALLD ist die beste Antwort auf ALLC? Nein: auf ALLC ist ALLD beste Antwort -> Gewinn 0.
    assert A.deviation_gain(strat["ALLD"], strat["ALLC"], game, 0.5) == pytest.approx(0.0, abs=1e-9)
    assert A.deviation_gain(strat["ALLC"], strat["ALLC"], game, 0.5) == pytest.approx(10.0 - 6.0)


# --- Gleichgewicht und Schwelle ------------------------------------------------------------------------------------------------------------

def test_alld_is_an_equilibrium_for_every_delta(game, strat):
    for d in C.DELTA_GRID:
        assert A.is_equilibrium(strat["ALLD"], strat["ALLD"], game, d)


def test_allc_is_never_an_equilibrium_against_itself(game, strat):
    for d in C.DELTA_GRID:
        assert not A.is_equilibrium(strat["ALLC"], strat["ALLC"], game, d)


def test_tft_threshold_is_two_thirds_at_the_classic_payoffs(game, strat):
    assert A.axelrod_threshold(game, "TFT") == pytest.approx(2.0 / 3.0)
    assert A.is_equilibrium(strat["TFT"], strat["TFT"], game, 0.67)
    assert not A.is_equilibrium(strat["TFT"], strat["TFT"], game, 0.66)


def test_grim_threshold_is_one_half_and_lower_than_tft(game, strat):
    assert A.axelrod_threshold(game, "GRIM") == pytest.approx(0.5)
    assert A.is_equilibrium(strat["GRIM"], strat["GRIM"], game, 0.51)
    assert not A.is_equilibrium(strat["GRIM"], strat["GRIM"], game, 0.49)
    assert A.is_equilibrium(strat["GRIM"], strat["GRIM"], game, 0.60)
    assert not A.is_equilibrium(strat["TFT"], strat["TFT"], game, 0.60)


def test_at_exactly_the_threshold_the_deviation_is_a_tie(game, strat):
    d = 2.0 / 3.0
    assert A.deviation_gain(strat["TFT"], strat["TFT"], game, d) == pytest.approx(0.0, abs=1e-9)


def test_tf2t_is_exploitable_by_alternating_at_any_delta(game, strat):
    for d in (0.3, 0.7, 0.95):
        assert A.deviation_gain(strat["TF2T"], strat["TF2T"], game, d) > 0.1


def test_pavlov_is_a_knife_edge_at_the_classic_payoffs_and_stable_when_2r_exceeds_t_plus_p(strat):
    classic = Game(5.0, 3.0, 1.0, 0.0)           # 2R = T + P: Grenzfall
    roomy = Game(4.5, 3.0, 1.0, 0.0)             # 2R > T + P: Schwelle (T−R)/(R−P) = 0,75
    assert not A.is_equilibrium(strat["PAVLOV"], strat["PAVLOV"], classic, 0.95)
    assert A.is_equilibrium(strat["PAVLOV"], strat["PAVLOV"], roomy, 0.80)
    assert not A.is_equilibrium(strat["PAVLOV"], strat["PAVLOV"], roomy, 0.70)


def test_equilibrium_threshold_returns_none_when_it_never_holds(game, strat):
    assert A.equilibrium_threshold(strat["ALLC"], strat["ALLC"], game, step=0.05) is None


def test_equilibrium_threshold_matches_the_closed_form_on_the_grid(game, strat):
    assert A.equilibrium_threshold(strat["TFT"], strat["TFT"], game) == pytest.approx(0.67, abs=1e-9)
    assert A.equilibrium_threshold(strat["GRIM"], strat["GRIM"], game) == pytest.approx(0.5, abs=1e-9)


def test_closed_form_rejects_a_strategy_without_a_formula(game):
    with pytest.raises(ValueError):
        A.axelrod_threshold(game, "PAVLOV")
