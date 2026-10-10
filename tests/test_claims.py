"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import tft_algorithm as A
import tft_constants as C
import tft_evaluation as ev
from tft_scenario import ALTERNATE, DEVIATIONS, ONE_SHOT, STRATEGIES, Game, make_game

CLASSIC = Game(5.0, 3.0, 1.0, 0.0)


def test_threshold_of_tft_is_two_thirds_and_of_grim_one_half():
    rows = {r["key"]: r for r in ev.threshold_table(CLASSIC)}
    assert rows["TFT"]["formula"] == pytest.approx(2.0 / 3.0)
    assert rows["GRIM"]["formula"] == pytest.approx(0.5)
    assert rows["TFT"]["threshold"] == pytest.approx(0.67, abs=1e-9)   # erster Rasterwert (Schritt 0,005) oberhalb von 2/3
    assert rows["GRIM"]["threshold"] == pytest.approx(0.5, abs=1e-9)


def test_always_defect_is_an_equilibrium_at_every_delta_and_allc_never():
    rows = {r["key"]: r for r in ev.threshold_table(CLASSIC)}
    assert rows["ALLD"]["threshold"] <= C.THRESHOLD_STEP + 1e-9
    assert rows["ALLC"]["threshold"] is None


def test_tf2t_and_pavlov_are_never_a_symmetric_equilibrium_at_the_classic_payoffs():
    rows = {r["key"]: r for r in ev.threshold_table(CLASSIC)}
    assert rows["TF2T"]["threshold"] is None
    assert rows["PAVLOV"]["threshold"] is None


def test_tf2t_is_exploited_by_alternating_at_every_delta():
    tf2t = STRATEGIES["TF2T"]
    for d in C.DELTA_GRID:
        assert A.discounted_value(ALTERNATE, tf2t, CLASSIC, d) > A.discounted_value(tf2t, tf2t, CLASSIC, d)


def test_pavlov_threshold_is_three_quarters_when_t_is_4_5():
    game = make_game(4.5, 1.0, 0.0)
    pav = STRATEGIES["PAVLOV"]
    assert A.equilibrium_threshold(pav, pav, game) == pytest.approx(0.75, abs=0.006)
    assert (game.t - game.r) / (game.r - game.p) == pytest.approx(0.75)


def test_standard_preset_numbers():
    an = ev.analyse(ev.Settings())
    assert an.value_a == pytest.approx(15.0) and an.value_b == pytest.approx(15.0)
    assert an.average_a == pytest.approx(3.0)
    assert an.expected_rounds == pytest.approx(5.0)
    assert an.is_equilibrium and an.threshold == pytest.approx(0.67, abs=1e-9)


def test_deviation_values_at_delta_0_8():
    rows = {r["name"]: r["value"] for r in ev.deviation_table(CLASSIC, 0.8, "TFT", "TFT")}
    assert rows["Beibehalten (Tit-for-Tat)"] == pytest.approx(15.0)
    assert rows["Immer defektieren"] == pytest.approx(9.0)
    assert rows["Abwechselnd D, C"] == pytest.approx(13.89, abs=0.005)
    assert rows["Einmal D, dann C"] == pytest.approx(14.60, abs=0.005)
    assert rows["Beste Antwort (alle Strategien)"] == pytest.approx(15.0)


def test_short_shadow_preset_gain_is_095():
    an = ev.analyse(ev.Settings(delta=0.40))
    assert not an.is_equilibrium
    assert an.expected_rounds == pytest.approx(1.0 / 0.6)
    assert an.gain_a == pytest.approx(0.95, abs=0.005)
    assert an.value_a == pytest.approx(5.0)


def test_just_below_the_tft_threshold_gain_is_004():
    an = ev.analyse(ev.Settings(delta=0.66))
    assert not an.is_equilibrium
    assert an.gain_a == pytest.approx(0.04, abs=0.005)


