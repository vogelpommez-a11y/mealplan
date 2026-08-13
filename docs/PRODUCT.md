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

### Umgesetzt seit 13.08.2026: Tags, Meal-Prep, Aufwand

Drei dieser Metadaten stehen im Datenmodell: `tags[]`, `mealPrep`, `difficulty`
(siehe `docs/ARCHITECTURES.md`). Bewusst **feste Tag-Schlüssel statt Freitext** — nur damit
können Filter, kuratierte Bibliothek und der spätere Auto-Planer rechnen. Freitext-Tags
schreibt jeder anders, und ein Filter, der „Low Carb" nicht findet, ist schlimmer als keiner.

`difficulty` heißt in der Oberfläche **Aufwand** (Einfach / Mittel / Aufwendig): In der Küche
entscheidet die Zielgruppe nach Aufwand, nicht nach Können. Die Marke bewertet den Nutzer
nicht (siehe Markenstimme) — „Schwierigkeit" täte genau das.

Noch offen sind Ziel-Eignung und Preis. Beide erst, wenn ein Feature sie tatsächlich braucht.

### Der Meal-Filter zeigt nur, was es zu filtern gibt

Die Chip-Reihe im Meals-Reiter (seit 13.08.2026) blendet jedes Merkmal aus, das im eigenen
Bestand nicht vorkommt, und verschwindet unter sechs Meals ganz. Ein Filter mit acht Knöpfen,
von denen sieben ins Leere führen, ist kein Werkzeug, sondern Ballast — und genau der
Erstkontakt, den ein neuer Nutzer nicht braucht.

Mehrfachauswahl ist **UND**-verknüpft: Wer „Vegan" und „Meal-Prep" antippt, will beides.

Die Reihe **bricht um**, sie scrollt nicht waagerecht. Ein Scroller versteckt Filter am rechten
Rand und ist über einer Liste zugleich eine Gestenfalle (`CLAUDE.md` §11). Im schlimmsten Fall
(alle sieben Merkmale im Bestand) sind es auf 360 px drei Zeilen — im Alltag meist eine.

Bewusst **kein** Filter nach Zeit: Die Zubereitungszeit (`time`) steht nur in den mitgelieferten
Beispiel-Meals, im Editor gibt es kein Feld dafür. Ein Filter auf ein Feld, das niemand pflegt,
findet zuverlässig nichts. Kommt das Feld, kommt der Filter.

## Bewusste Produktentscheidung: Vier Reiter, vier Fragen

Seit 13.08.2026 gibt es einen vierten Reiter **Fortschritt**. Danach beantwortet jeder Reiter
genau eine Frage:

| Reiter | Frage |
|---|---|
| Home | Wie steht meine Woche? |
| Wochenplan | Was esse ich wann? |
| Meals | Was koche ich? |
| Fortschritt | Wie lief es bisher? |

Vorher trug Home vier Themen gleichzeitig (Hero, Wochenziele, Rückblick, Gewicht) und verstieß
damit gegen den eigenen UX-Grundsatz „jeder Screen löst möglichst genau ein Problem". Rückblick
und Gewichtskarte sind unverändert umgezogen — der Ort hat sich geändert, nicht die Funktion.

Die Navigationsmechanik bleibt, wie sie war: gleitende Pille, gerichteter Inhaltswechsel,
untere Kapsel auf dem Handy. Der vierte Reiter ist eine Spalte mehr, kein neues Prinzip.

**Gewicht eintragen kostet jetzt zwei Taps statt vier.** Das Plus auf der Gewichtskarte öffnet
direkt das Eingabefeld; Jahresziel und Einwilligungs-Widerruf stehen im Überlaufmenü daneben.
Für „Fitness & Meal-Prep" ist Wiegen wöchentliche Routine — sie gehört nicht hinter ein Menü,
in dem sie sich mit zwei seltenen Aktionen die Prominenz teilt.

## Bewusste Produktentscheidungen für Fitness & Meal-Prep (13.08.2026)

Vier Eingriffe, die alle aus derselben Frage kommen: Was tut die Zielgruppe **regelmäßig**, und
wie viele Taps kostet es sie?

* **Wiegen ist wöchentlich, nicht monatlich.** Ein Trend, der erst nach Monaten sichtbar wird,
  hilft niemandem, der sein Defizit steuert. Taggenau bleibt trotzdem falsch: Wasser und
  Mahlzeiten schwanken stärker als der Fortschritt einer Woche. Deshalb zusätzlich der
  gleitende Durchschnitt über vier Messungen — er ist die Linie, die man liest, die Rohwerte
  bleiben daneben sichtbar. Eine App, die nur den geglätteten Wert zeigt, versteckt, woraus er
  entsteht.
