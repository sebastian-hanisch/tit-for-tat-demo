"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern (die Komposition der Einheiten aus tft_algorithm)."""

from dataclasses import dataclass

import tft_algorithm as A
import tft_constants as C
from tft_scenario import ALTERNATE, DEVIATIONS, STRATEGIES, Game, make_game


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    delta: float = C.DEFAULT_DELTA
    t: float = C.DEFAULT_T
    p: float = C.DEFAULT_P
    s: float = C.DEFAULT_S
    a: str = C.DEFAULT_A
    b: str = C.DEFAULT_B
    rounds: int = C.DEFAULT_ROUNDS

    def game(self) -> Game:
        return make_game(self.t, self.p, self.s)


@dataclass(frozen=True)
class Analysis:
    game: Game
    history: tuple[tuple[int, int], ...]
    payoffs: tuple[tuple[float, float], ...]           # Auszahlung je Runde an a und an b
    cumulative_a: tuple[float, ...]                    # diskontiert kumuliert
    cumulative_b: tuple[float, ...]
    value_a: float                                     # diskontierter Gesamtwert (unendlicher Horizont)
    value_b: float
    average_a: float                                   # mittlere Auszahlung je Runde
    average_b: float
    best_response_a: float                             # bester Wert für a gegen b über alle Strategien
    best_response_b: float
    gain_a: float
    gain_b: float
    is_equilibrium: bool
    threshold: float | None                            # kleinstes δ (Raster 0,01), ab dem (a, b) ein Gleichgewicht ist
    expected_rounds: float


def analyse(settings: Settings) -> Analysis:
    game = settings.game()
    a, b = STRATEGIES[settings.a], STRATEGIES[settings.b]
    history = A.play(a, b, settings.rounds)
    payoffs = A.stage_payoffs(game, history)
    cum_a, cum_b, ca, cb = [], [], 0.0, 0.0
    for t, (ua, ub) in enumerate(payoffs):
        ca += settings.delta ** t * ua
        cb += settings.delta ** t * ub
        cum_a.append(ca)
        cum_b.append(cb)
    d = settings.delta
    return Analysis(
        game=game,
        history=tuple(history),
        payoffs=tuple(payoffs),
        cumulative_a=tuple(cum_a),
        cumulative_b=tuple(cum_b),
        value_a=A.discounted_value(a, b, game, d),
        value_b=A.discounted_value(b, a, game, d),
        average_a=A.average_value(a, b, game, d),
        average_b=A.average_value(b, a, game, d),
        best_response_a=A.best_response_value(b, game, d),
        best_response_b=A.best_response_value(a, game, d),
        gain_a=A.deviation_gain(a, b, game, d),
        gain_b=A.deviation_gain(b, a, game, d),
        is_equilibrium=A.is_equilibrium(a, b, game, d),
        threshold=A.equilibrium_threshold(a, b, game, step=0.01),
        expected_rounds=A.expected_rounds(d),
    )


def action_string(actions) -> str:
    """Aktionsfolge als „C D D …“ (C = kooperiert, D = defektiert)."""
    return " ".join("C" if a == C.COOPERATE else "D" for a in actions)


def strategy_overview(rounds: int = 8) -> list[dict]:
    """Je Strategie: Beschreibung und die eigenen ersten `rounds` Aktionen gegen Immer-Defektieren und gegen einen Abwechsler (D, C, D, C, …).

    Beide Spuren machen sichtbar, was die Worte meinen: wer vergibt, wer nie wieder kooperiert, wer sofort zurückkehrt."""
    rows = []
    for key in C.STRATEGY_KEYS:
        auto = STRATEGIES[key]
        vs_alld = [x for x, _ in A.play(auto, STRATEGIES["ALLD"], rounds)]
        vs_alt = [x for x, _ in A.play(auto, ALTERNATE, rounds)]
        rows.append({"key": key, "label": auto.label, "description": auto.description,
                     "vs_alld": action_string(vs_alld), "vs_alt": action_string(vs_alt)})
    return rows


def payoff_matrix(game: Game, delta: float) -> list[list[float]]:
    """Mittlere Auszahlung je Runde, Zeile gegen Spalte, in der Reihenfolge STRATEGY_KEYS."""
    return [[A.average_value(STRATEGIES[r], STRATEGIES[c], game, delta) for c in C.STRATEGY_KEYS] for r in C.STRATEGY_KEYS]


