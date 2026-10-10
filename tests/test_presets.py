"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzen/Einrasten."""

import pytest

import tft_constants as C
import tft_evaluation as ev
import tft_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        assert C.DELTA_MIN <= preset["delta"] <= C.DELTA_MAX, name
        assert C.T_MIN <= preset["t"] <= C.T_MAX and C.P_MIN <= preset["p"] <= C.P_MAX and C.S_MIN <= preset["s"] <= C.S_MAX, name
        assert preset["a"] in C.STRATEGY_KEYS and preset["b"] in C.STRATEGY_KEYS, name
        assert C.ROUNDS_MIN <= preset["rounds"] <= C.ROUNDS_MAX, name


def test_default_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(**first) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_is_a_valid_dilemma():
    for preset in C.PRESETS.values():
        ev.Settings(**preset).game()


def test_clamp_limits_numbers_and_snaps_choices():
    spec = P.SETTING_SPECS["delta_slider"]
    assert P.clamp(spec, 2.0) == C.DELTA_MAX and P.clamp(spec, -1.0) == C.DELTA_MIN
    choice = P.SETTING_SPECS["a_select"]
    assert P.clamp(choice, "TFT") == "TFT" and P.clamp(choice, "gibt-es-nicht") == C.DEFAULT_A


def test_presets_make_their_story_true():
    """Die Presets behaupten etwas über die Schwellen; hier steht, dass es stimmt (Auszahlungen 5/3/1/0)."""
    from tft_scenario import STRATEGIES
    import tft_algorithm as A
    g = ev.Settings().game()
    tft, grim = STRATEGIES["TFT"], STRATEGIES["GRIM"]
    assert A.is_equilibrium(tft, tft, g, 0.80)
    assert not A.is_equilibrium(tft, tft, g, 0.40)
    assert A.is_equilibrium(grim, grim, g, 0.60) and not A.is_equilibrium(tft, tft, g, 0.60)
    assert not A.is_equilibrium(tft, tft, g, 0.66)
    assert A.expected_rounds(0.40) == pytest.approx(1.0 / 0.6)
