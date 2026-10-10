"""Kern der Demo (nur numpy/Standardbibliothek): das wiederholte Gefangenendilemma mit Diskontierung.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b):

- `play`                   spielt zwei Automaten Runde für Runde (die sichtbare Spur)
- `discounted_value`       diskontierter Gesamtwert eines Paares (lineares Gleichungssystem über die gemeinsamen Zustände)
- `best_response_value`    bester erreichbarer Wert gegen einen festen Automaten (Politikiteration über seine Zustände), gegen ALLE Strategien
- `deviation_gain`         was Abweichen gegenüber dem Beibehalten bringt
- `is_equilibrium`         Nash-Gleichgewicht der Wiederholung: keine Seite gewinnt durch irgendeine Abweichung
- `equilibrium_threshold`  kleinstes δ, ab dem ein Paar auf dem δ-Raster ein Gleichgewicht ist
- `axelrod_threshold`      die geschlossene Formel zum Vergleich (Axelrod 1984)

`solve` im Sinn anderer Demos gibt es nicht: die Komposition steht in tft_evaluation.py."""

from functools import lru_cache

import numpy as np

import tft_constants as C
from tft_scenario import Automaton, Game


def play(a: Automaton, b: Automaton, rounds: int) -> list[tuple[int, int]]:
    """Die ersten `rounds` Aktionspaare (Aktion von a, Aktion von b); beide starten im Zustand 0."""
    sa = sb = 0
    out = []
    for _ in range(rounds):
        x, y = a.act(sa), b.act(sb)
        out.append((x, y))
        sa, sb = a.step(sa, y), b.step(sb, x)
    return out


def stage_payoffs(game: Game, history: list[tuple[int, int]]) -> list[tuple[float, float]]:
    """Auszahlung je Runde an a und an b."""
    return [(game.stage(x, y), game.stage(y, x)) for x, y in history]


def discounted_value(a: Automaton, b: Automaton, game: Game, delta: float) -> float:
    """Diskontierter Gesamtwert für a gegen b: V = Σ δ^t · u_t.

    Der gemeinsame Zustand (sa, sb) bestimmt die Aktionen und den Folgezustand eindeutig, also gilt
    V(sa, sb) = u(sa, sb) + δ · V(Folgezustand). Das ist ein lineares System (I − δP) V = u."""
    na, nb = a.size, b.size
    n = na * nb
    mat = np.eye(n)
    rhs = np.zeros(n)
    for sa in range(na):
        for sb in range(nb):
            i = sa * nb + sb
            x, y = a.act(sa), b.act(sb)
            rhs[i] = game.stage(x, y)
            j = a.step(sa, y) * nb + b.step(sb, x)
            mat[i, j] -= delta
    return float(np.linalg.solve(mat, rhs)[0])


def average_value(a: Automaton, b: Automaton, game: Game, delta: float) -> float:
    """Mittlere Auszahlung je Runde: (1 − δ) · V."""
    return (1.0 - delta) * discounted_value(a, b, game, delta)


def evaluate_policy(opp: Automaton, game: Game, delta: float, policy: tuple[int, ...]) -> np.ndarray:
    """Wert W(s) je Zustand des Gegners, wenn wir in Zustand s die Aktion policy[s] spielen: (I − δP) W = u."""
    n = opp.size
    mat = np.eye(n)
    rhs = np.zeros(n)
    for s in range(n):
        x = policy[s]
        rhs[s] = game.stage(x, opp.act(s))
        mat[s, opp.step(s, x)] -= delta
    return np.linalg.solve(mat, rhs)


@lru_cache(maxsize=None)
def best_response_policy(opp: Automaton, game: Game, delta: float) -> tuple[tuple[int, ...], float]:
    """Beste Politik (Aktion je Zustand des Gegners) und ihr Wert gegen `opp`, per Politikiteration (Howard 1960).

    Der Gegner ist fest, also ist seine Zustandsmenge der gesamte relevante Zustand eines Entscheidungsprozesses. Das Maximum
    läuft über ALLE Strategien, nicht nur über die sechs Automaten der Demo. Bei Gleichstand bleibt die bisherige Aktion (Abbruch)."""
    policy = tuple(C.COOPERATE for _ in range(opp.size))
    for _ in range(64):
        w = evaluate_policy(opp, game, delta, policy)
        new = []
        for s in range(opp.size):
            y = opp.act(s)
            q = [game.stage(x, y) + delta * w[opp.step(s, x)] for x in (C.COOPERATE, C.DEFECT)]
            best = int(np.argmax(q))
            new.append(policy[s] if q[policy[s]] >= q[best] - 1e-12 else best)
        new = tuple(new)
        if new == policy:
            return policy, float(w[0])
        policy = new
    raise RuntimeError("Politikiteration ohne Konvergenz")  # praktisch unerreichbar: endliche Politikmenge, streng monoton


def best_response_value(opp: Automaton, game: Game, delta: float) -> float:
    """Bester diskontierter Wert, den irgendeine Strategie gegen `opp` erreichen kann."""
    return best_response_policy(opp, game, delta)[1]


def deviation_gain(a: Automaton, b: Automaton, game: Game, delta: float) -> float:
    """Wie viel a durch die beste Abweichung gegen b gewinnen könnte (≥ 0; 0 heißt: a ist bereits Bestantwort)."""
    return max(0.0, best_response_value(b, game, delta) - discounted_value(a, b, game, delta))


def is_equilibrium(a: Automaton, b: Automaton, game: Game, delta: float, tol: float = C.EQUILIBRIUM_TOL) -> bool:
    """Gleichgewicht der Wiederholung: Weder a gegen b noch b gegen a gewinnt durch irgendeine Abweichung mehr als `tol`."""
    return deviation_gain(a, b, game, delta) <= tol and deviation_gain(b, a, game, delta) <= tol


def equilibrium_threshold(a: Automaton, b: Automaton, game: Game, step: float = C.THRESHOLD_STEP) -> float | None:
    """Kleinstes δ auf dem Raster, ab dem (a, b) für ALLE größeren Rasterwerte ein Gleichgewicht ist; None, wenn nie."""
    grid = [round(step * i, 6) for i in range(1, int(round(1.0 / step)))]
    good = [is_equilibrium(a, b, game, d) for d in grid]
    if not good[-1]:
        return None
    first = len(good)
    for i in range(len(good) - 1, -1, -1):
        if not good[i]:
            break
        first = i
    return grid[first]


def axelrod_threshold(game: Game, strategy: str) -> float:
    """Geschlossene δ-Schwelle des Gleichgewichts „beide spielen `strategy`“.

    TFT: max{(T−R)/(T−P), (T−R)/(R−S)} (Axelrod 1984): Immer-D und das Abwechseln D, C sind die beiden gefährlichen Abweichungen.
    Grim Trigger: (T−R)/(T−P): nach der ersten Defektion folgt Immer-D, also bleibt nur Immer-D als Abweichung."""
    t, r, p, s = game.t, game.r, game.p, game.s
    if strategy == "TFT":
        return max((t - r) / (t - p), (t - r) / (r - s))
    if strategy == "GRIM":
        return (t - r) / (t - p)
    raise ValueError(f"keine geschlossene Formel für {strategy}")


def expected_rounds(delta: float) -> float:
    """Erwartete Zahl der Runden, wenn die Beziehung mit Wahrscheinlichkeit δ weitergeht: 1 / (1 − δ)."""
    return 1.0 / (1.0 - delta)