* **Das Ziel lässt sich direkt anpassen.** „100 kcal weniger" führte vorher durch den kompletten
  Rechner samt Alter, Größe und Trainingstagen. Der Rechner bleibt daneben — er ist der Weg,
  wenn sich die *Grundlagen* ändern, nicht die Feinjustierung.
* **Portionen sind planbar** (½, 1, 1½, 2 am Slot). Meal-Prep rechnet in Portionen, nicht in
  Gerichten. Der Faktor wirkt auf Tagesbilanz, Einkaufsliste und Ausdruck — ein Faktor, der nur
  angezeigt wird, wäre eine Lüge.
* **„Woche leeren" steht nicht mehr neben der Einkaufsliste.** Eine destruktive Aktion mit
  derselben Prominenz wie das meistgenutzte Werkzeug ist ein Fehlerangebot; die Rückfrage
  allein ist keine Entschuldigung dafür.

Bewusst **keine** freie Portionszahl: vier Stufen decken den Alltag ab, ein Zahlenfeld wäre
mehr Eingabe für weniger Klarheit.

## Bewusste Produktentscheidung: Der Rückblick misst gegen das Ziel

Der Rückblick zeigt **geplante** Kalorien, nicht gegessene — das ist die Planer-Identität und
steht seit 13.08.2026 auch als Klartextzeile in der Sektion. Vorher stand es nirgends, und
genau deshalb las man die Grafik als Ernährungsverlauf.

Zwei Regeln, die daraus folgen:

* **Bezugsgröße ist immer das Ziel**, nie die Streuung der Nachbarwochen. Eine Grafik, die
  Zielerreichung suggeriert, muss auch Zielerreichung zeigen.
* **Ein Streak muss verlierbar sein.** Er zählt eine Woche erst ab 5 von 7 geplanten Tagen.
  Vorher genügte eine einzige Mahlzeit; eine Serie ohne Anspruch motiviert niemanden und ist
  damit kein Produktnutzen, sondern Dekoration.

Was der Rückblick weiterhin **nicht** tut: bewerten. Wochen außerhalb des Ziels sind gedämpft
gezeichnet, nicht rot.

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

### Der Plan bleibt in der Reihenfolge stehen, in der er gebaut wurde

Die Gerichte eines Slots waren nach Zuweisung gruppiert: gemeinsame zuerst, dann die eigenen,
dann die der anderen. Das ordnete die Liste sauber — kostete aber bei jeder Zuweisung einen
Sprung, weil das Gericht seine Gruppe wechselt und sofort woanders steht. Bei zwei Personen
passiert das direkt unter dem Finger.

Die Gruppierung ist weg. Eine Liste, deren Reihenfolge man durch Antippen ändert, sortiert sich
unter dem Finger um — das ist verwirrend, egal wie ordentlich das Ergebnis ist. Der Tag steht
jetzt so da, wie man ihn gebaut hat.

