# STORE.md

# App Store und Google Play — die Prüfliste

**Das erklärte Leitziel des Projekts: Paddy's Mealplan erscheint in beiden Stores.**
Dieses Dokument ist der Maßstab dafür. Es beschreibt, was die Stores verlangen, wo das
Projekt heute steht und welche Entscheidungen noch offen sind.

**Register:**

| Abschnitt | Inhalt |
|---|---|
| 1. Der Weg dorthin | Capacitor, warum kein reiner WebView |
| 2. Bezahlung | Apple 3.1.1 — der teuerste offene Punkt |
| 3. Konto-Löschung | Pflicht seit 2022 |
| 4. Kein nachgeladener Code | Apple 2.5.2, deshalb `vendor/` |
| 5. Datenschutz-Formulare | Nutrition Labels, Data Safety |
| 6. Berechtigungen | Kamera |
| 7. Pflicht-Anhängsel | Was im Store-Eintrag steht |
| 8. Technische Mindestanforderungen | Offline, Login, Tablet |
| 9. Stand und offene Punkte | Wo es heute hängt |

Geprüft wird das laufend durch den Agenten `store-check`.

---

## 1. Der Weg dorthin

Die App ist heute eine Web-App aus `index.html`, `css/`, `data/` und `lib/`, ausgeliefert über GitHub Pages unter
`www.paddysmealplan.de`. Für die Stores wird sie mit **Capacitor** verpackt.

**Der entscheidende Punkt beim Verpacken:** Die App muss **lokal** ausgeliefert werden und
ohne Netz starten. Ein Wrapper, der nur `www.paddysmealplan.de` in einem WebView anzeigt,
trifft gleich zwei Ablehnungsgründe — Apple 4.2 („minimale Funktionalität", eine Website
in einer Hülle) und 2.5.2 (Code aus dem Netz).

**Seit dem 29.08.2026 liegt der Code auf mehreren Dateien** (`index.html`, `css/`,
`data/`, `lib/`). Capacitor kopiert beim Verpacken **einen** Ordner ins App-Paket,
konfiguriert über `webDir`. Zeigt der auf etwas, das nur `index.html` enthält, startet die
native App mit **leerem `#view`** — bei völlig fehlerfreiem Build: die Seite lädt, die
Skripte fehlen. Genau das Fehlerbild, das im Web HTTP 200 liefert und trotzdem nichts
zeigt (`docs/TROUBLESHOOTING.md` §5 und §6).

`webDir` muss deshalb so gesetzt sein, dass **alle vier** mitkommen. Die verbindliche
Liste dessen, was geladen wird, steht erzeugt in `docs/MODULE.md` unter „Ladereihenfolge“ —
sie ist die Prüfliste für den ersten Capacitor-Build.

**Erste Prüfung im nativen Projekt:** App starten, `#view` muss gefüllt sein. Ist es leer,
fehlt `css/`, `data/` oder `lib/` im Bundle — nichts anderes.

---

## 2. Bezahlung — Apple 3.1.1

**Der teuerste offene Punkt, und er ist eine Architekturentscheidung.**

Apple verlangt für digitale Inhalte und Funktionen, die **in der App** freigeschaltet
werden, In-App-Purchase. Ein Pro-Zugang, der über einen Web-Bezahlweg (Stripe, PayPal,
eigene Seite) verkauft oder auch nur **verlinkt** wird, ist ein klassischer
Ablehnungsgrund. Google Play verlangt Entsprechendes über Google Play Billing.

### Was Pro heute umfasst — zwei Beine, nicht eines

Korrigiert am 26.08.2026 nach Prüfung am Code. Eine frühere Fassung dieses Dokuments nannte
nur die Gruppe; das war überholt:

| Pro-Funktion | Wo durchgesetzt |
|---|---|
| **Gruppe gründen** und in der Gruppe planen | **In den Regeln.** `groupOwnerHasPro(gid)` bei `groups/{gid}/plans` und `groups/{gid}/recipes` (`firestore.rules:340`, `:347`) |
| **Auto-Wochenplaner** — laut `docs/PRODUCT.md` „das entscheidende Pro-Feature" | **Nur im Client.** `if (!isPro() && !syncGid)` in `index.html:8645` |

