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

Die App ist heute eine Web-App: eine `index.html`, ausgeliefert über GitHub Pages unter
`www.paddysmealplan.de`. Für die Stores wird sie mit **Capacitor** verpackt.

**Der entscheidende Punkt beim Verpacken:** Die App muss **lokal** ausgeliefert werden und
ohne Netz starten. Ein Wrapper, der nur `www.paddysmealplan.de` in einem WebView anzeigt,
trifft gleich zwei Ablehnungsgründe — Apple 4.2 („minimale Funktionalität", eine Website
in einer Hülle) und 2.5.2 (Code aus dem Netz).

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
| **Auto-Wochenplaner** — laut `docs/PRODUCT.md` „das entscheidende Pro-Feature" | **Nur im Client.** `if (!isPro() && !syncGid)` in `index.html:12567` |

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

## 8. Technische Mindestanforderungen

- **Startet die App ohne Netz?** Store-Prüfer testen offline. Der Service Worker und die
  lokalen `vendor/`-Dateien sind die Voraussetzung dafür.
- **Funktioniert sie ohne Anmeldung sinnvoll?** Ein Login-Gate ohne Grund vor allem Inhalt
  ist ein Ablehnungsgrund. Der lokale Modus (`authMode = "local"`) deckt das ab.
- **„Mit Apple anmelden" (Apple 4.8) — greift bereits.** Der Google-Login wird heute
  bedingungslos angeboten (`index.html:14941`), während `APPLE_ENABLED = false` steht
  (`index.html:14873`) und der Apple-Knopf dahinter verborgen ist (`:14942`). Apple verlangt
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

**Nicht aus diesem Repo prüfbar:** alles, was in App Store Connect, der Play Console oder
im Capacitor-Projekt steht.
