"""Tit-for-Tat und der Schatten der Zukunft - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Wurzel der Wiederholte-Spiele-Linie: zwei Spediteure tauschen jede Woche Rückladungen (Gefangenendilemma) und treffen sich wieder.
Gezeigt wird, ab welchem Diskontfaktor δ die Drohung der Vergeltung Kooperation trägt, gegen ALLE möglichen Abweichungen geprüft.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import tft_constants as C
import tft_evaluation as E
from tft_evaluation import Settings, fmt
from tft_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from tft_scenario import STRATEGIES
from tft_visualization import build_delta_curves, build_deviations, build_equilibrium_map, build_rounds

st.set_page_config(page_title="Tit-for-Tat und der Schatten der Zukunft – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _curves(settings):
    return E.delta_curves(settings.game(), settings.a, settings.b)


@st.cache_data(show_spinner=False)
def _thresholds(settings):
    return E.threshold_table(settings.game())


@st.cache_data(show_spinner=False)
def _deviations(settings):
    return E.deviation_table(settings.game(), settings.delta, settings.a, settings.b)


@st.cache_data(show_spinner=False)
def _equilibrium_map(settings):
    return E.equilibrium_map(settings.game())


@st.cache_data(show_spinner=False)
def _matrix(settings):
    return E.payoff_matrix(settings.game(), settings.delta), E.equilibrium_pairs(settings.game(), settings.delta)


st.title("🔁 Tit-for-Tat und der Schatten der Zukunft")
st.markdown(
    """