Cloud-Sync selbst bleibt ausdrücklich gratis.

### ⚠️ Die Lücke: Der Auto-Planer ist bei Solo-Konten nicht durchgesetzt

Ein Solo-Konto schreibt sein Planergebnis in `users/{uid}`. Diese Regel hat **bewusst keine
Pro-Prüfung** (`firestore.rules:112-121`, ausdrücklich so entschieden am 15.08.2026, weil
Cloud-Sync frei bleiben soll). Der `isPro()`-Riegel davor ist damit eine **UI-Sperre** — und
UI-Sperren sind keine Sicherheitsgrenze (CLAUDE.md § 12). Wer `autoPlanWeek()` über die
DevTools aufruft, bekommt den Plan.

Solange niemand für Pro bezahlen kann, ist das folgenlos. **Sobald echtes Geld daran hängt,
verkauft man eine Funktion, die technisch nicht durchgesetzt ist.** Das ist zuerst ein
Umsatzthema und erst danach ein Store-Thema.

Eine regelseitige Durchsetzung ist schwierig: Die Rules können den *Inhalt* eines Plans
kaum prüfen — sie sehen nicht, ob er von Hand oder automatisch entstanden ist. Realistische
Optionen: bewusst als bekannte Grenze dokumentieren (wie bei `memberCount`), oder den Planer
serverseitig rechnen lassen.

### Was der Verkauf zusätzlich verlangt

- **15–30 % Marge** (15 % im Small Business Program bis 1 Mio. USD Jahresumsatz).
- **„Wiederherstellen" ist Pflicht** bei nicht verbrauchbaren Käufen und Abos. Existiert
  heute nicht — es gibt noch nichts wiederherzustellen.
- Bei einem Abo müssen Preis, Laufzeit und Verlängerungsbedingungen **vor** dem Kauf
  sichtbar sein, mit Link auf AGB und Datenschutzerklärung auf derselben Ansicht.

### Wie ein Kaufbeleg nach `entitlements` käme — heute gar nicht

`entitlements/{uid}` ist regelseitig sauber: `allow get` nur für die eigene UID,
`create, update: if false`. Ein Client kann sich **kein Pro selbst geben**. Geschrieben wird
das Dokument heute **von Hand in der Firebase-Konsole** (`FIREBASE-SETUP.md:147`).

Für echten Store-Betrieb braucht es dazwischen einen Server, der die Quittung bei Apple bzw.
Google validiert und dann `entitlements/{uid}` schreibt. **Das kollidiert mit dem aktuellen
Firebase-Tarif:** Cloud Functions verlangen **Blaze** (Pay-as-you-go); das Projekt läuft auf
**Spark**. Ohne Tarifwechsel gibt es serverseitig gar keinen Ort für die Prüfung.

Der Tarifwechsel gehört damit **vor** den Bau der Bezahlung, nicht danach.

### Entschieden am 26.08.2026

| Frage | Entscheidung |
|---|---|
| Abo oder Einmalkauf? | **Abo**, monatlich **und** jährlich (jährlich mit Rabatt) |
| Wann Blaze? | **Beim Baubeginn der Bezahlung**, nicht vorher — aber fest eingeplant |
| Auto-Planer trotz Client-Lücke Pro? | **Ja**, als bekannte Grenze dokumentiert |
| Wo liegen künftige Pro-Rezepte? | **In Firestore** hinter `hasPro()`, nicht in `index.html` |

Begründungen: `docs/PRODUCT.md`, Abschnitt „Bewusste Produktentscheidung: Wie Pro verkauft
wird". Umgesetzt ist davon **noch nichts** — die Entscheidungen legen fest, wie gebaut wird.

---

## 3. Konto-Löschung in der App

Pflicht bei Apple seit 2022: Wer in der App ein Konto anlegen kann, muss es **in der App**
wieder löschen können. Nicht per E-Mail, nicht über eine Webseite. Die Löschung muss das
Konto tatsächlich entfernen, nicht nur abmelden.

Stand: `deleteAccountFlow()` existiert. Zu prüfen bleibt bei jeder Änderung:

