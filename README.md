# Tit-for-Tat und der Schatten der Zukunft – Streamlit-Demo

<!-- Nach dem Deploy direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/)** -->

Erstes Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Wurzel der Linie. Vorgänger außerhalb der Linie ist [nash-demo](https://sebastianhanisch-nash-demo.streamlit.app/): dort ist das Spiel einmalig und Eigennutz gewinnt
immer. Hier treffen sich dieselben zwei Spediteure **wieder**, und die Drohung der Vergeltung kann Kooperation tragen.

Vehikel: **Rückladungstausch.** Zwei Spediteure fahren dieselbe Relation; jede Woche kann jeder eine Rückladung anbieten (kooperieren) oder die des anderen nur
nutzen (defektieren). Auszahlungen je Woche in 100 EUR: T = 5 (nur nutzen), R = 3 (beide tauschen), P = 1 (keiner tauscht), S = 0 (angeboten, nichts bekommen);
gewählt, nicht gemessen. Eigennutz und Rationalität der Spediteure sind Modellannahmen, kein Befund über echte Betriebe.

## Warum dieses Problem

Im Einmalspiel ist Defektion für beide die beste Antwort, obwohl beide mit Kooperation besser führen. In der Wiederholung kann ein Spieler Kooperation mit einer Strafe
absichern. Die Frage ist, **wie lang die Beziehung weiterlaufen muss**, damit die Strafe schwerer wiegt als der Gewinn der Defektion: ab welchem Diskontfaktor δ (hier die
Wahrscheinlichkeit, dass die Beziehung nach einer Woche weiterläuft) trägt Tit-for-Tat, und warum trägt Grim Trigger früher?

## Modell

Strategien sind endliche Automaten: je Zustand eine Aktion, der Folgezustand hängt von der letzten Aktion des Gegners ab. Sechs stehen zur Wahl: Immer kooperieren,
Immer defektieren, Tit-for-Tat, Grim Trigger, Tit-for-Two-Tats und Pavlov (Win-Stay-Lose-Shift). Der diskontierte Wert eines Paares ist die Lösung eines linearen
Systems über die gemeinsamen Zustände; die **beste Antwort** auf einen festen Automaten ist ein Entscheidungsprozess über dessen Zustände und läuft über **alle**
Strategien, nicht nur über die sechs. Ein Paar ist ein Gleichgewicht, wenn keine Seite durch irgendeine Abweichung gewinnt. Formeln im 📐-Expander der App.

## Methodik

- **Strategien erklärt:** Die App zeigt eine Überblickstabelle der sechs Strategien (Beschreibung und ihre eigenen ersten acht Aktionen gegen Immer-D und gegen einen Abwechsler) und erklärt die gewählten Strategien A und B in der Seitenleiste (`tft_evaluation.strategy_overview`, Test `test_strategy_overview_traces_by_hand`).
- **Wert eines Paares:** lineares System `(I − δP) V = u` über die gemeinsamen Zustände (`tft_algorithm.discounted_value`).
- **Beste Antwort:** Politikiteration über die Zustände des Gegners (`best_response_policy`), exakt und mit wenigen Schritten.
- **Gleichgewicht und Schwelle:** `is_equilibrium`, `equilibrium_threshold` (kleinstes δ auf dem Raster, ab dem das Paar für alle größeren δ trägt).
- **Geschlossene Formel zum Vergleich:** `axelrod_threshold`: für Tit-for-Tat max{(T−R)/(T−P), (T−R)/(R−S)}, für Grim Trigger (T−R)/(T−P).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen bei T/R/P/S = 5/3/1/0, wenn nicht anders genannt.

| Frage | Befund | Test |
|---|---|---|
| Ab welchem δ trägt Tit-for-Tat gegen Tit-for-Tat? | Ab δ = 2/3 (Raster: 0,67). Die engere Abweichung ist das **Abwechseln** von Defektion und Kooperation, nicht Immer-Defektieren (das schon ab 1/2 aufhört zu lohnen). | `test_threshold_of_tft_is_two_thirds_and_of_grim_one_half`, `test_tft_threshold_is_the_larger_of_the_two_deviations` |
| Und Grim Trigger? | Schon ab δ = 1/2: Die Nachsicht von Tit-for-Tat (sofortige Rückkehr zur Kooperation) öffnet die Lücke, die Grim nicht hat. Bei δ = 0,60 trägt Grim, Tit-for-Tat nicht. | `test_grim_holds_where_tft_does_not_at_delta_0_6` |
| Wie viel gewinnt man durch Abweichen bei kurzem Schatten? | Bei δ = 0,40 (erwartete Dauer 1,7 Wochen) bringt die beste Abweichung 0,95 mehr als Tit-for-Tat gegen Tit-for-Tat; knapp unter der Schwelle (δ = 0,66) nur 0,04. | `test_short_shadow_preset_gain_is_095`, `test_just_below_the_tft_threshold_gain_is_004` |
| Welche Abweichung lohnt bei δ = 0,80 nicht? | Gegen Tit-for-Tat bringen Immer-D 9,00, Abwechseln 13,89 und Einmal-D 14,60 gegen 15,00 für das Beibehalten; die beste Antwort aus allen Strategien ist Tit-for-Tat selbst. | `test_deviation_values_at_delta_0_8` |
| Wer trägt überhaupt? | Immer defektieren bei jedem δ, Immer kooperieren nie. **Tit-for-Two-Tats und Pavlov tragen bei 5/3/1/0 bei keinem δ gegen sich selbst:** Tit-for-Two-Tats lässt sich durch Abwechseln ausbeuten, Pavlov liegt genau auf dem Grenzfall 2R = T + P. Bei T = 4,5 trägt Pavlov ab δ = 0,75. | `test_always_defect_is_an_equilibrium_at_every_delta_and_allc_never`, `test_tf2t_and_pavlov_are_never_a_symmetric_equilibrium_at_the_classic_payoffs`, `test_pavlov_threshold_is_three_quarters_when_t_is_4_5` |
| Wie viele Gleichgewichte unter den sechs bei δ = 0,80? | Vier Paare: Immer-D/Immer-D, Tit-for-Tat/Tit-for-Tat, Tit-for-Tat/Grim, Grim/Grim. Kooperation ist ein Gleichgewicht unter mehreren, keine Vorhersage. | `test_four_equilibrium_pairs_at_delta_0_8` |
| Was verliert Tit-for-Tat gegen Immer-D? | Nur die erste Woche: Wert 4,00 gegen 9,00 für den Defektierer bei δ = 0,80 (je Woche im Mittel 0,80 gegen 1,80). | `test_exploitation_preset_numbers` |

### Korrektur gegenüber dem Plan

Der Plan der Linie nannte für Tit-for-Tat bei 5/3/1/0 die Schwelle δ ≥ 0,5. Das war falsch: 0,5 ist die Schwelle gegen **Immer-Defektieren**. Tit-for-Tat braucht
2/3, weil das Abwechseln stärker ist. Die Vormessung hat das gegen drei unabhängige Rechenwege bestätigt; Grim Trigger trägt tatsächlich bei 1/2.

## Ehrliche Grenzen

- **Die Auszahlungen sind gewählt.** Die Schwellen hängen von T, P und S ab (Regler); „ab 2/3“ gilt nur für 5/3/1/0.
- **Keine Fehler, kein Rauschen:** beide sehen die Aktion des anderen fehlerfrei. Was ein einzelner Fehler bei Tit-for-Tat auslöst, zeigt diese Demo nicht.
- **Nur zwei feste Partner:** keine wechselnden Partner, keine Dritten, keine Bündnisse.
- **δ ist eine Fortsetzungswahrscheinlichkeit.** Ein bekanntes Ende ändert die Rechnung; es ist hier nicht modelliert.
- **Gleichgewicht ist keine Vorhersage:** viele Paare tragen (Immer-Defektieren immer), welches gespielt wird, sagt die Rechnung nicht.
- **Sechs wählbare Strategien**, die Gleichgewichtsprüfung läuft aber gegen alle denkbaren Antworten.

## Verifikation

- **Kern:** je Einheit eine Handrechnung am Spiel 5/3/1/0 (Spielverlauf der sechs Strategien, diskontierte Werte, Bestantworten, Schwellen); jede Reglerkombination ist ein gültiges Dilemma.
- **Orakel** (`tests/test_oracle_tit_for_tat.py`): (1) der Wert jedes Paares aus 8 × 8 Automaten gegen die abgeschnittene Summe über 400 simulierte Runden; (2) die beste Antwort
  gegen Aufzählung aller stationären Politiken **und** gegen Wertiteration, für drei Spiele; (3) die Schwelle von Tit-for-Tat und Grim gegen die geschlossene Formel für alle
  64 Kombinationen von T, P und S der Regler (128 Prüfungen, je Strategie eine).
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py` über dieselben Auswertungsfunktionen wie die App.
- **Presets:** vollständig, Werte in den Grenzen, jedes Preset ein gültiges Dilemma, die Preset-Aussagen stimmen.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, Permalink begrenzt und rastet ein) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tft_algorithm.py` | Kern: Spielverlauf, diskontierter Wert, Bestantwort, Gleichgewicht, Schwelle |
| `tft_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `tft_evaluation.py` | Analyse, Auszahlungsmatrix, Schwellentabelle, Abweichungen, Verdikt |
| `tft_presets.py` | Permalink (Begrenzen und Einrasten), Presets |
| `tft_scenario.py` | Das Spiel und die Strategien als Automaten |
| `tft_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Lernen aus Erfahrung** statt fester Strategien: das ist ein anderes Verfahren (Regret-Minimierung), siehe [noregret-demo](https://sebastianhanisch-noregret-demo.streamlit.app/).
- **Kooperative Spieltheorie mit bindenden Verträgen** (Shapley, Kern): siehe [shapley-demo](https://sebastianhanisch-shapley-demo.streamlit.app/) und [kern-demo](https://sebastianhanisch-kern-demo.streamlit.app/). Hier ist Kooperation selbstdurchsetzend.
- **Mehr als zwei Aktionen** oder mehr als zwei Spieler.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
