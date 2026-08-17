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

### Die Pro-Grenze (festgelegt 10.08.2026, Grundlage seit 13.08.2026 im Code)

**Gratis läuft vollständig lokal — und dort uneingeschränkt.** Wochenplan, Einkaufsliste,
Barcode, Ziele, Gewicht, Vorkochen, Meal-Teilen per Link: alles ohne Konto, ohne Sperre,
ohne Zähler.

**Pro bringt das, was tatsächlich Server kostet oder echte Automatik ist:** gemeinsam planen,
den Auto-Wochenplaner, die erweiterte Bibliothek, adaptive Kalorienanpassung. (Cloud-Sync stand
hier ursprünglich mit in der Liste — siehe die Korrektur weiter unten.)

Die Begründung nach außen ist damit ehrlich: laufende Kosten und Zusatznutzen — nichts, was
vorher ging, wird weggenommen.

Der **Gruppenmodus** wird Pro-Funktion. Er bleibt technisch unverändert, wird aber nicht als
Haupt-Verkaufsargument beworben: vom Kostenfaktor zum Kaufgrund, ohne dass eine Zeile seines
Codes wegfällt.

**Der Einstieg führt seit 13.08.2026 (D1b) in den lokalen Modus.** Wer die App zum ersten Mal
öffnet, sieht „Ohne Konto loslegen" als Hauptweg und „Mit Konto anmelden" daneben. Vorher stand
dort „Konto erstellen" — eine Anmeldemaske vor einer App, die ohne Konto vollständig
funktioniert. Ohne diesen Schritt trägt die Pro-Grenze nicht: Ein Konto kann erst dann ein
Aufstieg sein, wenn es keine Eintrittskarte mehr ist.

Zwei Folgen, die dazugehören:

* **Wer schon lokal arbeitet, sieht nie wieder eine Anmeldemaske.** Bisher landete auch jemand
  mit fertigem lokalem Profil vor der Cloud-Anmeldung, sobald Firebase erreichbar war.
* **Die E-Mail-Adresse im lokalen Profil ist optional.** Sie verlässt das Gerät nie und wird für
  nichts gebraucht — sie zwingend abzufragen war das Gegenteil von Datenminimierung und eine
  Hürde vor dem ersten Meal.

Technisch ist der Status **serverseitig** verankert (`entitlements/{uid}`, für den Client nur
lesbar) — eine UI-Sperre wäre keine Grenze, sondern eine Anzeige. Siehe
`docs/ARCHITECTURES.md`.

### Cloud-Sync ist keine Pro-Funktion (korrigiert am 15.08.2026)

**Die Liste weiter oben nennt Cloud-Sync als Pro-Funktion. Das gilt nicht mehr.** D2b hatte den
Sync einen Tag lang hinter Pro gelegt; die Entscheidung wurde am selben Tag zurückgenommen.

Der Grund ist eine Erwartung, gegen die kein Preismodell ankommt: **Wer sich anmeldet, will seine
Meals auf dem zweiten Gerät sehen.** Das ist die Grunderwartung an ein Konto, kein Zusatznutzen —
Yazio und Lifesum synchronisieren gratis. Eine App, die dafür Geld verlangt, wirkt nicht premium,
sondern knausrig. Und die Serverkosten dafür sind bei Firestore erst in ganz anderen
Größenordnungen spürbar; das Argument „laufende Kosten" trug hier also nicht einmal sachlich.

**Was Pro trägt:**

| | ohne Pro |
|---|---|
| Alles Lokale | frei |
| Cloud-Sync, Mehrgeräte-Nutzung | **frei** |
| **Gruppe gründen, einladen** | **Pro** |
| Gruppe beitreten, darin mitplanen | frei |

**In einer Gruppe zahlt der Inhaber, nicht das Mitglied.** Wäre die Gruppe für jeden Beteiligten
Pro-pflichtig, hieße „gemeinsam planen", dass beide zahlen — und jede Einladung wäre eine
Verkaufsaufforderung an den Partner. Das passt nicht zu „Paar oder WG". Verworfen wurden „beide
brauchen Pro" (sperrt Dritte aus) und „Gruppe bleibt ganz gratis" (dann trägt die Grenze nichts).

Damit steht die Pro-Stufe vorerst auf einem Bein. Das zweite ist der **Auto-Wochenplaner** (D2) —
er ist ab jetzt nicht mehr nur das stärkste, sondern das entscheidende Pro-Feature.

**Die Lehre, die bleibt:** Eine Funktion, die Nutzer als Teil des Kontos verstehen, lässt sich
nachträglich nicht in ein Verkaufsargument umdeuten. Der Preis dafür wäre nicht Umsatz, sondern
Vertrauen.

## Auto-Wochenplaner (16.08.2026)

**Ein Knopf im Wochenplan füllt die offenen Slots gegen das Kalorienziel.** Damit steht das
zweite Bein der Pro-Stufe (siehe oben) — und die App tut endlich selbst, was sie verspricht:
Entscheidungen abnehmen statt sie zu verwalten.

### Er plant aus zwei Quellen (16.08.2026)

