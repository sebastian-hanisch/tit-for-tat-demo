"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# Aktionen: 0 = kooperieren (C, Rückladung anbieten), 1 = defektieren (D, nur nutzen).
COOPERATE, DEFECT = 0, 1

# Auszahlungen je Woche in 100 EUR (gewählt, nicht gemessen). R ist fest, T, P, S sind Regler.
# Die Grenzen sind so gewählt, dass JEDE Kombination T > R > P > S und 2R > T + S erfüllt (kein berechneter Reglerbereich).
R_FIXED = 3.0
T_MIN, T_MAX, DEFAULT_T, T_STEP = 3.5, 5.0, 5.0, 0.5
P_MIN, P_MAX, DEFAULT_P, P_STEP = 1.0, 2.5, 1.0, 0.5
S_MIN, S_MAX, DEFAULT_S, S_STEP = -1.0, 0.5, 0.0, 0.5

# Schatten der Zukunft: Fortsetzungswahrscheinlichkeit = Diskontfaktor δ je Runde.
DELTA_MIN, DELTA_MAX, DEFAULT_DELTA, DELTA_STEP = 0.05, 0.95, 0.80, 0.01
ROUNDS_MIN, ROUNDS_MAX, DEFAULT_ROUNDS = 6, 40, 20

# Strategien (Reihenfolge = Reihenfolge der Auszahlungsmatrix).
STRATEGY_KEYS = ("ALLC", "ALLD", "TFT", "GRIM", "TF2T", "PAVLOV")
DEFAULT_A, DEFAULT_B = "TFT", "TFT"

# Raster für die Gleichgewichts-Karte und für die Schwellenbestimmung.
DELTA_GRID = tuple(round(0.05 * i, 2) for i in range(1, 20))     # 0,05 ... 0,95
THRESHOLD_STEP = 0.005                                           # Auflösung der δ-Schwelle
EQUILIBRIUM_TOL = 1e-9                                           # Toleranz für „Abweichung lohnt nicht“

COLOR_C = "#2F6B65"
COLOR_D = "#B5483A"
COLOR_A = "#4c78a8"
COLOR_B = "#e08a2c"
COLOR_OTHER = "rgba(150,150,150,0.55)"

PRESETS = {
    "Standardfall: TFT gegen TFT (δ = 0,80)": {
        "delta": DEFAULT_DELTA, "t": DEFAULT_T, "p": DEFAULT_P, "s": DEFAULT_S, "a": "TFT", "b": "TFT", "rounds": DEFAULT_ROUNDS,
    },
    "Kurzer Schatten (δ = 0,40)": {
        "delta": 0.40, "t": DEFAULT_T, "p": DEFAULT_P, "s": DEFAULT_S, "a": "TFT", "b": "TFT", "rounds": DEFAULT_ROUNDS,
    },
    "Grim trägt, TFT nicht (δ = 0,60)": {
        "delta": 0.60, "t": DEFAULT_T, "p": DEFAULT_P, "s": DEFAULT_S, "a": "GRIM", "b": "GRIM", "rounds": DEFAULT_ROUNDS,
    },
    "Knapp unter der TFT-Schwelle (δ = 0,66)": {
        "delta": 0.66, "t": DEFAULT_T, "p": DEFAULT_P, "s": DEFAULT_S, "a": "TFT", "b": "TFT", "rounds": DEFAULT_ROUNDS,
    },
    "Ausbeutung: TFT gegen Immer-D": {
        "delta": DEFAULT_DELTA, "t": DEFAULT_T, "p": DEFAULT_P, "s": DEFAULT_S, "a": "TFT", "b": "ALLD", "rounds": DEFAULT_ROUNDS,
    },
}
PRESET_HELP = {
    "Standardfall: TFT gegen TFT (δ = 0,80)": "Zwei Spediteure mit Tit-for-Tat, Auszahlungen 5/3/1/0, die Beziehung läuft im Mittel fünf Wochen weiter. Kooperation trägt.",
    "Kurzer Schatten (δ = 0,40)": "Die Beziehung endet schnell (im Mittel 1,7 Wochen): jetzt lohnt Defektion, auch gegen Tit-for-Tat.",
    "Grim trägt, TFT nicht (δ = 0,60)": "Zwischen den beiden Schwellen: Grim Trigger hält Kooperation stabil, Tit-for-Tat gegen Tit-for-Tat nicht mehr.",
    "Knapp unter der TFT-Schwelle (δ = 0,66)": "Die Schwelle von Tit-for-Tat liegt bei 2/3: knapp darunter lohnt das Abwechseln von Defektion und Kooperation.",
    "Ausbeutung: TFT gegen Immer-D": "Tit-for-Tat wird nur in der ersten Woche ausgebeutet (S gegen T); danach bekommen beide P. Für Immer-Defektieren wäre Kooperation mit Tit-for-Tat besser.",
}
