"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import tft_constants as C
from tft_scenario import STRATEGIES


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_rounds(history, cumulative_a, cumulative_b, value_a, value_b, label_a, label_b):
    """Oben die Aktionsspur (grün = kooperiert, rot = defektiert), unten der kumulierte diskontierte Wert gegen den Wert des Unendlichen."""
    n = len(history)
    rounds = list(range(1, n + 1))
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.3, 0.7], vertical_spacing=0.08)
    for row_name, idx in ((label_a, 0), (label_b, 1)):
        colors = [C.COLOR_C if h[idx] == C.COOPERATE else C.COLOR_D for h in history]
        texts = ["kooperiert" if h[idx] == C.COOPERATE else "defektiert" for h in history]
        fig.add_trace(go.Scatter(x=rounds, y=[row_name] * n, mode="markers", marker=dict(symbol="square", size=16, color=colors),
                                 text=texts, hovertemplate="Runde %{x}: %{text}<extra>%{y}</extra>", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=rounds, y=list(cumulative_a), mode="lines+markers", name=label_a, line=dict(color=C.COLOR_A, width=3),
                             hovertemplate="Runde %{x}: %{y:.2f}<extra>" + label_a + "</extra>"), row=2, col=1)
    fig.add_trace(go.Scatter(x=rounds, y=list(cumulative_b), mode="lines+markers", name=label_b, line=dict(color=C.COLOR_B, width=3, dash="dot"),
                             hovertemplate="Runde %{x}: %{y:.2f}<extra>" + label_b + "</extra>"), row=2, col=1)
    fig.add_hline(y=value_a, line=dict(color=C.COLOR_A, width=1, dash="dash"), row=2, col=1)
    fig.add_hline(y=value_b, line=dict(color=C.COLOR_B, width=1, dash="dash"), row=2, col=1)
    fig.update_xaxes(title_text="Runde (Woche)", row=2, col=1)
    fig.update_yaxes(title_text="diskontierter Wert", row=2, col=1)
    fig.update_yaxes(autorange="reversed", row=1, col=1)
    return _base(fig, height=430)


def build_delta_curves(curves, threshold, label_keep, label_best):
    """Mittlere Auszahlung je Runde über δ: Beibehalten gegen die beste Abweichung; die Schwelle als senkrechte Linie."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["best"], mode="lines", name=label_best, line=dict(color=C.COLOR_D, width=3, dash="dash"),
                             hovertemplate="δ = %{x:.2f}: %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=curves["delta"], y=curves["keep"], mode="lines", name=label_keep, line=dict(color=C.COLOR_C, width=3),
                             hovertemplate="δ = %{x:.2f}: %{y:.2f}<extra></extra>"))
    if threshold is not None:
        fig.add_vline(x=threshold, line=dict(color="rgba(80,80,80,0.8)", width=1.5, dash="dot"),
                      annotation_text=f"Schwelle δ = {threshold:.2f}".replace(".", ","), annotation_position="top left")
    fig.update_xaxes(title_text="Diskontfaktor δ (Fortsetzungswahrscheinlichkeit)", range=[0.04, 0.96])
    fig.update_yaxes(title_text="mittlere Auszahlung je Runde")
    return _base(fig)


def build_equilibrium_map(flags, deltas=C.DELTA_GRID):
    """Zeilen = Strategien, Spalten = δ; dunkel = „beide spielen sie“ ist ein Gleichgewicht."""
    labels = [STRATEGIES[k].label for k in C.STRATEGY_KEYS]
    z = [[1 if f else 0 for f in row] for row in flags]
    text = [["Gleichgewicht" if f else "Abweichen lohnt" for f in row] for row in flags]
    fig = go.Figure(go.Heatmap(z=z, x=[f"{d:.2f}".replace(".", ",") for d in deltas], y=labels, text=text, zmin=0, zmax=1, showscale=False,
                               colorscale=[[0, "#E9D5D0"], [1, C.COLOR_C]], xgap=2, ygap=2,
                               hovertemplate="%{y}, δ = %{x}: %{text}<extra></extra>"))
    fig.update_yaxes(autorange="reversed", type="category")
    fig.update_xaxes(title_text="Diskontfaktor δ", type="category")
    return _base(fig, height=330)


def build_deviations(rows):
    """Diskontierter Gesamtwert für Spieler A: Beibehalten, drei feste Abweichungen und die beste Antwort."""
    names = [r["name"] for r in rows]
    values = [r["value"] for r in rows]
    best = max(values)
    colors = [C.COLOR_C] + [C.COLOR_D if v > values[0] + 1e-9 else C.COLOR_OTHER for v in values[1:]]
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=colors, text=[f"{v:.2f}".replace(".", ",") for v in values], textposition="outside",
                           hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_yaxes(title_text="diskontierter Gesamtwert", range=[0, best * 1.18 if best > 0 else 1])
    fig.update_xaxes(type="category")
    return _base(fig)
