"""Permalink (Begrenzen), Presets und Zustand der Regler (Standardmuster aus dem Demo-Portfolio)."""

from dataclasses import dataclass

import streamlit as st

import tft_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    choices: tuple | None = None


SETTING_SPECS = {
    "delta_slider": SettingSpec("delta", float, C.DEFAULT_DELTA, C.DELTA_MIN, C.DELTA_MAX),
    "t_slider": SettingSpec("t", float, C.DEFAULT_T, C.T_MIN, C.T_MAX),
    "p_slider": SettingSpec("p", float, C.DEFAULT_P, C.P_MIN, C.P_MAX),
    "s_slider": SettingSpec("s", float, C.DEFAULT_S, C.S_MIN, C.S_MAX),
    "a_select": SettingSpec("a", str, C.DEFAULT_A, choices=C.STRATEGY_KEYS),
    "b_select": SettingSpec("b", str, C.DEFAULT_B, choices=C.STRATEGY_KEYS),
    "rounds_slider": SettingSpec("rounds", int, C.DEFAULT_ROUNDS, C.ROUNDS_MIN, C.ROUNDS_MAX),
}
PRESET_KEYS = {"delta": "delta_slider", "t": "t_slider", "p": "p_slider", "s": "s_slider", "a": "a_select", "b": "b_select",
               "rounds": "rounds_slider"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp(spec: SettingSpec, value):
    """Wert auf die Reglergrenzen begrenzen bzw. auf eine erlaubte Auswahl einrasten (sonst Standard)."""
    if spec.choices is not None:
        return value if value in spec.choices else spec.default
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt bzw. eingerastet."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            raw = qp[spec.url_param]
            if isinstance(raw, list):
                raw = raw[0] if raw else ""
            try:
                value = spec.caster(raw)
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = clamp(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]
