"""Szenario: das Rückladungs-Dilemma (Gefangenendilemma) und die Strategien als endliche Automaten.

Eine Strategie ist ein deterministischer Automat: je Zustand eine Aktion, und der nächste Zustand hängt nur von der Aktion des
Gegners ab. Damit ist der Gegner für die Bestantwort-Rechnung ein Markov-Entscheidungsprozess mit wenigen Zuständen."""

from dataclasses import dataclass

import tft_constants as C


@dataclass(frozen=True)
class Game:
    """Auszahlungen je Runde an den Spieler, dessen Aktion zuerst steht: (D,C) = T, (C,C) = R, (D,D) = P, (C,D) = S."""
    t: float = C.DEFAULT_T
    r: float = C.R_FIXED
    p: float = C.DEFAULT_P
    s: float = C.DEFAULT_S

    def __post_init__(self):
        if not (self.t > self.r > self.p > self.s and 2 * self.r > self.t + self.s):
            raise ValueError(f"kein Gefangenendilemma: T={self.t}, R={self.r}, P={self.p}, S={self.s}")

    def stage(self, own: int, other: int) -> float:
        """Auszahlung einer Runde für die eigene Aktion `own` gegen `other` (0 = C, 1 = D)."""
        if own == C.COOPERATE:
            return self.r if other == C.COOPERATE else self.s
        return self.t if other == C.COOPERATE else self.p


@dataclass(frozen=True)
class Automaton:
    key: str
    label: str
    outputs: tuple[int, ...]                 # Aktion je Zustand
    trans: tuple[tuple[int, int], ...]       # trans[zustand][aktion des Gegners] = nächster Zustand
    description: str

    @property
    def size(self) -> int:
        return len(self.outputs)

    def act(self, state: int) -> int:
        return self.outputs[state]

    def step(self, state: int, opponent_action: int) -> int:
        return self.trans[state][opponent_action]


def _automata() -> dict[str, Automaton]:
    c, d = C.COOPERATE, C.DEFECT
    items = [
        Automaton("ALLC", "Immer kooperieren", (c,), ((0, 0),),
                  "Bietet jede Woche eine Rückladung an, egal was der andere tut."),
        Automaton("ALLD", "Immer defektieren", (d,), ((0, 0),),
                  "Nutzt nur, bietet nie an."),
        Automaton("TFT", "Tit-for-Tat", (c, d), ((0, 1), (0, 1)),
                  "Beginnt mit Kooperation und macht danach exakt das, was der andere zuletzt getan hat."),
        Automaton("GRIM", "Grim Trigger", (c, d), ((0, 1), (1, 1)),
                  "Kooperiert, bis der andere einmal defektiert; danach nie wieder."),
        Automaton("TF2T", "Tit-for-Two-Tats", (c, c, d), ((0, 1), (0, 2), (0, 2)),
                  "Verzeiht eine einzelne Defektion; defektiert erst nach zwei Defektionen in Folge."),
        Automaton("PAVLOV", "Pavlov (Win-Stay-Lose-Shift)", (c, d), ((0, 1), (1, 0)),
                  "Behält die letzte Aktion bei, wenn der andere kooperiert hat (Gewinn), und wechselt sie, wenn er defektiert hat."),
    ]
    return {a.key: a for a in items}


STRATEGIES = _automata()

# Hilfsautomaten für die Abweichungs-Analyse (nicht in der Strategienwahl der App).
ALTERNATE = Automaton("ALT", "Abwechselnd D, C", (C.DEFECT, C.COOPERATE), ((1, 1), (0, 0)), "Defektiert und kooperiert im Wechsel.")
ONE_SHOT = Automaton("ONE", "Einmal D, dann C", (C.DEFECT, C.COOPERATE), ((1, 1), (1, 1)), "Defektiert nur in der ersten Runde.")
DEVIATIONS = (
    STRATEGIES["ALLD"],
    ALTERNATE,
    ONE_SHOT,
)


def make_game(t: float, p: float, s: float) -> Game:
    return Game(t=float(t), r=C.R_FIXED, p=float(p), s=float(s))