**Der eigene Bestand allein reicht nicht.** Nach dem Onboarding stehen dort fünf Startmeals —
bei drei Haupt-Slots rotiert die Woche damit zwangsläufig auf denselben Gerichten. In der Praxis
kam heraus: sechsmal derselbe Joghurt zum Mittag, während 34 kuratierte Rezepte danebenlagen.

Der Planer zieht deshalb auch aus dem **Rezeptbuch** — gefiltert über `cookbookVisible()`, also
**nur, was zur Ernährungsform passt**. Eigene und kuratierte Meals stehen gleichberechtigt im
Topf; bei gleicher Bewertung gewinnt das eigene.

**Ein eingeplantes Rezeptbuch-Meal wandert seit dem 17.08.2026 NICHT mehr in die eigenen
Meals.** Bis dahin legte der Planer für jedes eingeplante Katalog-Rezept eine Bestandskopie an —
vermeintlich zwingend, weil der Wochenplan nur IDs speichert und ein Eintrag ohne passendes Meal
beim nächsten Laden verschwunden wäre. Diese Annahme war überholt: Das Rezeptbuch ist
mitgeliefert und auf jedem Gerät identisch, ein Planeintrag darf also direkt auf ein
Katalog-Gericht zeigen, ohne es vorher zu kopieren. Ein Planerlauf lässt den Bestand seither
unverändert. Der Toast nennt die Nutzung des Rezeptbuchs trotzdem weiter („· 6 Meals aus dem
Rezeptbuch") — eine relevante Information darüber, woher die Abwechslung dieser Woche kommt,
auch ganz ohne stillen Zuwachs im Bestand.

**„Meine Meals" enthält damit ausschließlich, was selbst angelegt oder bewusst übernommen
wurde** — eine bewusste Produktentscheidung, kein bloßes Implementierungsdetail. Wer ein
geplantes Rezeptbuch-Gericht wirklich in seine Sammlung holen und dort verändern will, tut das
weiterhin über den Übernehmen-Knopf (auch direkt aus der Meal-Ansicht eines Wochenplan-Slots
heraus) — genau der Weg, den das Rezeptbuch ohnehin vorsieht.

**Die Handauswahl schöpft aus derselben Menge wie der Planer.** Sobald der Bestand nicht mehr
bei jedem Planerlauf mitwächst, fiele eine bis dahin kaum sichtbare Asymmetrie auf: Der
Auto-Planer durfte aus dem gesamten Rezeptbuch wählen, wer einen Slot von Hand füllte, sah nur
den eigenen Bestand. Die Meal-Auswahl eines Slots zeigt deshalb beides — eigene Meals zuerst,
darunter der Abschnitt „Aus dem Rezeptbuch" (`pickerQuellen()`). Das spart den Umweg über
Übernehmen und hält den Grundsatz ein, dass zwei Wege zum selben Ziel dieselbe Auswahl haben.

Bewusst **nicht** dieselbe Funktion wie beim Planer (`planKandidaten()`), obwohl die Quellen
übereinstimmen: Der Planer muss rechnen und lässt Meals ohne Nährwerte weg. Von Hand darf man
sehr wohl etwas ohne Nährwerte einplanen — dem Nutzer eigene Meals vorzuenthalten, weil der
Planer mit ihnen nichts anfangen kann, wäre die falsche Sparsamkeit.

### Was er ist, und was er ausdrücklich nicht ist

Er ist **kein Rezept-Zufallsgenerator**. 21 verschiedene Gerichte in einer Woche sind das
Gegenteil dessen, wofür die App da ist: Sie wären sieben Einkäufe und sieben Kochabende. Der
Planer wählt je Slot-Art **zwei bis drei Gerichte für die ganze Woche** und wiederholt sie
(`PLAN_VARIANTEN`). Meal-Prep-taugliche Gerichte stehen dabei vorn, danach entscheidet der
Proteinanteil je Kalorie — die Zielgruppe der App ist Fitness und Abnehmen, nicht Abwechslung.

**Wichtig, damit die Zusage stimmt:** Der Proteinanteil **bevorzugt** Gerichte, er wird nicht
optimiert. Die Mengen rechnet der Planer gegen das **Kalorienziel**; ein Plan kann die Kalorien
also treffen und beim Protein trotzdem darunter liegen. Genau deshalb prüft die
Ehrlichkeits-Meldung (siehe unten) **beide** Säulen und nennt auch ein Protein-Defizit. Eine
Mengenrechnung gegen zwei Ziele gleichzeitig wäre ein anderer Algorithmus — der lohnt sich erst,
wenn die Bibliothek groß genug ist, um darin überhaupt Spielraum zu haben.

Er ist auch **kein Assistent mit Rückfragen**. Kein Regler für Abwechslung, keine Vorabfrage,
kein Bestätigungsdialog: ein Klick, ein Ergebnis, *Rückgängig* daneben. Ein
Konfigurationsdialog vor einer Automatik nimmt genau die Entscheidungen zurück, die sie
abnehmen sollte.

### Fünf Regeln

1. **Nur füllen, was für mich leer ist.** Bestehendes wird nie überschrieben. In einer Gruppe
   heißt „leer": kein Eintrag, der mich betrifft.
2. **Meal-Prep vor Abwechslung.**
3. **Das Ernährungsprofil ist eine harte Grenze**, keine Gewichtung. Ein veganes Profil bekommt
   nie ein Gericht ohne `vegan`-Tag — auch nicht, wenn die Makros perfekt passen.
4. **Die Kategorie muss GENAU zum Slot passen.** Der Picker ist großzügig — dort darf ein
   Mensch eine Beilage zum Frühstück einplanen, und ein Meal ohne bekannte Kategorie passt
   überall hin, damit nichts unplanbar wird. Ein Automatismus mit derselben Freiheit legt
   dagegen vier Shakes ins Mittagessen; genau das ist am 16.08.2026 passiert. Der Planer
   verwendet deshalb **nur, was ausdrücklich zu diesem Slot gehört**: Frühstück, Hauptgericht,
   Snack und Dessert. **Beilagen, Getränke und Meals ohne Kategorie plant er nie** — von Hand
   bleibt jeder Slot unverändert frei bebaubar.
5. **In der Gruppe wird einem vorhandenen Gericht beigetreten**, statt ein zweites zu wählen: ein
   Topf, zwei Teller. Das ist der eigentliche Trick am gemeinsamen Planen — drei Menschen mit
   3000, 2000 und 1800 kcal essen dasselbe Gericht in unterschiedlicher Anzahl. Passt es nicht
   zum eigenen Profil, wird ein anderes gewählt.

### Eine leere Zeile heißt „für alle" (16.08.2026)

Am Gerät zu zweit fiel auf: Der Planer trug **ausnahmslos sich selbst** ein. 31 von 31 Einträgen
trugen ein Namensschild. Der gemeinsame Wochenplan war randvoll — und für die andere Person
trotzdem leer, ihre Tagesbilanz stand auf null.

Der Maßstab lag längst in der App: Beim **manuellen** Einplanen entsteht in einer leeren Zeile
ein „für alle"-Gericht (`slotIsShared()`, an fünf Stellen). Der Auto-Planer war die einzige
Ausnahme. Er stellt jetzt dieselbe Frage.

**Das ist keine Fremdplanung.** Über das Kalorienziel der anderen wird nichts entschieden — jede
Bilanz rechnet weiter gegen ihr eigenes Ziel — und ein Klick auf das Personen-Symbol nimmt das
Gericht wieder heraus. Entschieden wird nur, **was gekocht wird**, und gemeinsam kochen ist der
Normalfall. Der darf keinen Zusatzklick kosten.

Die Grenze bleibt sauber:

* **Erste Portion** einer leeren Zeile → für alle.
* **Jede weitere** → nur mir. „Wir essen dasselbe, ich zweimal" — genau die Aussage, für die es
  Mehrfacheinträge in der Gruppe überhaupt gibt.
* **Beim Snack** ebenso: Die Zahl der Snacks hängt an meinem Restbudget, wer ein kleineres Ziel
  hat, soll nicht automatisch drei Kleinigkeiten mitessen.
* Steht in der Zeile schon eine **fremde Zuweisung**, entsteht kein „für alle" — sonst schriebe
  der Planer jemandem sein eigenes Gericht um.

### Beitreten statt doppeln (16.08.2026)

Der erste Test zu zweit zeigte, dass Regel 5 zwar das richtige Gericht wählte, aber einen
**zweiten Eintrag** dafür anlegte. Im Slot standen dann zwei Karten mit demselben Gericht und
zwei Namensplaketten. Rechnerisch stimmte alles — nur las es sich wie *jeder kocht für sich*,
obwohl *ein Topf, zwei Teller* gemeint war. **Der Plan zeigte die Buchhaltung statt das Essen.**

Deshalb trägt sich der Planer jetzt am **vorhandenen** Eintrag ein. Sind damit alle Mitglieder
dabei, wird daraus automatisch ein „für alle"-Gericht — aus zwei Karten wird eine, ohne Badge,
weil gemeinsam essen der Normalfall ist. Ein **zweiter** Eintrag entsteht nur noch, wenn jemand
wirklich zwei Portionen braucht. Dann ist er eine echte Aussage und keine Doppelung.

**Wer zuerst plant, wählt verträglich.** Ein veganes Hauptgericht kann auch der Fleischesser
mitessen, umgekehrt nicht. In einer Gruppe rücken Gerichte mit wenigen Einschränkungen deshalb
etwas nach vorn — damit die zweite Person häufiger beitreten kann und beide einmal kochen. Es ist
ein leichter Ausschlag, keine Vorentscheidung: Wer allein plant, merkt davon nichts, und das
Gedächtnis für Abwechslung wiegt weiterhin deutlich schwerer.

Verschiedene Ernährungsformen werden dabei **nicht wegprogrammiert**: Ein Veganer und ein
Fleischesser können nicht dasselbe essen. Dann stehen zwei Karten im Slot, jede mit ihrer
Plakette — und das ist die richtige Antwort, kein Fehler.

### Drei bewusste Grenzen beim gemeinsamen Planen

* **Der Planer füllt nie fremde Slots.** Ein Klick könnte die Woche für alle füllen, aber er
  würde für jemand anderen entscheiden — dessen Kalorienziel man gar nicht kennt (Ziffer 8a).
  Jeder plant für sich; das Zusammenführen passiert beim Beitreten.
* **„Nochmal" wirft nur die eigenen Einträge weg.** Fremde bleiben stehen, sie gehören jemand
  anderem. War man einem Gericht beigetreten, steigt man wieder aus — das Gericht selbst bleibt
  der anderen Person erhalten.
* **Die Reihenfolge entscheidet.** Wer zuerst plant, gibt die Woche vor. Ein echtes „für alle
  zugleich planen" bräuchte die Ziele aller, und die sind ausdrücklich privat.

### Abwechslung ist eine eigene Regel (16.08.2026)

Der erste Planer lieferte **an jedem Tag dasselbe Gericht für Mittag und Abend**. Das war kein
Zufall, sondern zwangsläufig: Beide Slots zogen aus derselben Menge, mit derselben Bewertung und
demselben Rotationsindex. Daraus folgen drei Festlegungen:

* **Mittag und Abend bekommen getrennte Gerichte** — je drei, aus disjunkten Mengen. Macht sechs
  verschiedene Hauptgerichte pro Woche.
* **An einem Tag nie zweimal dasselbe Gericht.** Das ist eine harte Regel am Ende der Auswahl,
  keine Wahrscheinlichkeit.
* **Eine Portion je Hauptmahlzeit**, wenn allein geplant wird. Mehrere Einträge desselben
  Gerichts ergeben nur in der Gruppe Sinn (siehe unten) — allein sehen sie wie ein Fehler aus.
  Was zum Tagesziel fehlt, geht in die Snack-Zeile; bleibt danach etwas offen, wird es benannt.

### Jeder Lauf ein anderer Plan

Der Planer nimmt **nicht** die drei bestbewerteten Gerichte, sondern zieht aus den **acht besten**
gewichtet nach Rang. Damit ergibt jeder Klick einen anderen Vorschlag — und jeder ist gut, weil
schwache Kandidaten gar nicht erst im Feld sind. Reiner Zufall würde auch das schlechteste
Gericht ziehen und die Zusage „trifft dein Kalorien- und Proteinziel" untergraben.

Dazu ein **„Nochmal"** direkt im Toast: Der Vorschlag wird verworfen und neu gewürfelt, so oft
man will. Ohne diesen Knopf müsste man über „Woche leeren" samt Rückfrage gehen — drei Schritte
für eine Meinungsfrage.

### Der Planer erinnert sich

Was in den letzten zwei Wochen dran war, wird abgewertet — **nicht gesperrt**. Bei sechs eigenen
Meals würde eine Sperre Slots leer lassen; die Abwertung wirkt dann gleichmäßig und das Ergebnis
bleibt brauchbar. Mit einer großen Bibliothek führt dieselbe Regel dazu, dass praktisch jede Woche
andere Gerichte oben stehen. Eine Regel, die über beide Größenordnungen trägt.

Dafür merkt sich das Konto zu eingeplanten Meals die Kalenderwoche (`state.planned`) — persönlich,
auch in einer Gruppe, und nach einigen Wochen automatisch vergessen.

### Mehrere Portionen ja, viermal dasselbe Getränk nein

Bei Frühstück, Mittag und Abend sind **Vielfache richtig** — sie sind Regel 5 in Zahlen: zweimal
Porridge bei 3000 kcal, einmal bei 1800.

Beim **Snack-Slot** war dieselbe Rechnung falsch. Er bekommt den Rest des Tages, und der ist
groß; bei einem 150-kcal-Shake ergab `Rest / kcal` vier Stück desselben Getränks. Als Mahlzeit
isst man zwei verschiedene Kleinigkeiten, nicht viermal dasselbe. Der Snack-Slot füllt deshalb
mit **verschiedenen** Snacks, jeden höchstens einmal am Tag. Bleibt danach etwas offen, wird es
im Toast benannt statt mit Wiederholungen aufgefüllt.

### Ehrlich sein statt schönrechnen

Trifft der Plan das Wochenziel um mehr als 10 % nicht, **sagt die App das**: „Woche geplant ·
noch rund 400 kcal offen" — und, wenn die Kalorien stimmen, das Protein aber nicht: „· rund
120 g Protein fehlen". Beim Protein zählt nur ein Defizit; es ist eine Untergrenze, darüber ist
gut. Lieber ein offener Rest als ein Plan, der die Lücke versteckt. Das ist dieselbe Haltung wie
beim Rückblick (siehe unten): Die Marke hilft, sie beschönigt nicht.

Genannt wird immer nur **ein** Zusatz, damit der Toast kurz bleibt — kcal vor Protein, denn wer
3000 kcal zu wenig geplant hat, hat das größere Problem.

Genauso wird nicht geraten: **Meals ohne Nährwerte fallen aus der Auswahl** statt geschätzt zu
werden. In einer Fitness-App ist eine erfundene Zahl schlimmer als ein fehlendes Gericht.

### Grenzfälle, die zum Produkt gehören

| Lage | Verhalten |
|---|---|
| Kein Ziel gesetzt | Der Knopf erscheint gar nicht — ohne Ziel gibt es nichts zu treffen |
| Weniger als sechs passende Meals | „Zu wenige passende Meals – leg noch welche an." Kein magerer Plan |
| Alle Slots schon belegt | „Deine Woche ist schon geplant." Kein Leerlauf-Klick |
| Wenig Auswahl je Slot | Der Plan entsteht, der Hinweis nennt die fehlende Abwechslung |

### Pro-Gating

Der Planer ist eine Pro-Funktion — **in einer Gruppe darf ihn aber jedes Mitglied nutzen**, auch
ohne eigenes Pro. Das folgt aus „in der Gruppe zahlt der Inhaber"; ohne diese Ausnahme könnte
ein eingeladenes Mitglied seinen Teil der Woche gar nicht füllen, und Regel 5 liefe leer.

Ohne Pro erscheint derselbe freundliche Hinweis wie beim Gruppen-Gründen, kein toter Knopf.

## Rezeptbuch (15.08.2026)

Im Meals-Reiter gibt es zwei Ansichten: **Meine Meals** und **Rezeptbuch** — ein kuratierter
Katalog, aus dem man mit einem Tipp übernimmt. Was man übernimmt, ist eine **Kopie**: Sie
gehört danach dem Nutzer und darf frei bearbeitet werden.

**Der Katalog ist nach dem Ernährungsprofil gefiltert.** Wer vegan gewählt hat, sieht vegane
Meals. Das ist der erste sichtbare Nutzen des Profils.

**Im eigenen Bestand wird dagegen nicht gefiltert** — die Meals dort hat der Nutzer selbst
angelegt, sie zu verstecken wäre Bevormundung. Vorschläge filtern, Eigenes nie.

### Die 30 Rezepte (15.08.2026)

Der Katalog ist vollständig: **34 Rezepte in allen sechs Kategorien** — 7 Frühstück,
16 Hauptgerichte, 5 Snacks, 2 Desserts, 2 Beilagen, 2 Getränke. Die Aufteilung ist keine
Gleichverteilung, sondern folgt dem Wochenplan: Mittag und Abend sind vierzehn Slots pro Woche,
Dessert und Getränk je einer.

**Ausgerichtet auf Fitness und Meal-Prep, nicht auf Vielfalt um ihrer selbst willen:**

* **21 von 34 sind zum Vorkochen geeignet** (`mealPrep`). Wer sonntags kocht, braucht Gerichte,
  die drei Tage im Kühlschrank überstehen — nicht Rührei.
* **21 von 34 erreichen die Schwelle „Proteinreich"** (≥ 30 % der Kalorien aus Protein).
* Die Portionen liegen zwischen 207 kcal (Getränk) und 680 kcal (Hauptgericht) — planbar gegen
  ein Tagesziel, ohne dass ein einzelnes Meal die Bilanz sprengt.
* **15 von 34 sind vegan, 24 vegetarisch**, und zwar in **jeder** Kategorie. Der Katalog wird
  nach dem Profil gefiltert; wer vegan gewählt hat, darf nicht vor einer halb leeren Ansicht
  stehen.

**Jedes der 34 Rezepte hat ein eigenes Bild** (`img/library/`, zusammen rund 1,6 MB, je 40–65 KB
im Format 2,4:1). Sie sind KI-generiert, in einem einzigen eingefrorenen Stil: dunkles
Nussbaumholz, helles mattes Steingut, 45-Grad-Seitenansicht. Das ist der sichtbarste Unterschied
zu vorher — der Katalog lief bis dahin auf allgemeinen Stichwortfotos, auf denen zwei
verschiedene Gerichte dasselbe Bild trugen. Bei der Sichtprüfung fielen zwei durch und wurden neu
gezogen: der Chia-Pudding (sachlich richtig grau) und der Eiweißshake (stand in einer Schüssel
statt im Glas, weil die Kategorie „Snack" das Geschirr bestimmte).

### Der erste Bestand kommt aus dem Katalog (15.08.2026)

**Die vier festen Beispiel-Meals sind abgeschafft.** Nach dem Onboarding legt die App **fünf
Startmeals** an, die zur gewählten Ernährungsform passen — Kopien aus dem Rezeptbuch.

**Der Grund ist ein Zeitpunkt, keine Geschmacksfrage.** Die alten Beispiele wurden beim
allerersten Start eingesetzt, also *bevor* nach der Ernährungsform gefragt wurde. Ein Veganer
bekam als Begrüßung ein Rindersteak und einen Molke-Shake. Die Auswahl stand fest, bevor
irgendetwas über den Nutzer bekannt war.

**Verteilt auf 1 Frühstück, 3 Hauptgerichte, 1 Snack** — damit ist jeder Slot-Typ des
Wochenplans sofort bedienbar, und die Hauptgerichte, die 14 Slots pro Woche füllen müssen, haben
Auswahl. Wo möglich mit `mealPrep`.

**Es sind echte Meals, keine Attrappen.** Sie synchronisieren, sie wandern in eine Gruppe, sie
tauchen im Rezeptbuch als „In deinen Meals" auf. Der Knopf „Beispiele entfernen" ist damit
entfallen: Es gibt nichts mehr, was sich vom eigenen Bestand unterscheidet — löschen kann man
sie einzeln wie jedes andere Meal.

**Und sie tragen dieselben Bilder wie der Katalog.** Ein Bestand mit allgemeinen Stichwortfotos
neben einem hochwertigen Katalog hätte den ersten Eindruck genau dort gebrochen, wo er entsteht.

**Die vier alten Gerichte sind nicht verloren** — sie stehen jetzt im Rezeptbuch (Katalog damit
**34** Rezepte). Ihre Bilder lagen bereits im richtigen Stil vor, und das Rindersteak ist bis
heute das einzige seiner Art.

**Die Bilder liegen nicht im Precache des Service Workers.** Sie kommen beim ersten Blick auf
die Meals und liegen danach dauerhaft im Cache. Den Kaltstart um über ein Megabyte zu
verteuern, für Bilder, die viele Nutzer nie sehen, wäre die falsche Abwägung — Ladezeit ist in
dieser App ein Produktwert.

**Herkunft der Rezepte, für den Fall der Frage:** Sie sind für dieses Projekt **selbst
formuliert** — keine Übernahme aus Rezeptsammlungen, Kochbüchern oder einer Rezeptdatenbank.
Die einzige benutzte Datenquelle ist die projekteigene `FOODS`-Tabelle. Das ist keine bloße
Vorsichtsmaßnahme: Ein Rezept **als solches** ist ohnehin nicht urheberrechtlich geschützt
(Zutaten und Mengen sind eine Handlungsanweisung, keine persönliche geistige Schöpfung,
§ 2 Abs. 2 UrhG); schutzfähig wäre allein eine eigenständige sprachliche Fassung des
Zubereitungstexts. Die Texte hier sind kurz und zweckgebunden und erreichen das nicht.
Gerichtsnamen sind bewusst **beschreibend** und nennen keine Marken.

**Das Risiko liegt bei den Bildern, nicht bei den Texten** — dafür gelten `PHOTO_CREDITS` und
`CLAUDE.md` §22 unverändert weiter. Die 30 Bilder des Rezeptbuchs sind KI-generiert und im
Impressum als solche gekennzeichnet; zu jedem ist in `img/library/bilder-protokoll.json`
festgehalten, mit welcher Beschreibung, welchem Modell und wann es entstanden ist. Das ist der
Beleg, dass nichts von fremden Seiten übernommen wurde. Kommt eine künftige Charge Rezepte aus einer fremden
Quelle, ist das eine **andere** Rechtslage als diese hier; siehe auch die Entscheidung gegen
Scraping für die Pro-Bibliothek.

**Jeder Nährwert ist gegengerechnet, keiner geschätzt** (`tools/rezept-makros.py`). Das ist
keine Genauigkeitsspielerei: Ein Katalog, der um 30 % danebenliegt, macht die Tagesbilanz —
den Kern der App — wertlos.

**Was der Filter sagt, muss die Karte bestätigen.** Der Tag „High Protein" und das Badge
„Proteinreich" kommen aus zwei Quellen (gepflegt bzw. gerechnet). Im Katalog sind sie
deckungsgleich; vier der ersten neun Rezepte trugen den Tag ohne die Schwelle zu erreichen und
haben ihn verloren. Bei **eigenen** Meals gilt das nicht — dort taggt der Nutzer selbst.

**Mit Pro wächst dieselbe Ansicht** von 30 auf über 100 Rezepte, die monatlich wechseln. Das
ist der Kern des Pro-Versprechens: nicht ein anderer Ort, sondern **mehr vom selben, laufend
neu**. Ein Gratis-Nutzer lernt den Mechanismus an 30 Rezepten kennen und versteht ohne
Erklärtext, was Pro bringt.

**Kein eigener Reiter, und das war eine Korrektur.** Der erste Entwurf sah einen Rezeptbuch-
Reiter anstelle von „Fortschritt" vor. Der `ux-reviewer` hat zwei Einwände gebracht, die beide
trugen: Die vier Reiter sind Tätigkeiten (orientieren, planen, verwalten) — „entdecken"
gehört **vor** das Verwalten, nicht daneben. Und die Gewichtskarte zurück auf Home zu holen
hätte genau den überladenen Zustand wiederhergestellt, den B8 zwei Tage zuvor aufgelöst hatte.

### Keine Vegan/Vegetarisch-Badges auf der Karte (entschieden 15.08.2026)

Die Meal-Karte zeigt höchstens zwei gerechnete Badges („Proteinreich", „Low Carb", aus
`macroBadges()`). Ein drittes für die Ernährungsform wurde geprüft und **verworfen**:

* **Es hätte keine Trennschärfe.** 24 von 34 Rezepten sind vegetarisch, 15 vegan — ein Badge auf
  drei Vierteln der Karten informiert nicht mehr, es wird Tapete. Badges leben von Seltenheit.
* **Im Rezeptbuch wäre es redundant.** Der Katalog ist bereits nach der Ernährungsform gefiltert;
  wer vegan gewählt hat, sieht ausschließlich vegane Meals.
* **Es verdeckt das Bild.** Die Badges liegen als Overlay auf dem Foto — und die Fotos sind gerade
  der Grund, warum die Karten überhaupt hochwertig wirken.

Die Information ist vollständig verfügbar: als Merkmal im großen Sheet (`mealFlagsHtml()`) und
als Filter-Chip in beiden Ansichten.

## Ernährungsprofil (15.08.2026)

Die Einführung fragt seit dem 15.08.2026 nach der **Ernährungsform** (Alles / Vegetarisch /
Vegan) und optionalen **Einschränkungen** (glutenfrei, laktosefrei). Beides liegt in
`state.goal`.

**Warum das kein Nachzügler sein durfte:** Ohne diese Angabe plant der Auto-Wochenplaner einem
Veganer Rindersteak — nicht als Panne, sondern systematisch. Und die kuratierte Bibliothek (C1)
wüsste nicht, welche Meals sie überhaupt braucht. Nachträglich eingeführt hieße: 30 Meals
nachtaggen, den Planer umbauen, die Beispieldaten austauschen.

**Die Ernährungsform ist eine harte Grenze, keine Gewichtung.** Wer vegan gewählt hat, bekommt
nie ein Gericht ohne den Tag — auch nicht, wenn die Makros perfekt passen. „Ungefähr vegan" gibt
es nicht.

**Vegan schließt vegetarisch ein.** Wer vegetarisch wählt, sieht auch vegane Gerichte; ohne diese
Regel fiele die Hälfte des Bestands weg.

**Der Meal-Filter wird bewusst NICHT vorbelegt.** Er filtert die *eigene* Sammlung — die hat der
Nutzer selbst angelegt, und sie automatisch zu beschneiden versteckt nur etwas, statt Zeit zu
sparen. Das Profil wirkt dort, wo *Vorschläge* entstehen: im Auto-Planer und in der
Pro-Bibliothek.

**Formulierung:** „Ich möchte glutenfreie Meals", nicht „Ich vertrage kein Gluten". Die App fragt
tatsächlich nur, was vorgeschlagen werden soll, und leitet daraus keine Gesundheitsaussage ab —
das ist der Unterschied zwischen einer Präferenz und einem Gesundheitsdatum nach Art. 9 DSGVO.

## Ein Meal ist eine Portion (15.08.2026)

**Die App kennt keine Portionsgrößen mehr.** Ein Meal ist genau eine Portion: Nährwerte und
Zutatenmengen beschreiben denselben Gegenstand. Wer mehr braucht, plant das Meal zweimal ein.

Das ist der dritte und letzte Schritt einer Linie, die zweimal vorher gezogen wurde: Der
Portionsfaktor am Slot-Eintrag (B5) und das Merkmal „Aufwand" sind aus demselben Grund
gefallen — sie verlangten eine Entscheidung, ohne dafür etwas zurückzugeben.

Bei `portions` kam hinzu, dass das Feld **schlicht falsche Ergebnisse erzeugte**: Die
Tagesbilanz rechnete mit den vollen Nährwerten des Rezepts, die Einkaufsliste mit den vollen
Zutatenmengen — und der Teiler griff nur bei individuell zugewiesenen Gerichten in einer Gruppe.
Im Normalfall kaufte man für zwei und rechnete für einen. Der eigene Beispieldatensatz enthielt
genau diesen Fehler.

**Was dadurch einfacher wird:**

* Die Einkaufsliste stimmt zum ersten Mal mit den Nährwerten überein.
* Die Vorkochen-Ansicht sagt „Hähnchen 4× diese Woche" statt „4 Portionen, 2 Durchgänge" — die
  Frage, wie viel in einen Topf passt, beantwortet ohnehin nur der Topf.
* **Der Auto-Planer bekommt eine verlässliche Einheit.** Unterschiedliche Kalorienziele in einer
  Gruppe lassen sich damit über die **Anzahl** der Einträge abbilden: Alle essen dasselbe
  Gericht, wer mehr braucht, bekommt zwei davon. Einmal kochen, verschiedene Mengen.

Bestehende Meals mit `portions > 1` werden beim Laden einmalig umgerechnet (Mengen geteilt),
statt den Fehler stillschweigend weiterzutragen — siehe `docs/ARCHITECTURES.md`.

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

### Umgesetzt seit 13.08.2026: Tags und Meal-Prep

Zwei dieser Metadaten stehen im Datenmodell: `tags[]` und `mealPrep`
(siehe `docs/ARCHITECTURES.md`). Bewusst **feste Tag-Schlüssel statt Freitext** — nur damit
können Filter, kuratierte Bibliothek und der spätere Auto-Planer rechnen. Freitext-Tags
schreibt jeder anders, und ein Filter, der „Low Carb" nicht findet, ist schlimmer als keiner.

**Ein „Aufwand"-Feld (Einfach / Mittel / Aufwendig) gab es einen Tag lang und ist wieder
entfernt worden.** Es war gut gemeint und sogar sauber benannt — in der Küche entscheidet man
nach Aufwand, nicht nach Können —, aber **nichts wertete es aus**: nicht der Filter, nicht der
geplante Auto-Planer. Genau das ist der Fall, den der Produktfilter oben abfangen soll: Ein
Merkmal, das nur erfasst und angezeigt wird, kostet jeden Nutzer eine Entscheidung im Editor
und bringt ihm nichts zurück.

Die Regel für alles Weitere aus dieser Liste (Ziel-Eignung, Preis, …): **Ein Feld entsteht,
wenn ein konkretes Feature es liest** — nicht, weil es später einmal nützlich sein könnte.

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
* **Zurückgenommen: der Portionsfaktor am Slot** (½ / 1 / 1½ / 2, war einen Tag lang drin).
  Er saß als eigener Knopf am selben Vorschaubild wie die Zuweisung und beantwortete eine sehr
  ähnliche Frage — „wie viel davon" neben „für wen" —, ohne dass beide zusammen gedacht waren.
  Zwei gleich große Bedienelemente nebeneinander, die Verwandtes tun, kosten mehr Aufmerksamkeit
  als sie einbringen. Die Menge steuert weiterhin die Zuweisung (wer isst mit) und die
  Personenzahl der Einkaufsliste. Käme das Thema zurück, dann als **eine** Entscheidung
  zusammen mit der Zuweisung, nicht als zweiter Knopf daneben.
* **„Woche leeren" steht nicht mehr neben der Einkaufsliste.** Eine destruktive Aktion mit
  derselben Prominenz wie das meistgenutzte Werkzeug ist ein Fehlerangebot; die Rückfrage
  allein ist keine Entschuldigung dafür.

Bewusst **keine** freie Portionszahl: vier Stufen decken den Alltag ab, ein Zahlenfeld wäre
mehr Eingabe für weniger Klarheit.

## Bewusste Produktentscheidung: Vorkochen ist eine eigene Ansicht

Der Wochenplan beantwortet „was esse ich wann?", die Einkaufsliste „was muss ich kaufen?".
Beim Meal-Prep fehlte die dritte Frage: **„was koche ich am Sonntag, und wie viel davon?"**

„Vorkochen" (seit 13.08.2026, im Überlaufmenü des Wochenplans) bündelt denselben Wochenbestand
nach **Gericht** statt nach Tag. Je Gericht zwei Zahlen, und die zweite ist die eigentlich
nützliche:

* **Portionen** — ein Eintrag je Esser (bei Zuweisung) bzw. je eingestellter Person
* **Durchgänge** — `Portionen / portions` des Rezepts, aufgerundet: so oft muss der Topf auf
  den Herd. Ohne gepflegtes `portions` entfällt die Angabe, statt eine Eins zu erfinden.

Sortiert nach Portionen absteigend — danach richtet sich, womit man anfängt.

**Derselbe Zeitraum wie die Einkaufsliste** (aktuelle Woche ab heute, nächste Woche ganz).
Beide Ansichten müssen dieselbe Woche beschreiben, sonst kauft man für einen Tag ein, den die
Vorkochliste nicht mehr kennt.

Bewusst **keine** eigene Kochreihenfolge, keine Zeitplanung, keine Ofen-Belegung. Das wäre eine
Küchen-App; hier geht es um die Frage, was in welcher Menge auf die Liste kommt.

## Bewusste Produktentscheidung: Der Wizard endet im Wochenplan

Der Abschlussknopf der ersten Schritte heißt „Zum Wochenplan" — er landete bis 13.08.2026
trotzdem auf **Home**, und Home zeigt einem frisch angelegten Konto vor allem leere Ringe. Der
Wochenplan ist der Ort, an dem etwas zu tun ist: An jedem Slot steht „+ Meal wählen", und die
vier Beispiel-Meals liegen bereit. Mobil startet er am heutigen Tag.

Wer nur sein Ziel neu berechnet, kennt die App und geht wie bisher zurück auf Home.

Bewusst **kein** automatisch aufspringender Meal-Picker: Nach mehreren Schritten Formular
gleich das nächste Fenster zu öffnen, nimmt dem Nutzer die erste eigene Entscheidung ab, statt
ihm Arbeit abzunehmen.

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

### Höchstens vier Personen (16.08.2026)

Eine Gruppe fasst **vier** Mitglieder: Paar, WG oder Familie. Wer mehr braucht, ist kein Haushalt
mehr — und **Pro trägt einen Haushalt, keine Verteilerliste.**

Vorher gab es gar kein Limit, und das war eine offene Flanke: Cloud-Sync ist ausdrücklich gratis,
Pro trägt allein das *Gründen* einer Gruppe. Ein einmal weitergereichter Einladungslink ließ
beliebig viele herein — einer zahlt, zehn essen mit. Das ist kein theoretischer Missbrauch,
sondern der naheliegende: Man teilt einen Link, den man hat.

Vier statt zwei, obwohl die Praxis zu zweit stattfindet: Das Datenmodell trägt es ohnehin
(Farbvergabe, Initialen-Auflösung, Zuweisungs-Chips, Einkaufsliste), und Ziffer 8a der
Datenschutzerklärung nennt seit jeher „etwa als Paar oder WG". Ein Limit von zwei hätte eine
Zusage gebrochen, die schon gemacht war.

**Der Riegel liegt in den Firestore Rules, nicht in der Oberfläche.** Der Missbrauchende wäre
hier der Inhaber selbst — eine ausgeblendete Schaltfläche hält ihn nicht auf. Die Oberfläche
zeigt nur die freundliche Seite davon: Ist die Gruppe voll, verschwindet „Person einladen" und
ein Satz erklärt es; wer mit einem Link auf eine volle Gruppe trifft, liest „Diese Gruppe ist
schon voll." — **ohne Zahl**, denn wie groß eine fremde Gruppe ist, geht Außenstehende nichts an.

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