def test_grim_holds_where_tft_does_not_at_delta_0_6():
    grim = ev.analyse(ev.Settings(delta=0.60, a="GRIM", b="GRIM"))
    tft = ev.analyse(ev.Settings(delta=0.60))
    assert grim.is_equilibrium and not tft.is_equilibrium
    assert grim.value_a == pytest.approx(7.5)


def test_exploitation_preset_numbers():
    an = ev.analyse(ev.Settings(a="TFT", b="ALLD"))
    assert an.value_a == pytest.approx(4.0)       # S + δ P / (1 − δ) = 0 + 0,8 · 5
    assert an.value_b == pytest.approx(9.0)       # T + δ P / (1 − δ) = 5 + 4
    assert an.average_a == pytest.approx(0.8) and an.average_b == pytest.approx(1.8)
    assert an.gain_a == pytest.approx(1.0) and an.gain_b == pytest.approx(6.0)
    assert an.threshold is None


def test_four_equilibrium_pairs_at_delta_0_8():
    pairs = {frozenset(p) for p in ev.equilibrium_pairs(CLASSIC, 0.8)}
    assert pairs == {frozenset({"ALLD"}), frozenset({"TFT"}), frozenset({"GRIM"}), frozenset({"TFT", "GRIM"})}


def test_payoff_matrix_entries_by_hand():
    m = ev.payoff_matrix(CLASSIC, 0.8)
    idx = {k: i for i, k in enumerate(C.STRATEGY_KEYS)}
    assert m[idx["TFT"]][idx["TFT"]] == pytest.approx(3.0)
    assert m[idx["ALLD"]][idx["ALLC"]] == pytest.approx(5.0)
    assert m[idx["ALLC"]][idx["ALLD"]] == pytest.approx(0.0)
    assert m[idx["ALLD"]][idx["ALLD"]] == pytest.approx(1.0)
    assert m[idx["TFT"]][idx["ALLD"]] == pytest.approx(0.2 * 0.0 + 0.8 * 1.0)   # (1 − δ) · S + δ · P


def test_equilibrium_map_matches_the_threshold_table():
    flags = ev.equilibrium_map(CLASSIC)
    tft = flags[C.STRATEGY_KEYS.index("TFT")]
    for d, f in zip(C.DELTA_GRID, tft):
        assert f == (d >= 0.67 - 1e-9), d
    assert all(flags[C.STRATEGY_KEYS.index("ALLD")])
    assert not any(flags[C.STRATEGY_KEYS.index("ALLC")])


def test_verdict_names_the_threshold_and_levels():
    ok = ev.verdict(ev.analyse(ev.Settings()), ev.Settings())
    assert ok[0] == "success" and "0,67" in ok[1]
    bad_settings = ev.Settings(delta=0.40)
    bad = ev.verdict(ev.analyse(bad_settings), bad_settings)
    assert bad[0] == "warning" and "0,95" in bad[1] and "0,67" in bad[1]
    never_settings = ev.Settings(a="ALLC", b="ALLC")
    never = ev.verdict(ev.analyse(never_settings), never_settings)
    assert never[0] == "warning" and "keinem" in never[1]


def test_deviations_catalog_is_alld_alternate_one_shot():
    assert [d.key for d in DEVIATIONS] == ["ALLD", "ALT", "ONE"]
    assert ALTERNATE.key == "ALT" and ONE_SHOT.key == "ONE"


def test_strategy_overview_traces_by_hand():
    rows = {r["key"]: r for r in ev.strategy_overview()}
    assert rows["TFT"]["vs_alld"] == "C D D D D D D D"
    assert rows["TFT"]["vs_alt"] == "C D C D C D C D"
    assert rows["GRIM"]["vs_alt"] == "C D D D D D D D"
    assert rows["TF2T"]["vs_alld"] == "C C D D D D D D"
    assert rows["PAVLOV"]["vs_alld"] == "C D C D C D C D"
    assert rows["ALLC"]["vs_alld"] == "C C C C C C C C" and rows["ALLD"]["vs_alt"] == "D D D D D D D D"
    assert all(r["description"] for r in rows.values())
