# PRODUCT.md

# Paddy's Mealplan — Produktdefinition

Dieses Dokument beschreibt Produktidentität, Produktphilosophie, UX-Prinzipien, Markenstimme und Regeln für neue Features.

## Produkt in einem Satz

**Paddy's Mealplan ist ein intelligenter Wochen-Essensplaner, der Menschen möglichst viele Ernährungsentscheidungen im Alltag abnimmt.**

## Was die App nicht ist

Paddy's Mealplan ist **kein Kalorien-Tracker**.

Ein Tracker schaut zurück:

> Was habe ich gegessen?

Paddy's Mealplan schaut nach vorne:

> Was werde ich essen?

Die App soll nicht möglichst viele Daten protokollieren, sondern Planung vereinfachen.

## Produktversprechen

Jede Funktion sollte mindestens einen dieser Effekte erzeugen:

* Zeit sparen
* Entscheidungen reduzieren
* Ernährung vereinfachen

Die App soll den Nutzer nicht mit zusätzlichen Aufgaben belasten.

## Produktidentität

Paddy's Mealplan:

* **plant**, statt nur zu protokollieren
* **automatisiert**, statt zusätzliche Arbeit zu erzeugen
* **motiviert**, statt zu bewerten
* **vereinfacht**, statt zu überfordern

Der Nutzer soll möglichst wenig darüber nachdenken müssen, was als Nächstes zu tun ist.

## Produktfilter für Features

Vor jeder neuen Funktion prüfen:

1. Spart sie Zeit?
2. Reduziert sie Entscheidungen?
3. Verbessert sie die Nutzererfahrung?
4. Passt sie zum Wochenplan-Konzept und zu `state.goal`?

Wenn keine Frage mit Ja beantwortet wird, wird das Feature nicht umgesetzt.

Technische Machbarkeit allein ist kein Grund für eine Funktion.

„Wäre auch ganz nett" ist ebenfalls kein ausreichender Grund.

## UX-Philosophie

Jeder Screen löst möglichst genau ein Problem.

Grundprinzipien:

* weniger Optionen statt mehr
* kurze Wege
* geringe kognitive Last
* klare nächste Aktion
* keine unnötigen Erklärungen
* möglichst wenige Interaktionen

Wenn zwei technische Umsetzungen für den Nutzer gleichwertig sind, gewinnt diejenige mit weniger notwendigen Interaktionen.

## Markencharakter

Die App soll sich wie ein erfahrener Trainingspartner anfühlen:

* motivierend
* freundlich
* modern
* vertrauenswürdig

Nicht wie:

* Behördensoftware
* Medizinsoftware
* ein kompliziertes Ernährungs-Fachprogramm

**Die Marke hilft dem Nutzer. Sie bewertet ihn niemals.**

Das gilt insbesondere für:

* Fehler
* Gewicht
* Kalorien
* Ziele
* Fortschritt
* fehlgeschlagene Aktionen

## Markenstimme

UI-Texte sind:

* freundlich
* motivierend
* kurz
* modern
* positiv
* leicht verständlich

Vermeiden:

* Behörden-Deutsch
* unnötige Fachsprache
* Roboter-Sprache
* überlange Erklärungen
* wertende Formulierungen
* flapsigen Slang wie „Bro" oder „Digga"

### Buttons

Aktiv formulieren.

Gut:

* `Meal anlegen`
* `Plan speichern`
* `Woche teilen`

Schlecht:

* `Neues Meal wird angelegt`
* `Plan wurde gespeichert`
* `Woche kann geteilt werden`

### Fehlermeldungen

Fehler werden nicht dem Nutzer vorgeworfen.

Nicht:

* „Du hast einen ungültigen Wert eingegeben."

Besser:

* sachlich
* freundlich
* direkt zur Lösung führend

### Erfolgsmeldungen

Erfolg darf motivierend formuliert sein, statt nur technisch zu bestätigen.

## Textmenge

Die UI zeigt so wenig Text wie möglich.

Kein zusätzlicher Satz, wenn die Information bereits aus:

* Frage
* Label
* Option
* Beispiel
* Platzhalter

verständlich ist.

Hilfetext ist nur gerechtfertigt, wenn beim Weglassen eine echte Informationslücke entsteht.