def equilibrium_pairs(game: Game, delta: float) -> list[tuple[str, str]]:
    """Alle Paare (r, c) mit r vor c in der Reihenfolge, die ein Gleichgewicht der Wiederholung sind (inkl. r = c)."""
    keys = C.STRATEGY_KEYS
    return [
        (keys[i], keys[j])
        for i in range(len(keys)) for j in range(i, len(keys))
        if A.is_equilibrium(STRATEGIES[keys[i]], STRATEGIES[keys[j]], game, delta)
    ]


def threshold_table(game: Game) -> list[dict]:
    """Je Strategie: kleinstes δ, ab dem „beide spielen sie“ ein Gleichgewicht ist; geschlossene Formel, wo es eine gibt."""
    rows = []
    for key in C.STRATEGY_KEYS:
        auto = STRATEGIES[key]
        found = A.equilibrium_threshold(auto, auto, game)
        try:
            formula = A.axelrod_threshold(game, key)
        except ValueError:
            formula = None
        rows.append({"key": key, "label": auto.label, "threshold": found, "formula": formula})
    return rows


def deviation_table(game: Game, delta: float, a_key: str, b_key: str) -> list[dict]:
    """Was Spieler a gegen b bekommt: Beibehalten, drei feste Abweichungen, beste Antwort (alle diskontiert gesamt)."""
    a, b = STRATEGIES[a_key], STRATEGIES[b_key]
    rows = [{"name": f"Beibehalten ({a.label})", "value": A.discounted_value(a, b, game, delta)}]
    for dev in DEVIATIONS:
        rows.append({"name": dev.label, "value": A.discounted_value(dev, b, game, delta)})
    rows.append({"name": "Beste Antwort (alle Strategien)", "value": A.best_response_value(b, game, delta)})
    return rows


def delta_curves(game: Game, a_key: str, b_key: str, deltas=None) -> dict:
    """Mittlere Auszahlung je Runde von a gegen b und die beste Antwort auf b, über δ."""
    deltas = deltas or [round(0.01 * i, 2) for i in range(5, 96)]
    a, b = STRATEGIES[a_key], STRATEGIES[b_key]
    return {
        "delta": deltas,
        "keep": [A.average_value(a, b, game, d) for d in deltas],
        "best": [(1.0 - d) * A.best_response_value(b, game, d) for d in deltas],
    }


def equilibrium_map(game: Game, deltas=C.DELTA_GRID) -> list[list[bool]]:
    """Zeilen = Strategien, Spalten = δ: ist „beide spielen diese Strategie“ ein Gleichgewicht?"""
    return [[A.is_equilibrium(STRATEGIES[k], STRATEGIES[k], game, d) for d in deltas] for k in C.STRATEGY_KEYS]


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    """(Stufe, Satz) für die Kernfrage: trägt die Kooperation zwischen a und b bei diesem δ?"""
    a, b = STRATEGIES[settings.a], STRATEGIES[settings.b]
    d = settings.delta
    if an.is_equilibrium:
        both_coop = all(x == C.COOPERATE and y == C.COOPERATE for x, y in an.history)
        tail = "Beide kooperieren dauerhaft." if both_coop else "Keine Seite gewinnt durch irgendeine Abweichung."
        thr = f" Ab δ = {fmt(an.threshold)} gilt das." if an.threshold is not None else ""
        return "success", f"{a.label} gegen {b.label} ist bei δ = {fmt(d)} ein **Gleichgewicht**. {tail}{thr}"
    side, gain = ("A", an.gain_a) if an.gain_a >= an.gain_b else ("B", an.gain_b)
    who = a.label if side == "A" else b.label
    if an.threshold is None:
        return "warning", (f"{a.label} gegen {b.label} ist bei **keinem** δ ein Gleichgewicht: {who} gewinnt durch Abweichen "
                           f"{fmt(gain)} (diskontiert) bei δ = {fmt(d)}.")
    return "warning", (f"Bei δ = {fmt(d)} lohnt das Abweichen: {who} gewinnt {fmt(gain)} (diskontiert). "
                       f"Das Paar trägt erst ab δ = {fmt(an.threshold)}.")