Zwei Spediteure fahren dieselbe Relation. Jede Woche kann jeder eine **Rückladung anbieten** (kooperieren) oder die des anderen **nur nutzen**
(defektieren). Im Einmalspiel lohnt Defektion immer, das zeigt [nash-demo](https://sebastianhanisch-nash-demo.streamlit.app/) für
Überlastungsspiele. Treffen sich beide **wieder**, kann die Drohung der Vergeltung Kooperation tragen, aber nur, wenn die Beziehung lang genug
weiterläuft: Das ist der **Schatten der Zukunft** δ. Diese Demo prüft **exakt**, ab welchem δ Tit-for-Tat und seine Verwandten tragen, gegen
*jede* mögliche Abweichung.

Weiter unten: drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Eigennutz und die
Auszahlungen sind Modellannahmen (gewählt, nicht gemessen), kein Befund über echte Spediteure.
"""
)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/tit-for-tat-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Zwei Spediteure können sich jede Woche eine Rückladung anbieten. Einzeln betrachtet lohnt es sich, die Rückladung des anderen nur zu nutzen. Treffen sich beide nur einmal, ist das die beste Wahl, obwohl beide mit gegenseitigem Tauschen besser führen. Ein solches Spiel heißt **Gefangenendilemma**.

Treffen sich beide jede Woche **wieder**, kann **Tit-for-Tat** helfen: in der ersten Woche anbieten, danach tun, was der andere zuletzt getan hat. Wer nur nutzt, bekommt in der nächsten Woche selbst nichts angeboten.

Entscheidend ist der **Schatten der Zukunft**: die Wahrscheinlichkeit, dass die Beziehung nach einer Woche weiterläuft. Erst ab einer Schwelle trägt die Drohung. Die Demo rechnet diese Schwelle exakt aus und prüft jede mögliche Abweichung, nicht nur einige. Kooperation ist dabei ein stabiler Zustand unter mehreren, keine Vorhersage.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/tit-for-tat-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert Tit-for-Tat", expanded=True):
    st.markdown(
        """
1. **Runde 1: kooperieren.** Tit-for-Tat beginnt freundlich.
2. **Danach: genau das tun, was der andere zuletzt getan hat.** Wer defektiert, wird in der nächsten Woche mit Defektion beantwortet; wer
   zur Kooperation zurückkehrt, bekommt sie sofort zurück.
3. **Warum das tragen kann:** Eine Defektion bringt einmal *T* statt *R*, kostet aber die Strafe in den Folgewochen. Ab einem
   Schwellen-δ ist der diskontierte Verlust größer als der Gewinn, und niemand hat einen Grund abzuweichen. Die Demo rechnet das nicht
   nur für Tit-for-Tat, sondern gegen die **beste mögliche Antwort** aus.
        """
    )

with st.expander("Die sechs Strategien: wer macht was?", expanded=True):
    st.markdown(
        "Jede Strategie entscheidet jede Woche, ob sie **kooperiert (C)** oder **defektiert (D)**, und kennt dafür nur, was bisher passiert ist. "
        "Die beiden rechten Spalten zeigen, was die Strategie in den ersten acht Wochen **selbst tut**, wenn der Gegner immer defektiert "
        "beziehungsweise abwechselnd defektiert und kooperiert (D, C, D, C, …). Daran sieht man, wer vergibt und wer nicht."
    )
    rows_md = ["| Strategie | Verhalten | Gegen Immer-D | Gegen Abwechsler (D, C, …) |", "|---|---|---|---|"]
    for r in E.strategy_overview():
        rows_md.append(f"| **{r['label']}** | {r['description']} | `{r['vs_alld']}` | `{r['vs_alt']}` |")
    st.markdown("\n".join(rows_md))
    st.caption(
        "Lesebeispiel: Gegen den Abwechsler bleibt Tit-for-Tat bei „C D C D …“, weil es jede Aktion nur zurückspielt; Grim Trigger bleibt nach der "
        "ersten Defektion für immer bei D."
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Beziehung**")
    delta = st.slider("Schatten der Zukunft δ", *bounds("delta_slider"), step=C.DELTA_STEP, key="delta_slider",
                      help="Wahrscheinlichkeit, dass die Beziehung nach einer Woche weiterläuft. Erwartete Dauer: 1 / (1 − δ) Wochen.")
    st.markdown("**Strategien**")
    a_key = st.selectbox("Spediteur A", C.STRATEGY_KEYS, key="a_select", format_func=lambda k: STRATEGIES[k].label,
                         help="Die Strategie von Spediteur A (Zeile in den Tabellen).")
    b_key = st.selectbox("Spediteur B", C.STRATEGY_KEYS, key="b_select", format_func=lambda k: STRATEGIES[k].label,
                         help="Die Strategie von Spediteur B (Spalte in den Tabellen).")
    st.caption(f"**A, {STRATEGIES[a_key].label}:** {STRATEGIES[a_key].description}")
    st.caption(f"**B, {STRATEGIES[b_key].label}:** {STRATEGIES[b_key].description}")
    st.markdown("**Auszahlungen je Woche (in 100 EUR)**")
    t_val = st.slider("T: nur nutzen, nichts anbieten", *bounds("t_slider"), step=C.T_STEP, key="t_slider",
                      help="Versuchung: ich nutze die Rückladung des anderen und biete nichts an. Muss über R = 3 liegen.")
    st.caption(f"R = {fmt(C.R_FIXED, 1)} (beide tauschen) ist fest.")
    p_val = st.slider("P: keiner tauscht", *bounds("p_slider"), step=C.P_STEP, key="p_slider",
                      help="Beide fahren leer zurück. Muss zwischen S und R liegen.")
    s_val = st.slider("S: angeboten, nichts bekommen", *bounds("s_slider"), step=C.S_STEP, key="s_slider",
                      help="Ich biete an, der andere nutzt nur. Der niedrigste Wert.")
    st.markdown("**Anzeige**")
    rounds = st.slider("Gezeigte Runden", *bounds("rounds_slider"), key="rounds_slider",
                       help="Wie viele Wochen die Spur zeigt. Die Werte rechnen immer über den unendlichen Horizont.")

sync_query_params({"delta_slider": round(float(delta), 2), "t_slider": float(t_val), "p_slider": float(p_val), "s_slider": float(s_val),
                   "a_select": a_key, "b_select": b_key, "rounds_slider": int(rounds)})

settings = Settings(round(float(delta), 2), float(t_val), float(p_val), float(s_val), a_key, b_key, int(rounds))
an = _analysis(settings)
label_a, label_b = STRATEGIES[a_key].label, STRATEGIES[b_key].label

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown(f"## 🎬 Runde für Runde: {label_a} gegen {label_b}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Wert für A (diskontiert)", fmt(an.value_a), delta=f"{fmt(an.average_a)} je Woche im Mittel", delta_color="off")
m2.metric("Wert für B (diskontiert)", fmt(an.value_b), delta=f"{fmt(an.average_b)} je Woche im Mittel", delta_color="off")
m3.metric("Erwartete Dauer", f"{fmt(an.expected_rounds, 1)} Wochen", delta="1 / (1 − δ)", delta_color="off")
m4.metric("Gleichgewicht?", "ja" if an.is_equilibrium else "nein",
          delta=f"Abweichen bringt A {fmt(an.gain_a)}, B {fmt(an.gain_b)}", delta_color="off")
st.plotly_chart(build_rounds(an.history, an.cumulative_a, an.cumulative_b, an.value_a, an.value_b, f"A: {label_a}", f"B: {label_b}"),
                width="stretch", key="rounds_chart")
st.caption(
    "Oben: grün = kooperiert, rot = defektiert, Zeile A und Zeile B. Unten: der bis zur Runde angesammelte, diskontierte Wert; die gestrichelten "
    "Linien sind der Wert über den unendlichen Horizont, dem die Linien zustreben."
)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Trägt Kooperation bei diesem Schatten der Zukunft?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info}[level](sentence)

st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Ab welchem δ lohnt die beste Abweichung nicht mehr?")
st.caption(
    f"Mittlere Auszahlung je Woche von A ({label_a}) gegen B ({label_b}): wenn A bei seiner Strategie bleibt (grün) gegen die beste Antwort aus "
    "allen Strategien (rot gestrichelt). Wo die grüne Linie die rote berührt, trägt das Paar."
)
curves = _curves(settings)
st.plotly_chart(build_delta_curves(curves, an.threshold, f"A bleibt bei {label_a}", "A weicht optimal ab"), width="stretch", key="delta_chart")
table = _thresholds(settings)
rows_md = ["| Strategie (beide spielen sie) | Schwelle gemessen | geschlossene Formel |", "|---|---|---|"]
for r in table:
    if r["threshold"] is None:
        measured = "nie (bis δ = 0,99)"
    elif r["threshold"] <= C.THRESHOLD_STEP + 1e-9:
        measured = "bei jedem δ"
    else:
        measured = f"δ ≥ {fmt(r['threshold'], 3)}"
    formula = "–" if r["formula"] is None else f"δ ≥ {fmt(r['formula'], 3)}"
    rows_md.append(f"| {r['label']} | {measured} | {formula} |")
st.markdown("\n".join(rows_md))
tft_row = next(r for r in table if r["key"] == "TFT")
grim_row = next(r for r in table if r["key"] == "GRIM")
if tft_row["threshold"] is not None and grim_row["threshold"] is not None and tft_row["threshold"] > grim_row["threshold"] + 1e-9:
    st.info(
        f"Grim Trigger trägt schon ab δ = {fmt(grim_row['threshold'], 2)}, Tit-for-Tat erst ab δ = {fmt(tft_row['threshold'], 2)}. Der Unterschied ist "
        "die **Nachsicht**: Gegen Tit-for-Tat lohnt das Abwechseln von Defektion und Kooperation, weil nach jeder Defektion sofort wieder "
        "kooperiert wird; Grim lässt diese Lücke nicht."
    )
else:
    st.info("Bei dieser Auszahlungswahl liegen die Schwellen von Tit-for-Tat und Grim Trigger gleich hoch: kein Unterschied durch Nachsicht.")

st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader(f"🔬 Experiment: Welche Abweichung lohnt gegen {label_b}?")
st.caption(f"Diskontierter Gesamtwert für A bei δ = {fmt(settings.delta)}: bleiben gegen drei feste Abweichungen und gegen die beste Antwort aus allen Strategien.")
devs = _deviations(settings)
st.plotly_chart(build_deviations(devs), width="stretch", key="deviation_chart")
keep_value = devs[0]["value"]
best_value = devs[-1]["value"]
beating = [d["name"] for d in devs[1:-1] if d["value"] > keep_value + 1e-9]
if best_value <= keep_value + 1e-9:
    st.success(f"Keine Abweichung schlägt {label_a} gegen {label_b} bei δ = {fmt(settings.delta)}: die beste Antwort ist {label_a} selbst (Wert {fmt(keep_value)}).")
else:
    named = ", ".join(beating) if beating else "keine der drei festen Abweichungen, aber eine andere Strategie"
    st.warning(
        f"Abweichen lohnt: die beste Antwort bringt {fmt(best_value)} statt {fmt(keep_value)} (+{fmt(best_value - keep_value)}). "
        f"Schlagen {label_a}: {named}."
    )

st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wer ist mit wem im Gleichgewicht?")
st.caption("Dunkel: „beide spielen diese Strategie“ ist ein Gleichgewicht, das heißt, keine Abweichung (aus allen Strategien) lohnt.")
st.plotly_chart(build_equilibrium_map(_equilibrium_map(settings)), width="stretch", key="map_chart")
matrix, pairs = _matrix(settings)
pair_text = ", ".join(f"{STRATEGIES[x].label} / {STRATEGIES[y].label}" for x, y in pairs)
st.info(f"Bei δ = {fmt(settings.delta)} sind unter den sechs Strategien **{len(pairs)}** Paare Gleichgewichte: {pair_text}. "
        "Immer-Defektieren ist es bei **jedem** δ; Kooperation ist ein Gleichgewicht unter mehreren, nicht die Vorhersage.")
with st.expander("Auszahlungsmatrix: mittlere Auszahlung je Woche, Zeile gegen Spalte"):
    head = "| Zeile \\ Spalte | " + " | ".join(STRATEGIES[k].label for k in C.STRATEGY_KEYS) + " |"
    sep = "|---|" + "---|" * len(C.STRATEGY_KEYS)
    body = [f"| **{STRATEGIES[r].label}** | " + " | ".join(fmt(v) for v in row) + " |" for r, row in zip(C.STRATEGY_KEYS, matrix)]
    st.markdown("\n".join([head, sep] + body))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Auszahlungen 5/3/1/0 stimmen** | Sie sind gewählt, nicht gemessen. Die Schwellen verschieben sich mit T, P und S (Regler); die Aussage „ab δ trägt es“ gilt nur für diese Zahlen. | - |
| **Beide beobachten die Aktion des anderen fehlerfrei** | Das Modell kennt keine Verwechslung und keinen Fehlgriff. Was ein einzelner Fehler bei Tit-for-Tat auslöst, zeigt diese Demo nicht. | - |
| **Genau zwei feste Partner, immer dieselben** | Wechselnde Partner brauchen Reputation statt Gedächtnis: dieses Modell kennt weder Dritte noch Bündnisse. | - |
| **Das Ende ist unbekannt (Fortsetzungswahrscheinlichkeit δ)** | Ein bekanntes Ende ändert die Rechnung: die Strafdrohung der letzten Runde fällt weg. δ ist hier eine Wahrscheinlichkeit, kein Zeitpräferenz-Faktor. | - |
| **Gleichgewicht ist keine Vorhersage** | Es gibt viele Gleichgewichte (Immer-Defektieren immer); welches gespielt wird, sagt die Rechnung nicht. | `noregret-demo` zeigt, wie Spieler aus Erfahrung zu einem finden |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/tit-for-tat-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind ein Spiel mit den Auszahlungen $T$, $R$, $P$, $S$, die Fortsetzungswahrscheinlichkeit $\delta$ und zwei Strategien als Automaten. Gesucht ist der diskontierte Wert beider Spieler und die Frage, ab welchem $\delta$ keine Abweichung lohnt (Gleichgewicht).

| Symbol | Bedeutung |
|---|---|
| $C$, $D$ | kooperieren (Rückladung anbieten) bzw. defektieren (die des anderen nur nutzen) |
| $T$, $R$, $P$, $S$ | Auszahlung je Woche: nur nutzen ($T$), beide tauschen ($R$), keiner tauscht ($P$), angeboten und nichts bekommen ($S$) |
| $\delta$ | Schatten der Zukunft: Wahrscheinlichkeit, dass die Beziehung nach einer Woche weiterläuft; erwartete Dauer $1/(1-\delta)$ Wochen |
| $s$, $s'$ | Zustand eines Automaten bzw. sein Folgezustand |
| $u(s)$ | Auszahlung des Spielers im gemeinsamen Zustand $s$ der beiden Automaten |
| $P$ (in $I - \delta P$) | Übergangsmatrix der gemeinsamen Zustände (nicht die Auszahlung $P$); $I$ ist die Einheitsmatrix |
| $V$ | diskontierter Wert eines Strategiepaares (Vektor über die gemeinsamen Zustände) |
| $W(s)$ | bester erreichbarer Wert gegen einen festen Automaten, wenn dieser im Zustand $s$ ist |
| $x$ | gewählte Aktion in der Bellman-Gleichung für die beste Antwort ($C$ oder $D$) |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/tit-for-tat-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(
        r"""
**Spiel.** Je Runde wählen beide Spieler $C$ (kooperieren) oder $D$ (defektieren). Auszahlungen für den Spieler, dessen Aktion zuerst steht:
$(D,C) = T$, $(C,C) = R$, $(D,D) = P$, $(C,D) = S$ mit $T > R > P > S$ und $2R > T + S$. Die Beziehung läuft mit Wahrscheinlichkeit $\delta$
weiter, also zählt Runde $t$ mit Gewicht $\delta^t$ und die erwartete Dauer ist $1/(1-\delta)$.

**Strategien als Automaten.** Je Zustand eine Aktion; der Folgezustand hängt von der letzten Aktion des Gegners ab. Zwei Automaten
bilden einen gemeinsamen Zustand $(s_A, s_B)$, der die Spur eindeutig festlegt. Der diskontierte Wert löst
$V(s) = u(s) + \delta\, V(s')$, also das lineare System $(I - \delta P)\,V = u$.

**Beste Antwort.** Gegen einen festen Automaten ist dessen Zustandsmenge der gesamte relevante Zustand eines Entscheidungsprozesses:
$W(s) = \max_{x \in \{C,D\}} \big[\, u(x, \text{Aktion}(s)) + \delta\, W(s'(s,x)) \,\big]$. Das Maximum läuft über **alle** Strategien, nicht nur über die
sechs der Demo. Gelöst wird per Politikiteration. Ein Paar ist ein **Gleichgewicht**, wenn $V(A,B) \ge W_B(0)$ und $V(B,A) \ge W_A(0)$.

**Schwellen (Tit-for-Tat gegen Tit-for-Tat).** Zwei Abweichungen sind gefährlich: Immer-$D$ bringt $T + \delta P/(1-\delta)$ gegen
$R/(1-\delta)$, also $\delta \ge (T-R)/(T-P)$. Das Abwechseln $D, C, D, C, \dots$ bringt $(T + \delta S)/(1-\delta^2)$, also
$\delta \ge (T-R)/(R-S)$. Zusammen: $\delta \ge \max\{(T-R)/(T-P),\,(T-R)/(R-S)\}$. Bei $5/3/1/0$ sind das $1/2$ und $2/3$. Gegen Grim Trigger
fällt das Abwechseln weg (nach der ersten Defektion folgt Immer-$D$): $\delta \ge (T-R)/(T-P)$.

**Literatur.** Axelrod und Hamilton (1981), *The Evolution of Cooperation*, Science 211, 1390–1396 (Tit-for-Tat im Turnier und als
evolutionär stabile Strategie); Axelrod (1981), *The Emergence of Cooperation among Egoists*, American Political Science Review 75,
306–318, und Axelrod (1984), *The Evolution of Cooperation*, Basic Books (Schwelle der „kollektiven Stabilität“ von Tit-for-Tat in
Abhängigkeit von T, R, P, S; die Formel oben ist hier hergeleitet und exakt nachgerechnet, nicht aus dem Buch übernommen); Friedman (1971),
*A Non-cooperative Equilibrium for Supergames*, Review of Economic Studies 38, 1–12 (Grim Trigger, bei Axelrod „Friedman“); Howard (1960),
*Dynamic Programming and Markov Processes*, Technology Press und Wiley (Politikiteration; nur über Bibliografien bestätigt, nicht im
Volltext gelesen).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