Fachlich oder rechtlich notwendige Hinweise dürfen ausführlicher sein, sollen aber möglichst nicht den normalen UI-Fluss dominieren.

## Premium

Premium soll nicht einfach bestehende Funktionen künstlich sperren.

Premium muss einen zusätzlichen Nutzen erzeugen:

* Automatisierung
* Optimierung
* Zeitersparnis
* intelligente Unterstützung

Beispiele:

* automatische Wochenplanung
* adaptive Kalorienanpassung
* KI-Meal-Empfehlungen
* Budget-Optimierung
* intelligente Einkaufsunterstützung

Premium soll **mehr leisten**, nicht künstlich weniger freischalten.

## Langfristige Vision

Entwicklung:

**Heute:** Meal Planner
**Morgen:** Nutrition Assistant
**Später:** Intelligent Nutrition Coach

Langfristig soll die App möglichst viele Alltagsentscheidungen automatisch übernehmen:

* Wochenplanung
* Einkaufslisten
* Kalorienanpassung
* Budgetplanung
* personalisierte Empfehlungen

Neue Produktentscheidungen sollten diese Entwicklung unterstützen.

## Meal-Datenbank

Meals sollen:

* hochwertig
* fitness-fokussiert
* sauber getaggt
* strukturiert
* wiederverwendbar

sein.

Langfristig relevante Metadaten:

* Kategorie
* Ziel: Abnehmen / Halten / Aufbauen
* Zubereitungszeit
* Meal-Prep-Eignung
* Preis
* Schwierigkeit
* Tags
* Zutaten
* Makros
* Bild

Die Datenstruktur soll spätere intelligente Filterung und Automatisierung ermöglichen.

## Bewusste Produktentscheidungen: Wochenplan

### Der angezeigte Tag folgt einer Anker-Regel

„Aktuelle Woche" zeigt immer **heute**, „Nächste Woche" immer **Montag** — beim Betreten des
Wochenplans und bei jedem Wochenwechsel.

Verworfen wurden bewusst:

* **Tagesindex beibehalten** (Do bleibt Do): elegant, aber die eigentliche Frage ist „was esse
  ich heute" bzw. „ich plane die nächste Woche". Der Vergleich Do gegen Do ist ein Nischenfall.
* **Zuletzt betrachteten Tag je Woche merken**: unsichtbarer Zustand, dasselbe Tippen führt je
  nach Vorgeschichte woandershin, und über eine Tagesgrenze hinweg wird der Wert falsch.

Eine Regel, keine Ausnahme, in einem Satz erklärbar.

### Nichts steht zweimal da

Auf dem Handy nennt die Tagesleiste den Wochentag bereits. Die Kopfzeile der Tageskarte
(ausgeschriebener Wochentag, „Heute"-Chip) wurde deshalb dort entfernt, statt dieselbe Aussage
zwei Zentimeter tiefer zu wiederholen.

Was dabei echte Information war, ist umgezogen statt verschwunden:

* **Trainingstag** → Farbe und Hantel-Icon am aktiven Reiter.
* **Über dem Kalorienziel** → Klartext in der Fußbilanz („120 kcal drüber").

Die Trainingsstufe (Locker/Normal/Intensiv) ist auf dem Handy bewusst nur noch „ja/nein". Sie
steuert weiterhin die Rechnung und bleibt in der Sprachausgabe erhalten.

### Ein Zustand wird nie allein über Farbe angezeigt

Gilt für Trainingstag und Zielüberschreitung gleichermaßen: zur Farbe kommt immer eine Form
(Icon, Punkt) oder ein Wort. Rot und Blau sind für Farbenblinde praktisch identisch.

Deshalb war der Wegfall des Überschreitungs-Zeichens kein reines Streichen — die Textzeile in
der Fußbilanz, die vorher wegen des Zeichens unterdrückt war, wurde im selben Schritt wieder
eingeschaltet.

## Was bewusst nicht passieren soll

Keine Features hinzufügen, nur weil sie:

* technisch interessant sind
* schnell gebaut werden können
* andere Apps ebenfalls haben
* „noch ganz nett wären"
* die Oberfläche mit Optionen anreichern

Die App gewinnt nicht durch Funktionsmenge, sondern durch weniger Aufwand für den Nutzer.