- Erreichbar ohne Umwege?
- Trifft sie **beide** Speicher — `localStorage` und Cloud? (TROUBLESHOOTING 37)
- Übersteht sie einen fremden oder toten `shared/{id}`-Eintrag? (TROUBLESHOOTING 48)
- Was passiert mit einer Gruppe, wenn der **Inhaber** löscht?

---

## 4. Kein nachgeladener ausführbarer Code — Apple 2.5.2

Apple lehnt Apps ab, die zur Laufzeit Code aus dem Netz holen und ausführen.

**Deshalb liegt das Firebase-SDK seit dem 23.08.2026 unter `vendor/`** statt auf dem
gstatic-CDN, geholt und angepasst durch `tools/firebase-vendor.py`. Dasselbe gilt für
ZXing.

Bei jeder Änderung zu prüfen: Gibt es irgendwo wieder ein `<script src="https://…">`, ein
dynamisches `import()` auf eine fremde URL, `eval` oder `new Function` mit nachgeladenem
Inhalt? **Jeder neue CDN-Verweis macht diese Arbeit zunichte.**

Nebeneffekt, der ebenfalls zählt: Ohne CDN startet die Cloud-Anmeldung auch offline.

---

## 5. Datenschutz-Formulare beider Stores

**Apple Privacy Nutrition Labels** und **Google Play Data Safety** fragen dasselbe in
unterschiedlichen Formularen: Welche Daten werden erhoben, sind sie mit der Person
verknüpft, wozu dienen sie, gehen sie an Dritte?

Aus dem Code abgeleitet:

| Datentyp | Erhoben | Personenbezug | Zweck |
|---|---|---|---|
| E-Mail-Adresse | ja (Firebase Auth) | ja | Konto |
| Nutzerinhalte (Meals, Pläne, eigene Fotos) | ja | ja | Kernfunktion |
| **Gesundheit & Fitness** (Gewicht, Ziel, Kalorienbedarf, Rückblick) | ja | ja | Kernfunktion |
| Gruppen-Mitgliedschaften | ja | ja | Gemeinsam planen |
| Barcode-Abfragen | an Open Food Facts | nein | Produktsuche |

**Die Kategorie „Health & Fitness" ist der heikle Punkt.** Sie zieht bei Apple schärfere
Anforderungen nach sich und korrespondiert mit der Frage, ob Art. 9 DSGVO greift — siehe
`docs/DATENSCHUTZ-INTERN.md`.

Empfänger, die genannt werden müssen: Google (Firebase), Cloudflare (Worker), GitHub
(Pages), Open Food Facts.

Ein falsch ausgefülltes Formular ist ein eigener Ablehnungsgrund — und später ein
Rechtsrisiko, weil es eine Zusage gegenüber den Nutzenden ist.

---

## 6. Berechtigungen

**Kamera** (Barcode-Scanner) ist die einzige heikle:

