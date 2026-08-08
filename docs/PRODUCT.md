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

## Offline-Nutzbarkeit

Der Wochenplan, die Meals und die Einkaufsliste müssen auch ohne Internetverbindung nutzbar sein
— Supermarkt, Keller, Küche mit schlechtem WLAN sind der Alltag, für den geplant wird. Das ist
seit dem Firestore-Offline-Cache (`docs/ARCHITECTURES.md`, Abschnitt „Firestore-Offline-Cache")
eine Produktzusage, kein bloßer Härtungsschritt. Kein eigener Offline-Hinweis in der UI: der
Sync-Status bleibt der bestehende farbige Punkt am Avatar.

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
* `Meal teilen`

Schlecht:

* `Neues Meal wird angelegt`
* `Plan wurde gespeichert`
* `Meal kann geteilt werden`

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

### Snacks sind ein eigener Slot, kein Anhängsel

Ein Riegel am Nachmittag landete vorher behelfsmäßig unter „Abendessen". Die Tagesbilanz stimmte
dann zwar, die Planung war aber gelogen — und genau die Planung ist das Produkt.

Snack und Dessert lassen sich seitdem **nur noch** in „Snacks" einplanen. Das ist bewusst eine
Einschränkung: Sie hält die Auswahlliste jedes Slots kurz, und kurze Listen sind der eigentliche
Zweck der Kategorien. Wer doch einen Snack zum Frühstück will, kommt über „Alle anzeigen" dorthin
— der Weg ist einen Tipp länger, nicht versperrt.

Bereits verplante Snacks in anderen Slots bleiben stehen. Eine nachträgliche Umsortierung fremder
Pläne wäre eine Änderung an Daten, die der Nutzer selbst so angelegt hat.

### Auf dem Handy steht der Plan still

Der Wochenplan ist mobil eine Fläche fester Höhe: Wochenumschalter und Tagesleiste oben, die
Tagesbilanz unten, und nur die Mahlzeiten dazwischen scrollen.

Das ist eine Produktentscheidung, keine Layoutfrage: Bei einem vollen Tag liegt etwas unter der
Falz. Dafür beantwortet der Bildschirm ohne Scrollen die beiden Fragen, für die man den Plan
öffnet — *welcher Tag* und *wie weit bin ich mit meinem Ziel*. Vorher wanderte die Bilanz mit dem
Inhalt nach unten und war bei vollen Tagen genau dann unsichtbar, wenn sie am meisten zählt.

Zwei Dinge mussten dafür weichen: die Überschrift „Dein Wochenplan" (die Reiterleiste sagt bereits
„Plan") und der breite Einkaufslisten-Knopf, der mobil ein Icon im Kopf wurde. Ein zweiter fester
Balken über der Reiterleiste hätte auf einem 667 px hohen Gerät die halbe Meal-Fläche gekostet.

## Bewusste Produktentscheidungen: Gemeinsam planen

### Erst einladen, dann entscheiden

„Person einladen" fragt vorab nichts mehr ab. Früher stand vor dem Einladungslink ein
Rollen-Umschalter („Was darf die eingeladene Person?") — eine Option, bevor überhaupt ein Nutzen
sichtbar war. Jetzt gilt ein sinnvoller Default (Rolle „Mitplanen", Einkauf für alle rechnen an,
Hinweis bei Änderungen an), und wer ihn ändern will, tut das später direkt am Mitglied bzw. in
den Gruppen-Einstellungen — wenn der Bedarf tatsächlich da ist, nicht vorher spekulativ.

Passt zum UX-Grundsatz „wenige statt viele Optionen": eine Entscheidung, die man nicht treffen
muss, ist besser als eine gut vorbereitete.

### Die Gruppe startet erst mit dem Beitritt

Ein Klick auf „Person einladen" legt technisch schon eine Gruppe an, aber der Owner bleibt bis
zum tatsächlichen Beitritt in seinen eigenen Daten (Wartezustand, siehe `ARCHITECTURES.md`,
Abschnitt „Gruppenmodus"). Wer nur mal ausprobiert, ob das Feature etwas für ihn ist, landet so
nicht ungefragt dauerhaft in einer Einpersonen-Gruppe. Erst wenn wirklich geplant wird, ist es
auch wirklich „gemeinsam".

### Gerichte müssen nicht für alle gleich sein

Der Wochenplan war bisher zwangsläufig für die ganze Gruppe identisch, obwohl jede Person schon
ein eigenes Kalorien-/Makroziel hat. In der Praxis isst man nicht jeden Tag exakt dasselbe — will
aber trotzdem eine einzige, gemeinsame Einkaufsliste. Einzelne Gerichte lassen sich deshalb per
Personen-Symbol optional nur einer Teilmenge der Gruppe zuweisen, die Einkaufsliste skaliert pro
Gericht nach tatsächlicher Personenzahl. Der Regelfall ("für alle") bleibt dabei ohne jeden
zusätzlichen Klick — Zuweisung ist eine Ausnahme, keine Pflichtentscheidung beim Einplanen.
Das Symbol war ursprünglich ein Stift, der wie "bearbeiten" statt "wer isst mit" liest — inzwischen
ein Personen-Icon, das die tatsächliche Aktion zeigt.

## Bewusste Produktentscheidung: Barcode-Schnellzugriff

Fertigprodukte (Tiefkühlpizza, Riegel, Joghurt) verdienen keine Rezept-Pflege — trotzdem musste
bisher jedes über das volle Meal-Formular angelegt werden. Der Barcode-Scan (bereits als
Zutaten-Hilfsmittel vorhanden) ist deshalb ein zweiter, schnellerer Weg geworden: direkt aus dem
Wochenplan heraus scannen, Open Food Facts liefert Name und Nährwerte, das Produkt landet ohne
Formular im gewählten Tag/Slot.

**Verworfene Alternative: eigenes "Produkt"-Konzept.** Ein paralleler Datentyp neben Meals hätte
entweder bei jedem Sync verworfen werden müssen (`normalizePlan()` kennt nur `state.recipes`) oder
an allen ca. 6 Stellen nachgezogen werden müssen, die heute `getRecipe()` aufrufen (Kalorien,
Einkaufsliste, PDF, Ziel-Ringe). Ein Scan erzeugt deshalb einen ganz normalen Recipe-Eintrag —
nur mit `barcode` (Wiedererkennung, verhindert Duplikate beim erneuten Scan desselben Produkts)
und `quick: true` (blendet ihn aus der Meals-Bibliothek aus, der Nutzer wollte diesen Eintrag dort
nicht sehen). Sync, Einkaufsliste, Ziel-Ringe, Sharing bleiben dadurch unverändert funktionsfähig.

**Entscheidung: kein Foto von Open Food Facts.** OFF-Bilder direkt zu verlinken oder zu
übernehmen wäre ein Lizenzrisiko (siehe Abschnitt „Bilder und Lizenzen" in `CLAUDE.md`) — die
bestehende Fallback-Kette in `photoFor()` (Stichwort → Kategorie → neutral) greift für
Barcode-Meals automatisch, ganz ohne Codeänderung.

**Unsicherer Fall geht nicht in einen Fehlwert.** Liefert Open Food Facts keine auswertbare
**Portionsgröße** (eine bloße Packungsgröße wie „500 g" zählt nicht — sonst stünde eine ganze
Tüte Nudeln als ein Meal im Plan) oder fehlen Name/Nährwerte, wird nicht geraten — der Scan
öffnet stattdessen das normale Formular vorausgefüllt, samt der gefundenen Nährwerte als
Zutaten-Zeile; einzutragen bleibt nur die Menge. Kalorienkorrektheit ist das Kernversprechen der
App; ein zusätzlicher Bestätigungsklick in diesem Randfall wiegt das auf.

**Ein gescanntes Produkt ist flüchtig, kein Bestand.** Es gehört zu dem einen Tag, an dem man den
Riegel isst — nicht in die Bibliothek und auch nicht in die Auswahlliste beim Planen. Aus dem
Meals-Reiter war es von Anfang an ausgeblendet; die Auswahlliste des Wochenplans las aber lange
an dieser Regel vorbei und wuchs mit jedem Scan. Beide gehen jetzt über dieselbe Menge.

Damit sich die Produkte nicht still in den Daten stapeln, werden sie beim Start entfernt, sobald
sie in keiner Woche mehr verplant **und** älter als die Aufbewahrung der Wochen sind. Die
Altersgrenze ist kein Beiwerk: Ohne sie könnte ein Gerät ein Produkt löschen, das der Partner
gerade eingeplant hat und das hier noch nicht angekommen ist. Speicherplatz zu sparen darf keine
fremde Planung beschädigen.

## Bewusste Produktentscheidung: Meal-Ansicht und Editor sind eins

Ein Meal hatte früher drei getrennte Oberflächen: die Karte in der Liste, ein Ansehen-Modal und
ein Bearbeiten-Modal. Wer etwas ändern wollte, tippte mindestens zweimal — Karte → Ansehen →
Bearbeiten — und landete in einem langen Formular, das mit der eben gesehenen Ansicht optisch
nichts zu tun hatte. Dieselben Daten, drei Darstellungen.

Das widersprach dem eigenen Grundsatz aus der UX-Philosophie: „Wenn zwei technische Umsetzungen
für den Nutzer gleichwertig sind, gewinnt diejenige mit weniger notwendigen Interaktionen."

**Umsetzung.** Die Karte ist eine ruhige Vorschau (Foto, Name, Kalorien + Makros als farbige
Kurzform). Ein Tipp lässt sie zu einer großen Ansicht wachsen — dieselbe Fläche zeigt Ansehen und
Bearbeiten, es gibt keine dritte, separate Formularseite mehr wie früher.

**Autosave statt Speichern-Knopf.** Ein Speichern-Knopf zwingt zu der Frage „Habe ich schon
gespeichert?" — bei einer einzigen Oberfläche ohne getrennten Bearbeiten-Modus ist das keine
sinnvolle Frage mehr. Änderungen greifen beim Verlassen eines Felds, ein neues Meal existiert
zunächst nur als Entwurf und zieht erst mit dem ersten eingetragenen Namen in die
Meal-Bibliothek ein — ein Fehltipp beim Öffnen hinterlässt keine „Unbenannt"-Leiche, die noch
dazu in die Cloud synchronisiert würde.

**Zutaten: Ruhezustand statt Dauerformular.** Acht Zutaten als acht offene Formularkarten
untereinander (Textfeld, Zahlenfeld, Einheiten-Auswahl, aufklappbare Nährwerte) sind zum reinen
Nachschauen zu laut. Die Liste zeigt deshalb im Ruhezustand nur Menge, Name, Kalorien und Makros
je Zutat; ein Tipp auf die Zeile öffnet genau diese eine zum Bearbeiten. Wer nur planen will,
sieht eine ruhige Liste; wer ändern will, ist einen Tipp entfernt.

**Makros: dieselbe Kachelform wie im Ansehen-Modus.** Ein kurzlebiger Zwischenstand hatte die vier
Eingabefelder für Kalorien/KH/P/F hinter einer antippbaren Kurzzeile versteckt (Vorbild Zutaten-
liste). In der Abnahme zeigte sich: Makros sind kein Nebendetail wie eine einzelne Zutat, sondern
die Zahl, für die die App überhaupt gebaut ist — sie sollen beim Öffnen sofort sichtbar sein, ohne
Extra-Tipp. Die vier Felder stehen deshalb dauerhaft in derselben Kachelform (`.nutfacts`) wie im
Ansehen-Modus; der einzige Unterschied ist, dass man im Bearbeiten-Modus hineinschreiben kann.
Wiedererkennung entsteht so nicht durch An-/Zuklappen, sondern dadurch, dass Ansehen und
Bearbeiten optisch gleich aussehen.

**Jedes Meal öffnet zuerst zum Ansehen.** Autosave ohne Speichern-Knopf hat einen Preis: Wer ein
Meal nur nachschlagen will („was esse ich Dienstag?", „was war da nochmal drin?"), ist sonst einen
Fingertipp von einer ungewollten Änderung entfernt — in einer Gruppe landet ein Vertipper sofort
auf dem anderen Gerät, und für einzelne Felder gibt es kein Rückgängig. Ein Tipp auf ein Meal —
im Wochenplan wie im Meals-Reiter, einheitlich — öffnet die Ansicht deshalb lesend, mit einem
„Bearbeiten"-Knopf im Kopf, einen Tipp entfernt. Nur ein neues Meal und der Barcode-Schnellzugriff
starten direkt im Bearbeiten-Modus, weil dort noch nichts anzusehen ist bzw. sofort ergänzt werden
soll.

## Was bewusst nicht passieren soll

Keine Features hinzufügen, nur weil sie:

* technisch interessant sind
* schnell gebaut werden können
* andere Apps ebenfalls haben
* „noch ganz nett wären"
* die Oberfläche mit Optionen anreichern

Die App gewinnt nicht durch Funktionsmenge, sondern durch weniger Aufwand für den Nutzer.