Was dadurch entfällt: Fremde Gerichte stehen nicht mehr gebündelt am Ende. Die Zusammenfassung
ab dem dritten („+2 weitere") gibt es weiterhin, sie zählt nur in Plan-Reihenfolge.

### Die Mahlzeitenfarbe kehrt im Symbol zurück

Mit der Listen-Optik verschwand die Mahlzeitenfarbe aus Überschrift und Streifen — richtig, denn
eine eingefärbte Überschrift sagt nichts, was das Wort daneben nicht schon sagt. Ohne sie gingen
die Abschnitte im gemeinsamen Fenster aber unter.

Sie kommt deshalb an der kleinsten sinnvollen Stelle zurück: **im Symbol**. Amber fürs Frühstück,
Teal fürs Mittagessen, Violett fürs Abendessen. Das ist Wiedererkennung, keine Information — das
Wort steht ausgeschrieben daneben, das Symbol ist für Screenreader unsichtbar.

Dazu bekommt jeder Abschnitt mehr Luft über sich. Raum statt Schriftgröße: Die Abschnittsform gilt
app-weit, und die Einheitlichkeit mit „Zutaten" in der Meal-Ansicht war ausdrücklich gewünscht.

**Nachtrag — der Streifen ist auch zurück.** Das Symbol allein hat die Farbcodierung zwar gerettet,
aber sie blieb schwächer als am Rechner: Dort trägt jeder Slot zusätzlich einen Farbstreifen links.
Wer zwischen den Geräten wechselt, sah dieselbe Woche zweimal unterschiedlich stark gegliedert.

Der Streifen sitzt mobil im Innenabstand des gemeinsamen Fensters, nicht im Textfluss — die Zeilen
bleiben bündig und die Trennlinien laufen weiter durch. Streifen und Symbol stören sich nicht: das
eine färbt den Rand, das andere die Zeile. Die Kachelform kommt damit ausdrücklich **nicht**
zurück; es kehrt nur die Farbe zurück, nicht der Rahmen.

**Farbe nur, wo das Theme sie kennt.** Snacks bleiben grau — dieselbe Entscheidung wie beim
Farbstreifen. Im Meals-Reiter tragen Frühstück und Hauptgericht dieselben zwei Farben wie im Plan,
Snack, Dessert, Beilage, Getränk und Favoriten bleiben neutral. Vier neue Töne zu erfinden, damit
jede Kategorie eine hat, würde mit Makro-, Mitglieds- und Trainingsfarben kollidieren.

### Ein Fenster für die Mahlzeiten, eines für den Stand

Auf dem Handy stehen die vier Mahlzeiten in einer gemeinsamen Fläche, die Tagesbilanz in einer
zweiten darunter. Zwei ruhige Flächen statt vieler Kästen — die Trennlinien gliedern innerhalb
des Fensters weiter.

Bewusst **ein** Fenster und nicht vier: Ein eigener Rahmen je Mahlzeit wäre die Kachel-Optik
zurück, die vorher abgeschafft wurde, und zusammen mit der Bilanz lägen fünf Kästen auf einem
Bildschirm.

### Die Einkaufsliste spricht dieselbe Sprache — auf beiden Geräten

Die Einkaufsliste war lange die letzte Ansicht, die ihre Positionen als Kachelstapel zeigte:
jede Zutat ein eigener Rahmen, dazwischen Luft. Wochenplan und Zutatenliste waren da längst
Listen mit dünnen Trennlinien. Auf dem Handy sprach die App damit zwei Sprachen.

Sie ist jetzt ebenfalls eine Liste in einem Fenster, mit derselben Gliederung wie der Wochenplan:
Abschnittsüberschrift, darunter Zeilen mit Trennlinien. **Anders als beim Wochenplan gilt das auf
beiden Geräten** — die Liste steht in einem Modal und ist auf jedem Bildschirm einspaltig
untereinander. Das Argument für Kacheln am Rechner (sieben Tage nebeneinander brauchen
Abgrenzung) hat hier nie gegolten; die Kachelform war nur nie angefasst worden.

Abgehakte Positionen tragen sich ohne eingefärbte Fläche: durchgestrichener grauer Text, gefülltes
Häkchen, gedämpfte Menge. Eine Tönung über die volle Zeilenbreite läse sich ohne Rahmen als
Auswahlbalken statt als „erledigt".

Die Personenzeile darüber behält ihre Fläche, teilt sich aber Rundung und Ton mit dem Listenfenster
— oben die Einstellung, unten das Ergebnis, als Paar lesbar. Dasselbe Mittel wie bei Plan und
Tagesbilanz im Wochenplan.

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

**Nachtrag — der Einkaufsknopf steht jetzt auf beiden Geräten oben.** Er war eine Zeit lang zwei
Knöpfe: am Rechner der breite Gradient-Knopf unter dem Plan, auf dem Handy das Symbol im Kopf.
Dieselbe Aktion an zwei Orten in zwei Formen — wer zwischen Rechner und Handy wechselt, sucht sie
jedes Mal woanders. Jetzt sitzt sie immer in der Werkzeugleiste neben dem Wochenumschalter; am
Rechner mit dem Wort „Einkaufsliste", ab 680 px nur noch als Symbol. Das ist dasselbe Muster, das
der Wochenumschalter daneben schon fährt (` Woche` entfällt auf schmalen Geräten).

Der Verzicht auf den großen Gradient-Knopf ist bewusst: Die Einkaufsliste ist wichtig, aber sie ist
kein Aufruf zum Handeln, den man dem Nutzer anbieten muss — sie ist ein Werkzeug, das man sucht,
wenn man einkaufen geht. Werkzeuge gehören in die Werkzeugleiste.

**Zweiter Nachtrag — die feste Höhe ist wieder weg.** Sie kostete das Wischen zwischen den Tagen:
Ein eigener Scroller in der Tageskarte fängt die Geste ab, und auf Touch gibt er sie nicht mehr
her. Am Gerät ließ sich der Plan gar nicht mehr durchblättern — ein Funktionsausfall wiegt mehr
als eine ruhigere Fläche.

Jetzt scrollt die Seite wieder. Der eigentliche Gewinn bleibt trotzdem erhalten: Der Kalorienstand
steht in einer Leiste unter dem Streifen, die beim Scrollen über der Reiterleiste kleben bleibt.
Man sieht ihn also weiterhin ohne Scrollen — nur trägt ihn nicht mehr eine feste Fläche, sondern
ein klebendes Element. Die Lehre daraus steht in `docs/TROUBLESHOOTING.md`, Punkt 58.

**Nachtrag aus der Geräteabnahme:** Die feste Höhe war richtig, aber der Fuß der Karte zu schwer.
Die Tagesbilanz belegte 125 px, davon 41 px allein für eine Knopfzeile mit dem Wort „Makros". Der
Aufklapper ist deshalb ein Chevron in der Kalorienzeile geworden. Zusammen mit der Fußzeile, die
ins Menü gewandert ist, sieht man jetzt alle vier Mahlzeiten ohne zu scrollen — vorher endete der
Blick beim Abendessen.

Die Makros klappen dabei **nach oben** auf. Das ist keine Geschmacksfrage: Die Bilanz ist am
Kartenfuß verankert, wüchse sie nach unten, schöbe sie ihren eigenen Auslöser weg.

### Rechtliches steht im Menü, nicht in der Fußzeile

Auf dem Handy führen Impressum und Datenschutz über das Ausklappmenü oben rechts — zwei Tipps,
Profil-Knopf und dann der Eintrag. Für mobile Seiten ist das der übliche Weg: Eine Fußzeile muss
man erst ans Seitenende scrollen, und genau das gilt als riskant.

Zwischenzeitlich stand die Fußzeile fest über der Reiterleiste. Das löste das Scroll-Problem,
kostete aber dauerhaft Platz und störte im Bild. Der Menüpunkt löst dasselbe besser.

**Abgemeldet und in den ersten Schritten bleibt die Fußzeile.** Das Menü gibt es erst nach der
Anmeldung — wäre sie überall weg, läge das Impressum hinter dem Auth-Gate. Beide Fälle schließen
sich aus, deshalb steht nichts doppelt da.

Die Schrift im Menü ist mit 13,5 px größer als die 12,5 px der Fußzeile, und die Einträge sind
44 px hoch. Ein Pflichtweg, den man nicht bequem trifft, wäre keiner.


**Abgemeldet bleibt sie vollständig.** Das Menü gibt es erst nach der Anmeldung — wäre die
Fußzeile dort reduziert, läge der Copyright-Hinweis nirgends. Während der ersten Schritte
ebenfalls: Dort ist die Reiterleiste ausgeblendet, und ein Weg weniger wäre genau der falsche
Moment.

Platz zu gewinnen rechtfertigt keinen versperrten Pflichtweg — aber 11 px lassen sich mitnehmen,
ohne einen zu versperren.

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

## Bewusste Produktentscheidung: Schnelleintrag für Stück-Artikel

Ein Apfel ist kein Meal. Wer eine Banane zum Frühstück einplanen will, hat vorher ein Meal
angelegt — Name, Kategorie, Nährwerte — für 105 kcal. Das ist genau die Entscheidungslast, die die
App abnehmen soll. Der Schnelleintrag ist deshalb der dritte Weg in einen Slot, neben Meal wählen
und Barcode scannen: tippen, antippen, drin.

**Er sitzt im bestehenden Suchfeld**, nicht in einer eigenen Ansicht. Wer „ban" eintippt, sieht
seine Meals und darunter den Abschnitt „Schnell". Ein zweiter Knopf am Slot hätte den Nutzer
gezwungen, vorher zu wissen, in welcher der beiden Listen sein Ziel steckt.

**Nur echte Stück-Artikel.** Apfel, Banane, Ei, Brötchen, Mandarine — Dinge, bei denen „ein Stück"
eine natürliche Portion ist. Keine Scheiben, keine Handvoll: „1 Stück Brot" ist schlicht falsch,
und jedes eigene Mengenwort wäre eine neue Sonderregel in einer Liste, die vom Ablesen lebt.

**Ein Tipp = ein Stück.** Zwei Bananen sind zwei Antipper und zwei Karten im Slot. Ein
Mengen-Regler hätte jede Zeile um zwei Knöpfe und einen Bestätigungsschritt verlängert — für den
Regelfall (ein Stück) wäre das teurer geworden, und die Einkaufsliste fasst „2× Banane" von selbst
zusammen.

**Verworfen: ein eigener Eintragstyp im Slot.** Dieselbe Begründung wie beim Barcode-Schnellzugriff
— Tagesbilanz, Einkaufsliste, PDF, Gruppen-Sync und Undo kennen nur Rezept-IDs. Der Schnelleintrag
legt darum ein stilles Meal an, das aus der Bibliothek ausgeblendet bleibt und automatisch
verschwindet, sobald es nirgends mehr eingeplant ist.

**Ohne ein einziges Meal ist der Slot jetzt trotzdem benutzbar.** Der frühere Sonderdialog „Noch
keine Meals" war eine Sackgasse mit einem Ausweg; der Hinweis samt Weg zu den Meals steht jetzt im
Picker selbst, über dem Schnellbereich.

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