- iOS braucht `NSCameraUsageDescription`. **Ohne diesen Text stürzt die App beim ersten
  Zugriff ab**; mit einem nichtssagenden Text wird sie abgelehnt. Er muss den konkreten
  Zweck nennen („um Barcodes von Lebensmitteln zu scannen").
- Die Abfrage gehört in den **Moment der Nutzung**, nicht in den App-Start.
- Keine Berechtigung anfordern, die nicht gebraucht wird.

---

## 7. Pflicht-Anhängsel im Store-Eintrag

- **Datenschutzerklärung als URL** — nicht nur in der App.
- **Support-Kontakt.**
- **Altersfreigabe / Content Rating** ausgefüllt.
- **Keine medizinischen Heilversprechen.** Die App ist kein Medizinprodukt und darf sich
  nicht so darstellen. Das betrifft UI-Texte *und* die Store-Beschreibung.
- **Keine Verweise auf andere Plattformen** in der App („auch im Play Store!").
- Lizenzangaben für eingebundene Bibliotheken (Apache 2.0 für Firebase-SDK und ZXing,
  siehe `LICENSE`).

---

## 7a. KI-generierte Inhalte

Stand der Recherche vom **07.09.2026**. **Keine Rechtsberatung** — die Bewertung gehört
einem Anwalt vorgelegt, bevor bezahlte Inhalte entstehen.

**Was die App tut:** Alle 80 mitgelieferten Gerichtsfotos sind KI-generiert (OpenAI,
`gpt-image-2`), **vorab** erzeugt und als Dateien ausgeliefert. **Zur Laufzeit ruft die App
keine KI**, und es gehen **keine Nutzerdaten** an OpenAI — der Schlüssel liegt nur lokal in
`.env` und wird nur von `tools/meal-bilder.py` benutzt.

Das ist der Unterschied, an dem in beiden Stores fast alles hängt: Paddy's Mealplan ist
**keine KI-App**, sondern eine App mit KI-erzeugten Bildern.

### EU AI Act (Verordnung 2024/1689), Art. 50 — seit 02.08.2026 anwendbar

| | Adressat | Trifft uns? |
|---|---|---|
| **Abs. 2** — maschinenlesbare Markierung der Ausgabe | **Anbieter** des KI-Systems (Art. 3 Nr. 3) | **Nein.** Das ist OpenAI. |
| **Abs. 4** — sichtbare Offenlegung | **Betreiber** (Art. 3 Nr. 4) | Nur bei **Deepfakes**. |

**Deepfake** nach Art. 3 Nr. 60 ist Inhalt, der „wirklichen Personen, **Gegenständen**,
Orten, Einrichtungen oder Ereignissen ähnelt und einer Person fälschlicherweise als echt
oder wahrheitsgemäß erscheinen würde“. Das Wort **Gegenständen** ist der Grund, warum die
Frage nicht so trivial ist, wie sie klingt — ein Teller Essen ist ein Gegenstand.

Die **finalen Leitlinien der Kommission** (20.07.2026) lösen das über **drei kumulative**
Kriterien: hohe Ähnlichkeit zu einem simulierten Subjekt, das Dargestellte muss
**existieren oder plausibel existieren**, und das Material muss **fälschlich als echt
erscheinen**. Rein generische Bilder ohne Bezug zu etwas Bestimmtem fallen danach
typischerweise **nicht** darunter.

**Hier muss man die beiden Bildsorten auseinanderhalten** — sie stehen rechtlich nicht
gleich:

* Die **44 Stichwortbilder** (`data/bilder.js`) sind generisch. `schnitzel.webp` springt für
  jedes Gericht ein, dessen Name das Wort trägt; es bildet kein bestimmtes Gericht ab und
  behauptet das auch nicht. Nach den drei Kriterien: **kein Deepfake.**
* Die **36 Bibliotheksbilder** (`img/library/`) gehören je einem **konkret angebotenen
  Rezept**. Das liegt näher am Produktfoto — und die Leitlinien erstrecken „Gegenstände“
  ausdrücklich auf Produkte, die ein Unternehmen verkauft. Für KI-Produktfotos wird
  überwiegend zur Kennzeichnung geraten. **Hier ist die Antwort offen**, und sie wird
  wichtiger, sobald Rezepte hinter Pro liegen.

**Was die Wettbewerbszentrale dazu sagt** — und die ist hier die praktisch wichtigste
Stimme, weil sie nicht bewertet, sondern abmahnt: Sie rät, „abstrakt ähnliche
Darstellungen“ zu kennzeichnen, „wenn betrachtende Personen sie für authentisch halten
könnten“, und zwar ausdrücklich „bis zur gerichtlichen Klärung“. Fotorealistische
Produktbilder nennt sie als Beispiel. Unsere Bilder sind fotorealistisch.

**Das ist der eigentliche Grund für die Kennzeichnung** — nicht das Bußgeld. Ein Verstoß
gegen Art. 50 gilt überwiegend zugleich als Verstoß gegen eine Marktverhaltensregel nach
§ 3a UWG. Dann können **Mitbewerber und Wirtschaftsverbände abmahnen**, ohne dass je eine
Behörde tätig wird. Höchstrichterlich geklärt ist auch das noch nicht.

Beide tragen denselben Hinweis — die Unterscheidung ändert nichts an der Umsetzung, wohl
aber daran, wie sicher die Begründung ist. Wer hier später etwas weglässt, sollte wissen,
dass er es beim zweiten Fall auf einer dünneren Grundlage tut.

**Trotzdem wird gekennzeichnet**, sichtbar an der großen Meal-Ansicht:
`Symbolbild · KI-generiert` (`bildHinweisHtml()`) — und im **Alt-Text** des Bildes
(`bildAlt()`), damit die Auskunft nicht nur bekommt, wer sehen kann. Zwei Gründe:

1. **Falls** ein Gericht „Gegenständen“ weiter auslegt, ist die Pflicht bereits erfüllt —
   und zwar am richtigen Ort. Art. 50 Abs. 5 verlangt die Angabe „klar und eindeutig,
   spätestens zum Zeitpunkt der ersten Aussetzung“; ein Hinweis, den man erst im Impressum
   findet, genügt dafür vermutlich nicht.
2. **Unabhängig vom AI Act: Irreführung nach UWG.** Das Wort *Symbolbild* sagt genau das,
   worauf es ankommt — das Gericht sieht beim Nachkochen nicht zwingend so aus. Das wird
   scharf, sobald Inhalte bezahlt sind (Pro).

Die Rückwirkungs-Ausnahme der Leitlinien (Inhalte von **vor** dem 02.08.2026 müssen nicht
nachträglich gekennzeichnet werden) hilft **nicht**: Die Bibliotheksbilder stammen vom
15.08.2026, die Stichwortbilder vom 07.09.2026.

### Google Play

Die Offenlegungspflicht für KI-Inhalte zielt auf Apps, die **zur Laufzeit** Inhalte
erzeugen (Chatbots, Bildgeneratoren) — das tut diese App nicht. Verlangt wird, dass Nutzer
ohne eigene Nachforschung erkennen können, dass KI im Spiel ist; der sichtbare Hinweis
erfüllt das. Im Store-Eintrag ist die Angabe ebenfalls zu machen, wenn zutreffend.

### Apple

Guideline **5.1.2(i)** (Stand 13.11.2025) verlangt ausdrückliche Einwilligung, wenn
**personenbezogene Daten an Dritt-KI-Anbieter** gehen. Trifft uns nicht: Es gehen keine
Nutzerdaten an OpenAI. **Diese Aussage muss stimmen bleiben** — sobald ein Feature zur
Laufzeit eine KI ruft, kippt sie, und dann sind Einwilligung, Nennung des Anbieters und
Widerruf Pflicht (dazu `docs/DATENSCHUTZ-INTERN.md`: OpenAI wäre dann Auftragsverarbeiter).

### Nutzungsrechte an den Bildern

OpenAI tritt die Rechte am Output ab („OpenAI hereby assigns to you all its right, title and
interest in and to Output“), unter dem Vorbehalt der Einhaltung der Bedingungen. Maßgeblich
sind die **Business Terms** (API-Nutzung), nicht die Consumer-„Terms of use“ von ChatGPT —
das Impressum verlinkt seit 07.09.2026 die richtigen.

**Offen:** Die Business Terms enthalten in Abschnitt 10 eine Freistellung („Copyright
Shield“) für API-Kunden, mit Ausnahmen. Deren Reichweite war nicht zu belegen —
`openai.com/policies/` weist maschinelle Abrufe mit HTTP 403 ab. **Im OpenAI-Konto
nachsehen und hier nachtragen.**

## 7b. Barrierefreiheit — BFSG

**Offen, und die Frage muss vor der Einreichung beantwortet sein.** Festgehalten am
10.09.2026 nach einem Lauf des Agenten `anwalt`.

Das Barrierefreiheitsstärkungsgesetz gilt seit dem 28.06.2025 und setzt die EU-Richtlinie
2019/882 um. Ob es für Paddy's Mealplan greift, hängt an **einer** Einordnung:

* Ist die App eine **Dienstleistung**, greift voraussichtlich die
  Kleinstunternehmer-Ausnahme (weniger als 10 Beschäftigte, höchstens 2 Mio. € Umsatz
  oder Bilanzsumme).
* Wird sie über den Vertrieb im App Store und bei Google Play als **Produkt** eingeordnet,
  greift diese Ausnahme nach den gefundenen Quellen **nicht** — sie gilt ausdrücklich nur
  für Dienstleistungen.

Greift das Gesetz, braucht es eine **Barrierefreiheitserklärung** als eigenes Dokument
neben Impressum und Datenschutzerklärung. In `data/rechtstexte.js` steht heute keine.

**Das ist eine Rechtsfrage, keine Codefrage.** Sie hängt zudem an derselben Unklarheit wie
Abschnitt 2: wer bei In-App-Käufen über die Stores Verkäufer ist.

⚠️ Die Paragraphenverweise, die dazu kursieren (§ 2 Nr. 17, § 3 Abs. 3, Anlage 3 zu
§§ 14, 28 BFSG), stammen aus nicht-amtlichen Quellen und waren am 10.09.2026 **nicht am
Primaertext prüfbar** — `gesetze-im-internet.de/bfsg/` lieferte 404. Vor Verlass darauf am
amtlichen Text nachsehen.

**Was auf der Codeseite bereits getan ist** (10.09.2026, `341a528`): Textkontrast erreicht
in Light und Dark durchgängig 4,5:1, Trefferflächen liegen bei 44 px und mehr. Das ist
**kein** Nachweis der Barrierefreiheit — Tastaturbedienbarkeit, Screenreader und
Alternativtexte sind dafür nicht geprüft.

---

## 8. Technische Mindestanforderungen

- **Startet die App ohne Netz?** Store-Prüfer testen offline. Der Service Worker und die
  lokalen `vendor/`-Dateien sind die Voraussetzung dafür.
- **Funktioniert sie ohne Anmeldung sinnvoll?** Ein Login-Gate ohne Grund vor allem Inhalt
  ist ein Ablehnungsgrund. Der lokale Modus (`authMode = "local"`) deckt das ab.
- **„Mit Apple anmelden" (Apple 4.8) — greift bereits.** Der Google-Login wird heute
  bedingungslos angeboten (`index.html:11109`), während `APPLE_ENABLED = false` steht
  (`index.html:11041`) und der Apple-Knopf dahinter verborgen ist (`:11110`). Apple verlangt
  neben einem Drittanbieter-Login eine gleichwertige datensparsame Option; „Mit Apple
  anmelden" erfüllt sie, der Google-Login allein nicht. Die Einrichtung ist laut
  `FIREBASE-SETUP.md:178` vorbereitet — es fehlen der Apple-Developer-Account und das
  Umlegen des Schalters.
- **Tablet/iPad**: Layout darf nicht brechen.

---

## 9. Stand und offene Punkte

| Punkt | Stand |
|---|---|
| Kein CDN-Code (2.5.2) | ✅ seit 23.08.2026, `vendor/` |
| Offline-Start | ✅ Service Worker, lokale SDKs |
| Nutzung ohne Konto | ✅ lokaler Modus |
| Konto-Löschung in der App | ✅ vorhanden, bei Änderungen nachprüfen |
| Pro-Gating serverseitig | 🟡 **nur zur Hälfte** — Gruppe ja, Auto-Planer nur im Client. Am 26.08.2026 bewusst so entschieden |
| Kaufbeleg-Prüfung | 🔴 nicht vorhanden; braucht Cloud Functions und damit **Blaze statt Spark** |
| „Mit Apple anmelden" (4.8) | 🔴 **fehlt**, obwohl Google-Login aktiv ist |
| „Wiederherstellen" | 🔴 fehlt (existiert erst mit dem ersten Kauf) |
| **Bezahlweg (Apple 3.1.1)** | 🟡 **entschieden: Abo** (26.08.2026) — zu bauen: StoreKit + Play Billing |
| **Kaufbeleg serverseitig prüfen** | 🔴 zu bauen — Cloud Function, setzt den Blaze-Wechsel voraus |
| Nutrition Labels / Data Safety | 🟡 Datengrundlage steht (Abschnitt 5), Formulare nicht ausgefüllt |
| `NSCameraUsageDescription` | 🟡 zu prüfen, sobald das Capacitor-Projekt existiert |
| **Barrierefreiheit (BFSG)** | 🔴 **ungeklärt, ob das Gesetz greift** — Dienstleistung oder Produkt? Erklärung fehlt. Abschnitt 7b |

**Nicht aus diesem Repo prüfbar:** alles, was in App Store Connect, der Play Console oder
im Capacitor-Projekt steht.
