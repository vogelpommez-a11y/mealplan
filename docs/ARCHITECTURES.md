# ARCHITECTURES.md

# Architektur von Paddy's Mealplan

Dieses Dokument beschreibt die technische Struktur, Datenflüsse, Persistenz und bewusst beibehaltenen Architekturentscheidungen.

<!-- REGISTER-ANFANG (erzeugt aus den Ueberschriften, nicht von Hand pflegen) -->

**Register — 25 Abschnitte.** Wo welcher Teil des Systems beschrieben ist.

| # | Abschnitt |
|---|---|
| · | Grundstruktur |
| · | Struktur von `index.html` |
| · | HTML-Grundgerüst |
| · | Fehlermelder `window.noteError` (Aufgabe A7) |
| · | Zwei-Script-Architektur |
| · | Brücke zwischen Firebase und App |
| · | Graceful Fallback |
| · | State |
| · | Cloud-Synchronisation |
| · | Gruppenmodus |
| · | Mitgliederlimit: `memberCount` (16.08.2026) |
| · | Gruppen-Wochenplan |
| · | Gerichte-Zuweisung (Gemeinsam planen) |
| · | Wichtige Gruppen-Sync-Regeln |
| · | Rollen |
| · | Datenmodell und Datenschutz |
| · | Firebase Security |
| · | Namensdualität |
| · | Bilder |
| · | Wochenplan auf dem Handy |
| · | Zurück-Taste und Overlay-Stapel (D5, 23.08.2026) |
| · | Meal-Ansicht: eine Oberfläche statt zweier (`openMealSheet`) |
| · | Auto-Wochenplaner (D2, 16.08.2026) |
| · | Einkaufsliste: der Abhak-Zustand hängt an der Woche (28.08.2026) |
| · | Architekturprinzip |

<!-- REGISTER-ENDE -->

## Grundstruktur

Die App besteht aus einer einzigen:

`index.html`

Sie enthält:

* HTML
* CSS
* Firebase-Modul
* App-JavaScript
* Meal-/Fotodaten
* Rechtstexte

Es gibt keinen Build-Prozess.

Es gibt aktuell:

* keinen Bundler
* kein `package.json`
* kein npm
* kein Test-Framework
* keinen Linter

Firebase wird vom CDN geladen.

## Struktur von `index.html`

Seit dem 29.08.2026 ist die App **nicht mehr eine einzige Datei**. Ausgeliefert werden
weiterhin statische Dateien ohne Build; der Code liegt nur auf mehrere davon verteilt.

| Datei | Inhalt |
|---|---|
| `css/tokens.css` | Design-Tokens, alle vier Theme-Blöcke |
| `css/basis.css`, `css/komponenten.css`, `css/mobil.css` | das übrige UI-System |
| `lib/basis.js` | `window.PM` mit `esc()` und `el()` |
| `data/*.js` | `ICONS`, `PHOTOS`/`PHOTO_CREDITS`, `COOKBOOK`, `FOODS`, Rechtstexte |
| `lib/pdf.js`, `lib/barcode.js` | PDF-Schreiber und Barcode-Infrastruktur |
| `index.html` → `type="module"` | Firebase und Cloud-Abstraktion |
| `index.html` → normales `<script>` | Markup und der verwobene App-Kern (eine IIFE) |

**Die Reihenfolge der Einbindung ist Architektur.** Es sind klassische Skripte, keine
ES-Module: sie laufen synchron in Dokumentreihenfolge, sodass alle Konstanten und
Fassaden bereitstehen, bevor die App-IIFE geparst wird. ES-Module scheiden aus, weil sie
über `file://` nicht laden — und genau darauf bauen Smoke-Test und Prüfstände auf.

**Warum der Kern zusammenbleibt:** `state`, Persistenz, Cloud-Sync, Views, Meal-Sheet,
Einkaufsliste, Auto-Planer, Onboarding und Gruppe teilen sich `state`, `save()`,
`render()`, `toast()` und die Sanitizer-Kette. Ausgelagert wurde nur, was **gemessen**
keine Kernfunktion aufruft. Das ist eine Eigenschaft des Codes, keine Geschmacksfrage.

Zeilennummern sind grobe Orientierung und keine stabile API. Die aktuelle Zuordnung von
Bereich zu Datei und Zeilenbereich steht **erzeugt** in `docs/MODULE.md`
(`python tools/karte.py`). Bei Änderungen immer mit `Grep` nach konkreten Markern suchen —
und über **alle** Code-Dateien, nicht nur `index.html`.

## HTML-Grundgerüst

Folgende Elemente sind architektonisch relevant:

* `#view` — zentraler App-Inhalt
* `.site-foot` — Footer, auch ohne Login sichtbar
* `legalModal` — Impressum/Datenschutz
* `.wg-progress-bar` — Standard-Fortschrittsanzeige für mehrstufige Abläufe

`<meta charset>` und `<meta name="viewport">` dürfen nicht entfernt werden.

## Fehlermelder `window.noteError` (Aufgabe A7)

Steht als Erstes im **ersten** `<script>`-Block, noch vor dem Theme-Code, und ist damit in allen
späteren Blöcken verfügbar — auch im Firebase-Modul.

```js
noteError("group:dissolve", e);   // Kennung "bereich:aktion", dann der Fehler
noteError.dump();                 // die letzten 50 Fälle, für die DevTools
```

Vorher standen an 34 Stellen leere `catch (e) {}`. Was das kostet, steht in
`docs/TROUBLESHOOTING.md` §29: ein verschluckter `TypeError` ließ „Gruppe auflösen" monatelang
nie wirklich aufräumen, ohne dass irgendwo etwas auffiel.

**Eigenschaften, die keine Details sind:**

* **Gedrosselt** — pro Kennung höchstens 3 Meldungen, insgesamt 50 im Ringpuffer. Ohne das
  würden Sync-Listener und Schleifen (`getTracks().forEach(t => t.stop())`) den Puffer fluten
  und wertlos machen.
* **Kein Versand.** Ein Telemetrie-Dienst wäre ein Empfänger personenbezogener Daten und müsste
  in die Datenschutzerklärung. Kommt Store-Telemetrie (Plan D), ist **diese Funktion die eine
  Stelle** dafür — dann aber mit Rechtstext-Prüfung.
* **Kein `localStorage`.** Fehlermeldungen können Nutzerinhalte tragen; im Speicher gehalten
  sind sie mit dem Tab weg.
* **Wirft nie selbst**, auch nicht bei `noteError()` ohne Argumente oder einem zirkulären Objekt.
* Heißt bewusst **nicht** `reportError`: `window.reportError` ist eine echte Plattform-API.

**Warum die Position kritisch ist:** Ein leerer `catch` war unzerstörbar. Ein `catch` mit
`noteError()` darin ist es nicht mehr — fehlte die Funktion, legte **jede einzelne** dieser
Stellen einen `ReferenceError` nach und bewirkte das Gegenteil.

*(Hier stand bis zum 27.08.2026 „jede der 38 Stellen". Es waren zu dem Zeitpunkt längst 54 —
eine feste Zahl in einem Fließtext altert still, und niemand zählt nach. Deshalb steht hier
jetzt keine mehr. Wer die aktuelle braucht: `grep -c 'noteError("' index.html`.)* Der Melder darf deshalb nie hinter etwas
rutschen, das vorher scheitern kann, und nichts nachladen.

**Eine Stelle bleibt bewusst leer:** `navigator.share(...).catch(() => {})`. Bricht der Nutzer
das Teilen-Blatt ab, kommt ein `AbortError` — Normalbetrieb, kein Fehler.

**Nachtrag 27.08.2026 — ein freundlicher Toast ist auch ein Schlucken.** Der Melder deckte die
*leeren* `catch`-Blöcke ab, nicht die, die den Fehler in eine Nutzermeldung übersetzen und ihn
damit genauso verlieren. Drei Cloud-Pfade waren betroffen und haben jetzt ihre Kennung:

| Kennung | Wo | Was der Nutzer sieht |
|---|---|---|
| `group:switch` | Gruppe laden/wechseln | „Die Gruppe ist gerade nicht erreichbar …" |
| `sync:recipes` | Rezept-Batch in die Cloud | „Deine Meal-Fotos konnten gerade nicht …" |
| `save:localStorage` | `save()` schlägt fehl | „Der Speicher dieses Geräts ist voll …" |

Der Nutzen zeigte sich sofort: Beim ersten Lauf über `localhost` meldete `group:switch` die
Ursache, die vorher niemand sehen konnte — **„Missing or insufficient permissions."**, also ein
Firestore-Regelfall und kein Netzproblem. Genau diese Unterscheidung nimmt der Toast dem
Leser ab.

Weitere ~28 `catch`-Blöcke übersetzen ebenfalls in einen Toast (Teilen, PDF, Zwischenablage,
Einladungen). Sie sind **nicht** angefasst: Dort ist die Ursache aus der Aktion heraus meist
offensichtlich, und das Minimalprinzip gilt auch für Verbesserungen. Wer dort einmal im Dunkeln
steht, weiß jetzt, wo das Muster steht.

## Zwei-Script-Architektur

### Firebase-Modul

Das `type="module"`-Script läuft vor dem eigentlichen App-Script.

Es importiert Firebase v10 **aus dem Repo** (`vendor/firebase/10.12.5/`, drei ES-Module) und
stellt über `window` folgende Schnittstellen bereit:

### Firebase liegt lokal, nicht auf gstatic

Seit dem 23.08.2026 lädt das SDK nicht mehr von `https://www.gstatic.com/firebasejs/…`, sondern
aus `vendor/firebase/10.12.5/` — dieselbe Ablage wie `vendor/zxing.min.js`. Zwei Gründe:

* **Apple 2.5.2.** Eine App darf keinen ausführbaren Code aus dem Netz nachladen. Solange das
  SDK vom CDN kam, wäre das im Review angreifbar gewesen.
* **Kaltstart ohne Netz.** Der Service Worker reicht fremde Hosts absichtlich durch. Ohne
  Verbindung kam das SDK also nie an, und der Cloud-Nutzer landete nach 6 Sekunden Timeout im
  lokalen Modus — mit lokalem SDK startet die Anmeldung sofort.

Gepflegt wird der Ordner über `tools/firebase-vendor.py` (Version als Argument). Das Skript
schreibt genau **einen** Pfad um: In `firebase-auth.js` und `firebase-firestore.js` zeigt der
Import von `firebase-app.js` auf die absolute gstatic-URL. Bliebe der stehen, hätte die Seite
zwei App-Instanzen — eine lokale und eine nachgeladene — mit getrennten Komponenten-Registern,
und `getAuth(app)` fände seine App nicht mehr. Die gleichlautenden Strings **innerhalb** von
`firebase-app.js` sind dagegen Komponentennamen, keine Ladepfade, und bleiben unangetastet.

Nicht lokalisierbar bleibt der OAuth-Popup-Weg: `signInWithPopup` öffnet ein iframe unter
`https://paddys-mealplan.firebaseapp.com/__/auth/…`. Das ist Google-Infrastruktur, kein
Bundle — es verschwindet erst mit dem nativen Login aus D7.

### `window.CloudAuth`

Verantwortlich für:

* Registrierung
* E-Mail-Login
* Google-Login
* Bestätigungsmail
* Passwort-Reset

### `window.CloudSync`

Verantwortlich für:

* `load`
* `save`
* `watch`
* `wipeCache` — löscht den Firestore-Offline-Cache (siehe „Firestore-Offline-Cache" unten)

Cloud-Rezeptfunktionen arbeiten mit einem Basispfad, z. B.:

`["users", uid]`

oder:

`["groups", gid]`

Sie erwarten nicht einfach eine UID.

### `window.CloudShare`

Verantwortlich für:

* `publish`
* `fetch`

Daten liegen unter:

`shared/{id}`

### Meal teilen

Standardweg ist `shareRecipeNow(recipeId)`: ein Tipp, danach direkt das native Share-Sheet (`shareLink()`, analog `shareShopPdf()`/`shareFileOrText()`). Voraussetzung sind eine echte Cloud-Anmeldung (`CloudShare.enabled && authMode === "cloud"` — `enabled` allein sagt nur, dass Firebase konfiguriert ist) und `canShare()` (Gerät hat `navigator.share`); sonst öffnet weiterhin das Modal `openShareRecipe()` mit „Meal-Link erstellen" und Zwischenablage. Kein zusätzlicher Teilen-Knopf im Modal: sobald `openShareRecipe()` erfolgreich einen Link erzeugt (`createdUrl`), ist die Cloud-Anmeldung damit belegt — dann hätte `shareRecipeNow()` bei zugleich vorhandenem `canShare()` direkt den nativen Weg genommen und das Modal nie geöffnet. Der Zustand „Link fertig + `canShare()`" ist also unerreichbar (siehe ROADMAP, Opus-Nachprüfung zu Commit `0c9a3cd`).

`CloudShare.publish()` läuft bewusst ohne `await` parallel zu `shareLink()`, siehe `docs/TROUBLESHOOTING.md` Ziffer 40. `state.shares` wird erst ergänzt, wenn `publish()` erfolgreich war — unabhängig davon, ob der Nutzer das Share-Sheet danach abbricht oder durchführt.

### Link-Vorschau in Messengern (Cloudflare Worker, `worker/og.js`)

`shareMealPayload()` schreibt zusätzlich ein schlankes `og`-Feld (`{ t: r.name, img: … }`) nach `shared/{id}`. Bei einem **eigenen Foto** bleibt `og.img` bewusst `null` — der Base64-String steckt bereits in `recipes[0].image` desselben Payloads, ein zweiter Eintrag würde ihn verdoppeln und unnötig gegen die 400-KB-Payload-Grenze drücken (Firestore lehnt `undefined` im Dokument ab, deshalb `null` und kein weggelassenes Feld). Nur ohne eigenes Foto trägt `og.img` direkt den `PHOTOS`-Pfad aus `photoFor(r)` (z. B. `img/pasta.webp`). Der Worker liest bei `og.img === null` stattdessen `recipes[0].image`. `applySharedData()` ignoriert das `og`-Feld beim Import, `firestore.rules` bleibt unverändert (zusätzliche Felder sind bei `create` erlaubt).

**Stand:** `worker/og.js` liegt im Repo, ist aber **noch nicht deployt**. `CNAME` zeigt weiterhin direkt auf `vogelpommez-a11y.github.io`, keine Cloudflare-Nameserver aktiv — geteilte Links zeigen bis zur Infrastruktur-Umstellung weiterhin die generische Karte. Deployt wird ausschließlich über das Cloudflare-Dashboard (Domain bei Cloudflare aufnehmen, Nameserver umstellen, Worker-Route `www.paddysmealplan.de/*`, Service-Account-Secret hinterlegen — siehe `plans/TeilenVereinheitlichen.MD` Teil B3), GitHub Pages bleibt Ursprung und liefert weiterhin dasselbe statische `index.html` aus.

Nach dem Deployment gilt:

* Anfragen mit `?s=<id>` laufen unverändert zu GitHub Pages durch, der Worker ersetzt danach per `HTMLRewriter` nur `og:title`, `og:description`, `og:image`, `og:url` und `twitter:*` im HTML. Kein User-Agent-Sniffing, Crawler und Mensch bekommen dasselbe HTML.
* `/og/<id>.jpg` liest `shared/{id}` per Firestore-REST-API und liefert `og.img` aus (Base64 dekodiert oder als Pfad an GitHub Pages weitergereicht), Fallback ist `img/neutral.jpg`.
* Der Worker liest `shared/{id}` über einen **Service-Account** (Rolle nur `Cloud Datastore Viewer`), nicht über die App — die Firestore-Regel `allow get: if request.auth != null` (`firestore.rules` Zeile 62) bleibt unverändert. Der Zugriffs-Token entsteht per JWT-Bearer-Flow (RS256, `crypto.subtle`), der private Schlüssel liegt nur als Worker-Secret (`GCP_SA_PRIVATE_KEY`), nicht im Repo.
* Jeder Fehler im Worker (Firestore nicht erreichbar, unbekannte ID, abgelaufenes Secret) fällt still auf die unveränderte GitHub-Pages-Antwort zurück — der Worker darf die App nie blockieren.

**Nach dem Deployment** verarbeitet Cloudflare die IP-Adressen aller Besucher der gesamten Seite, nicht nur der `?s=`-Links, und `/og/<id>.jpg` liefert ein Meal-Foto ohne Anmeldung aus. Das berührt die Datenschutzerklärung (Cloudflare als Auftragsverarbeiter, Hinweis auf die anmeldungsfreie Vorschau) — **erst mit dem Deployment aktualisieren, nicht vorher**, sonst beschreibt der Rechtstext einen Zustand, der noch nicht existiert. Vorher (und danach erneut) `anwalt` und `website-security` einsetzen.

### `window.CloudGroup`

Verantwortlich für:

`groups/{gid}`

mit:

* `members/{uid}`
* `plans/{weekKey}`
* `recipes/{rid}`
* `invites/{code}`

Das Gruppendokument selbst trägt `status: "pending" | "active"` (rein informativ, siehe Wartezustand unten) sowie `name` (per `setName`) und `settings`.

### Firestore-Offline-Cache

**Beim Kontowechsel wird er geleert** (`kontoWechselAufraeumen()`, 29.08.2026). Der Cache liegt
pro **Ursprung**, nicht pro Konto — ein zweites Konto auf demselben Gerät trifft also auf den
Cache des ersten. Genau dort war der Zustand aus `docs/TROUBLESHOOTING.md` 134 messbar, in dem
jeder Zugriff dauerhaft `permission-denied` liefert. Reihenfolge zwingend: **merken, wischen,
neu laden** — umgekehrt entstünde eine Neulade-Schleife. Als Ausweg von Hand gibt es zusätzlich
„Einstellungen → Cloud-Verbindung zurücksetzen".

`db` wird über `initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) })` initialisiert, nicht mehr über das flüchtige `getFirestore(app)`. Der Cache spiegelt Wochenplan, Meals und Gruppendaten in IndexedDB, damit die App nach einem Kaltstart ohne Netz nutzbar bleibt (Wochenplan im Supermarkt, Einkaufsliste im Keller). Der Multi-Tab-Manager ist Pflicht — ohne ihn schaltet ein zweiter geöffneter Tab die Persistenz für beide Tabs stillschweigend ab.

Die Initialisierung sitzt in einem eigenen `try/catch` mit Fallback auf `getFirestore(app)`: sie steckt mitten im großen `try`-Block, dessen `catch` `cloudauth:disabled` wirft und damit die **gesamte** Cloud-Anmeldung deaktiviert (siehe „Graceful Fallback" oben). Scheitert die Persistenz allein (Privatmodus ohne IndexedDB, exotische WebView), darf das nicht die ganze Cloud kosten — Persistenz ist ein Komfortgewinn, keine Voraussetzung.

**Wichtigste Konsequenz: `fromCache` ist kein Beweis.** Mit dem flüchtigen Cache warf `getDoc`/`getDocs` offline zuverlässig — erkennbar als Fehler. Mit Persistenz liefern beide still den letzten bekannten Stand aus IndexedDB, kenntlich nur über `snap.metadata.fromCache`. `CloudGroup.fetch()` und `fetchMembers()` geben dieses Flag deshalb mit zurück (`{ data, fromCache }` bzw. `{ members, fromCache }`), `watchMembers()` reicht es als zweiten Callback-Parameter durch. `enterGroupSync()` leitet aus einem `fromCache`-Ergebnis **nie** `"gone"` ab, sondern `"error"` — siehe „Drei Zustände statt true/false" unten, ausführlicher Fehlerfall in `docs/TROUBLESHOOTING.md`.

**Löschung:** `CloudSync.wipeCache()` ruft `terminate(db)` gefolgt von `clearIndexedDbPersistence(db)` — Reihenfolge zwingend, `clearIndexedDbPersistence()` verlangt eine beendete Instanz. `wipeLocalData()` ruft das als letzten Schritt auf, nach `localStorage` und der Bild-IndexedDB. Seitdem kann `wipeLocalData()` erstmals fehlschlagen; alle drei Aufrufer (`deleteAccountFlow()` beide Zweige, `deleteLocalDataFlow()`) fangen den Fehler mit einer ehrlichen Meldung ab, statt „gelöscht" zu behaupten und neu zu laden.

## Brücke zwischen Firebase und App

Die beiden Scripts teilen sich grundsätzlich keine direkte Implementierung.

Es gibt **zwei** definierte Brücken:

| Brücke | Wer ruft | Wer empfängt |
|---|---|---|
| `window.__onCloudAuth(user)` | Firebase aus `onAuthStateChanged` | `handleCloudUser()` |
| `window.__onCloudWatchError(kennung, e)` | `watchFehler()` aus jedem `onSnapshot`-Fehler | setzt `setSyncStatus("offline")` und meldet einmal je Sitzung |

Die zweite kam am 28.08.2026 dazu (`docs/TROUBLESHOOTING.md` 129) und ist bewusst nach
demselben Muster gebaut: Das Modul kennt die App nicht, es ruft nur eine Funktion, wenn es sie
gibt.

Die App setzt sie auf:

`handleCloudUser`

Änderungen an Authentifizierung müssen daher immer beide Seiten dieser Brücke berücksichtigen.

`handleCloudUser` unterscheidet:

1. verifizierter User → `enterApp`
2. unverifizierter User → `renderVerifyPending`
3. kein User → `renderAuthCloud`

## Graceful Fallback

Die App muss auch ohne funktionierendes Firebase starten.

Wenn:

* `firebaseConfig` Platzhalter enthält
* das Firebase-CDN nicht erreichbar ist
* der Cloud-Start innerhalb des vorgesehenen Timeouts scheitert

fällt die App auf den lokalen Login zurück.

Relevante Zustände:

* `authMode = "local"`
* `authMode = "cloud"`

Lokaler Modus:

* Profil in `localStorage`
* kein Cloud-Sync

Dieser Fallback ist absichtlich Teil der Architektur und darf nicht versehentlich entfernt werden.

## State

Zentraler App-State:

`state = { recipes, plan, tab }`

Lokale Persistenz:

`wochenkueche_v1`

über:

* `load()`
* `save()`

### Getrennter Schlüsselraum für die Testumgebung

`localStorage` hängt an der Origin, die Cloud nicht: `http://localhost:8000` und
`https://www.paddysmealplan.de` sind zwei getrennte lokale Speicher, melden sich aber am
**selben** Firebase-Projekt mit derselben UID an. Ein lokaler Teststand schrieb dadurch in die
echte Cloud — und weil `mergeRemoteRecipes()` ein nur lokal vorhandenes Meal als „neu, noch
nicht hochgeladen" wertet, tauchten dort längst gelöschte Meals wieder auf.

Deshalb bekommen alle lokalen Schlüssel in der Testumgebung das Suffix `__test`, vergeben über
`localKey()`:

* `STORE_KEY`
* `PROFILE_KEY`
* `LAST_KEY`
* `SHOP_DONE_KEY`
* IndexedDB-Datenbank `mealplan-media`

Nicht betroffen ist `THEME_KEY` — eine reine Anzeigeeinstellung, die beim Testen absichtlich
mit der Live-Ansicht übereinstimmt; außerdem liest das Anti-Flimmer-Script im `<head>` denselben
Schlüssel, bevor `localKey()` überhaupt existiert.

**`isTestOrigin()` prüft bewusst nicht nur den Hostnamen.** Capacitor läuft selbst unter
`localhost` (Android `https://localhost`, iOS `capacitor://localhost`). Ein reiner Hostname-Test
würde die spätere App-Store-Fassung als Testumgebung einstufen und ihr die Daten des Nutzers
entziehen. Testumgebung ist daher nur `file:` oder `http:` **in Verbindung mit** einem lokalen
Hostnamen, zusätzlich abgesichert über `window.Capacitor`.

Auf der Live-Domain bleiben alle Schlüssel zeichengleich — bestehende Daten und alte
Sharing-Links dürfen nicht brechen (siehe Namensdualität).

### `wipeLocalData()` deckt beide Speicher ab

Seit die Meal-Fotos und das Profilbild in IndexedDB liegen (Paket A3) und nicht mehr im
`localStorage`-JSON, reicht das Entfernen der localStorage-Schlüssel nicht mehr aus.
`wipeLocalData()` ist deshalb `async` und räumt:

* `STORE_KEY`, `PROFILE_KEY`, `LAST_KEY`, `SHOP_DONE_KEY`
* den ObjectStore `images` der IndexedDB
* die Baseline `imgSaved`

Ohne den IndexedDB-Teil holte `hydrateImages()` nach dem Neustart `map.__profile__` wieder in
den State (`if (!state.profileImage && map.__profile__)`) — ein direkt danach neu registriertes
Konto hätte das Profilbild erneut in die Cloud geschrieben.

`store.clear()` statt `indexedDB.deleteDatabase()`: eine gewöhnliche Transaktion, die nie
blockiert. `deleteDatabase()` wartet auf das Schließen **jeder** offenen Verbindung — `idbOpen()`
hält genau so eine — und bliebe still in `onblocked` hängen.

Alle drei Aufrufer (`await wipeLocalData()`) warten das ab, bevor sie den Reload planen.

Das ist keine Kosmetik: Ziffer 10 der Datenschutzerklärung sagt wörtlich „sämtliche auf diesem
Gerät gespeicherten Daten sofort entfernen".

Bekannte Grenze: Ein Zugriff über die LAN-IP (`http://192.168.x.y`) gilt **nicht** als
Testumgebung. `test-server.ps1` bindet ohnehin nur an `localhost`, der Fall kann mit dem
mitgelieferten Server nicht auftreten.

## Cloud-Synchronisation

### Ein abgerissener Listener meldet sich (`watchFehler`, 28.08.2026)

Alle fünf `onSnapshot`-Aufrufe (`CloudSync.watch`/`watchRecipes`, `CloudGroup.watch`/
`watchPlans`/`watchMembers`) tragen einen gemeinsamen Fehlermelder. Er protokolliert über
`noteError` und reicht den Fall über `window.__onCloudWatchError` an die App — dieselbe
Brücken-Bauart wie `window.__onCloudAuth`. Die App setzt daraufhin `setSyncStatus("offline")`
und meldet **einmal je Sitzung** (`watchAbgerissen`, in `stopCloudSync()` zurückgesetzt).

**Warum das nötig ist:** Ein `onSnapshot`, der mit einem Fehler endet, wird von Firestore
ENDGÜLTIG beendet — er versucht es nicht erneut. Vier dieser Listener trugen ein leeres
`function () {}`; der Status blieb deshalb auf dem `"synced"` vom Ende des `startCloudSync()`
stehen, auch wenn nichts mehr ankam. Am 28.08.2026 war genau das messbar. Bewusst **kein**
automatisches Neuanhängen: Ein Listener, der an einer Regel scheitert, scheitert erneut, und
eine Wiederanhänge-Schleife wäre Dauerfeuer. `docs/TROUBLESHOOTING.md` 129.


Im Cloud-Modus schreibt `save()` den State über:

`scheduleCloudPush()`

mit einem Debounce von ca. 800 ms.

Live-Synchronisation erfolgt über `onSnapshot`.

Zur Vermeidung von Endlosschleifen werden insbesondere berücksichtigt:

* `hasPendingWrites`
* JSON-Vergleich
* `tab` wird nicht als Cloud-Änderung behandelt

### `canonJSON` — die einzige Serialisierung für Sync-Vergleiche

Firestore liefert Map-Schlüssel bei jedem Snapshot **sortiert** zurück, lokal gebaute Objekte
entstehen dagegen in Code-Reihenfolge. `JSON.stringify` ist reihenfolgeabhängig — ohne eine
kanonische Form vergleicht der Sync strukturell nie stabil, unabhängig von der Merge-Reihenfolge
aus Ziffer 34 in `docs/TROUBLESHOOTING.md` (dort war es Einfüge- statt Objektschlüssel-Reihenfolge,
hier ist es dieselbe Fehlerklasse an der Wurzel: zwei gültige Zeichenketten für denselben Inhalt).

`canonValue(v)`/`canonJSON(v)` sind die gemeinsame Antwort: Arrays bleiben unangetastet (Reihenfolge
ist dort inhaltlich, siehe `unionIds()`/`sanitizeTombstones()`), Objektschlüssel werden rekursiv
sortiert. **Regel: `canonJSON` vergleicht nur, es schreibt nie.** Eine kanonisierte Kopie in die
Cloud zu schreiben wäre selbst wieder eine dritte, neue Reihenfolge und verschöbe das Problem nur.

Alle Vergleichsstellen im Sync laufen darüber:

* `dataJSON()` (Kontodokument, `onRemote()`/`pushNow()`)
* `syncRecipes()` (Rezept-Subcollection, Baseline `lastPushedRecipes`)
* `onRecipesRemote()` (eingehende Rezept-Änderungen)
* `pushGroupPlan()`/`onGroupPlansRemote()` (Gruppen-Wochenplan-Slots, Baseline `lastPushedSlots`)

Jede Schreibstelle liest den **Rohwert**, nie den Vergleichsstring zurück (`puts.push(r)` statt
`JSON.parse(canonJSON(r))`, `mark(wk, field, flat[field])` statt `JSON.parse(json)`) — sonst
verlöre ein Schreibvorgang die eigentliche Absicht der Sortierung nur zum Vergleich.

Zwei Werte gehören **nie roh** in einen Push, auch wenn sie inhaltlich stimmen:

* **Berechnete Werte.** `shopPersons()` hängt an `groupMembers.length`/`"shopForAll"` und ist ein
  abgeleiteter Anzeigewert, keine Kontoeinstellung. `pushNow()`/`save()` schreiben stattdessen
  `sanitizeShopPersons(state.shopPersons)` — sonst überschriebe der berechnete Wert eine bewusst
  auf 1 gesetzte Zahl dauerhaft, und weil er sich je nach Gruppenzustand pro Gerät unterschiedlich
  berechnet, wäre er zugleich selbst wieder eine Endlos-Schreib-Quelle.
* **Merge-Ergebnisse ohne abschließende Sortierung.** `state.weightGoals = sanitizeWeightGoals(
  Object.assign({}, sanitizeWeightGoals(a), sanitizeWeightGoals(b)))` — sowohl innen als auch
  außen sanitizen: nur außen ließe einen ungültigen Remote-Wert ein gültiges lokales Zielgewicht
  überschreiben, das danach beim äußeren Sanitize-Durchlauf herausgefiltert würde — das Ziel wäre
  verloren, nicht nur unsortiert. `mergeTombstones()` sortiert ebenfalls seine eigene Rückgabe.

## Gruppenmodus

Wenn `syncGid` gesetzt ist, stammen:

* Wochenplan
* Meals

aus der Gruppe.

Persönliche Daten bleiben am eigenen Konto, insbesondere:

* `goal`
* `weights`
* `weightGoals`
* `weightConsent`
* `profileImage`
* `onboarded`

Dadurch können Personen denselben Plan verwenden, aber unterschiedliche persönliche Kalorienziele haben.

Ein Konto gehört höchstens einer Gruppe.

Die Gruppe wird über:

`groupId`

im eigenen `users/{uid}`-Dokument gefunden.

### Wartezustand (zweistufiger Start)

Eine Gruppe wird nicht mehr sofort scharf geschaltet. `prepareGroup()` legt `groups/{gid}` an (`status: "pending"`), lädt eigene Meals/Wochenpläne vorab hoch und erzeugt direkt den Einladungslink. Dabei bleibt `state.groupId` leer — `users/{uid}.pendingGroupId` trägt die vorbereitete Gruppen-ID, `users/{uid}.pendingInviteUrl` den Einladungslink. Der Owner plant bis zum Beitritt unverändert in seinen eigenen Daten weiter; `startCloudSync()` läuft dadurch im Einzelkonto-Zweig, ohne Sonderbehandlung.

**Der Beitretende bringt seine Woche mit (`mergeOwnPlanIntoGroup()`, 28.08.2026).**
`enterGroupSync()` ersetzt `state.plans` durch den Gruppenplan; hochgeladen wurde der eigene
Plan bis dahin nur beim Owner — die Woche des Beitretenden war lautlos weg. Nachgetragen
werden ausschließlich Slots, die in der Gruppe **noch leer** sind (die Owner-Regel aus
`finalizeGroupActivation()`, jetzt für beide Seiten aus **einer** Funktion). Reihenfolge
zwingend: erst `copyOwnRecipesToGroup()` (biegt die Planverweise auf die Gruppen-ids um),
dann der Plan. Gelesen wird über `CloudGroup.loadPlansFromServer()`; scheitert das Lesen,
wird **nichts** geschrieben — strenger als beim Meal-Abgleich, weil der Schaden hier die
gelöschte Woche der anderen Person wäre. `docs/TROUBLESHOOTING.md` 128.

**`dedupeAgainstCatalog()` läuft in einer Gruppe gar nicht** (`if (syncGid) return;`, ohne
das Flag zu setzen). `state.dedupeV1` steht nur im `localStorage` und ist damit ein
Geräte-Flag — in der Gruppe räumte die Migration aber den gemeinsamen Bestand auf, und jedes
weitere Gerät ließ sie erneut darauf los. Nach dem Verlassen holt sie es auf dem eigenen
Bestand sofort nach.

Aktivierung (`finalizeGroupActivation()`) läuft auf zwei Wegen:

* **Live:** ein schlanker `CloudGroup.watchMembers()`-Listener (`watchPendingGroup()`), solange `pendingGroupId` gesetzt ist. Sobald `members.length > 1`, trägt sie neue/gelöschte Meals und noch leere Wochenplan-Slots nach (belegte Slots der beigetretenen Person werden nicht überschrieben), setzt `status: "active"` und `users/{uid}.groupId`, danach `switchGroup()`.
* **Beim Start:** `startCloudSync()` prüft `remote.pendingGroupId` einmalig über `fetchMembers()`, *bevor* `wantGid` ermittelt wird — gelingt die Aktivierung, wird `remote.groupId` im selben Durchlauf gesetzt und über `enterGroupSync()` normal eingelesen (kein rekursiver `switchGroup()`-Aufruf aus einem laufenden `startCloudSync()` heraus). Deckt ab, dass der Owner offline war, als jemand beitrat.

„Einladung zurückziehen“ im Wartezustand (`withdrawPendingInvite()`) löst die vorbereitete Gruppe vollständig auf (`dissolveGroupFirestore()`, auch von `dissolveGroup()` für aktive Gruppen genutzt) und leert `pendingGroupId`/`pendingInviteUrl` — danach ist der Zustand identisch zu vor dem Einladen.

**Der Dubletten-Abgleich beim Beitritt liest vom SERVER, nicht aus dem Cache (28.08.2026).**
`copyOwnRecipesToGroup()` entscheidet anhand eines LEEREN Leseergebnisses, ob ein eigenes Meal
hochgeladen wird — und `getDocs()` liefert mit `persistentLocalCache` offline stillschweigend
ein leeres Ergebnis, statt zu werfen. Die Rezepte einer gerade erst beigetretenen Gruppe hat
der Cache aber noch nie gesehen. Deshalb `CloudSync.loadRecipesFromServer()`
(`getDocsFromServer`): Die wirft offline, und genau das erlaubt dem Aufrufer, „leer“ von
„unbekannt“ zu unterscheiden. Fällt sie aus, bleibt es beim alten Verhalten (alles hochladen).
`docs/TROUBLESHOOTING.md` 126.

**Ein Einladungscode gilt für genau einen Beitritt.** `joinAtomic()` schreibt seit dem 17.08.2026 drei Dokumente in einem Batch: die Mitgliedschaft, `memberCount` und `invites/{code}.used = true`. Gespeichert wird nur das Flag, **keine UID des Beitretenden** — wer dabei ist, sagt die Mitgliederliste, und `invites/{code}` darf jeder Angemeldete lesen. Die Rückkehr eines noch bestehenden Mitglieds läuft über `putMember()` und ist vom Verbrauch ausdrücklich nicht betroffen; `joinGroup()` prüft `inv.used` deshalb erst, nachdem `istMitglied()` verneint hat. Die harte Grenze liegt in Stufe 2 der Firestore-Regeln, die gestaffelt ausgeliefert wird (`docs/TROUBLESHOOTING.md` 105).

**Einladungscodes überdauern keine Mitgliedschaft.** `dropAllInviteCodes()` löscht in `leaveGroup()` alle Codes aus `state.inviteCodes` — auf beiden Wegen, Verlassen wie Auflösen. Begründung ist eine Zusage der Regeln: Erzeugen darf einen Code nur der Inhaber einer Gruppe, und in dieser Gruppe ist man danach nicht mehr. `dissolveGroupFirestore()` behält seine gid-gefilterte Runde, weil sie auch im Wartezustand läuft (`withdrawPendingInvite()`), wo es noch keine Mitgliedschaft zu verlassen gibt. Nur erfolgreich gelöschte Codes verlassen die Liste (`docs/TROUBLESHOOTING.md` 104).

**Der Rückweg räumt auf: `pruneOwnRecipes()` (28.08.2026).** Beim Beitritt wandert der eigene
Bestand in die Gruppe (`copyOwnRecipesToGroup()`) und wird lokal ersetzt — in
`users/{uid}/recipes` bleibt er aber liegen, denn `recipeBase()` zeigt in einer Gruppe auf
`["groups", gid]`. `leaveGroup()` räumt dort deshalb auf — **je `lib` bleibt genau einer stehen**, der aus dem
mitgebrachten Gruppenstand hat Vorrang. Ein Meal, dessen `lib` nur einmal vorkommt, ist damit
unantastbar; Meals ohne `lib` werden nie angefasst. Die Regel ist gegen die echten 81
Dokumente gerechnet worden, nachdem zwei einfachere Fassungen daran gescheitert waren
(`docs/TROUBLESHOOTING.md` 125, zweiter Nachtrag). Eine geleerte Baseline reicht dafür **nicht**: `syncRecipes()` bildet
`delIds` aus `prev ohne cur`, was nie in der Baseline stand, wird nie gelöscht — und
`startCloudSync()` mischte den Altbestand beim nächsten Start über `mergeRemoteRecipes()`
(Vereinigung über die **ID**, gleiche `lib` fällt dort nicht auf) wieder unter die
Gruppen-Meals. **Nur-Leser sind ausgenommen** (`warNurLeser`, vor `leaveGroupState()` gelesen):
`joinGroup()` kopiert für `role === "view"` nichts in die Gruppe, dort ist das eigene Konto die
einzige Kopie. Ein leerer Behalten-Stand und ein gescheiterter Lesevorgang räumen nichts —
Kür, nicht Pflicht, wie der Abgleich im Beitrittspfad. Ausführlich:
`docs/TROUBLESHOOTING.md` 125.

**Verlassen und Auflösen sichern denselben Snapshot, aber zu verschiedenen Zeitpunkten.** `snapshotOwnData()` liefert Meals und Wochenplan als eigene Kopie; `leaveGroup(keep)` schreibt sie zurück ins eigene Konto. Beim einfachen Verlassen bildet `leaveGroup()` den Snapshot selbst. Beim Auflösen zieht ihn `dissolveGroup()` **vor** `dissolveGroupFirestore()` und reicht ihn herein — sonst hätten `watchPlans`/`watchRecipes` den lokalen Stand nach dem Löschen bereits geräumt und die Sicherung wäre leer (`docs/TROUBLESHOOTING.md` 101).

Drei Randfälle werden bewusst behandelt, statt einen zweiten, verwaisten Gruppen-Zeiger entstehen zu lassen:

* **Konto löschen im Wartezustand:** `deleteAccountFlow()` sperrt nicht nur bei aktiver Eigner-Rolle (`syncGid`), sondern auch bei gesetztem `state.pendingGroupId` — sonst bliebe `groups/{gid}` als Karteileiche ohne erreichbaren Owner zurück.
* **Beitritt zu einer fremden Gruppe trotz eigener offener Einladung:** `joinGroup()` zieht eine eigene, andere `pendingGroupId` über `withdrawPendingInvite()` zurück — bewusst erst *nachdem* der Beitritt zur neuen Gruppe bereits geglückt ist (`putMember`/`copyOwnRecipesToGroup`/`CloudSync.save` liefen durch), nicht davor. Andernfalls würde ein Netzfehler zwischen Zurückziehen und Beitritt beide Gruppen kosten. Ohne das Zurückziehen würde ein späterer Beitritt über die alte Einladung `finalizeGroupActivation()` mit dem inzwischen fremden `state.recipes`-Bestand befüllen.
* **Eigene Einladung scannen/öffnen:** `openInviteModal()`/`joinGroup()` prüfen zusätzlich `state.pendingGroupId === inv.gid` — sonst würde die Firestore-Regel den Rollenwechsel auf sich selbst zwar verhindern, der Nutzer sähe aber nur einen generischen Fehler.

### Drei Zustände statt true/false: `enterGroupSync()`

`enterGroupSync()` liefert `"ok"`, `"gone"` oder `"error"`. Die Unterscheidung ist keine Kosmetik, sondern die Grenze zwischen „wir sind nachweislich draußen" und „wir wissen es gerade nicht":

* `"ok"` — drin, alle Listener hängen.
* `"gone"` — Gruppendokument existiert nicht mehr, oder man steht nicht in der Mitgliederliste. **Nur hier** darf `startCloudSync()` `state.groupId` leeren. Eine **leere** Mitgliederliste zählt ausdrücklich nicht dazu: `getDocs()` wirft offline nicht, sondern liefert das leere Cache-Ergebnis — das ergibt `"error"`.
* `"error"` — der Zugriff ist gescheitert (Netz, noch nicht veröffentlichte Regeln, Rate-Limit) oder `CloudGroup` ist gar nicht verfügbar. Über die Mitgliedschaft sagt das nichts aus, der Zeiger bleibt stehen, der nächste Start versucht es erneut.

Bei `"error"` setzt `startCloudSync()` zusätzlich `groupSyncFailed = true`. Dieses Flag hält `pushNow()` davon ab, die Felder `groupId` und `plans` überhaupt in das Kontodokument zu schreiben — was nicht in der Nutzlast steht, steht auch nicht in `mergeFields`, der vorhandene Cloud-Stand bleibt also unangetastet (siehe „Das Kontodokument wird feldweise ersetzt" unten). Ohne das Flag würde der Fehlerzustand (`syncGid === null`) als `groupId: ""` hochgeschrieben und die Gruppe für **alle** Geräte des Kontos unauffindbar machen. Das reguläre Verlassen ist davon nicht betroffen: `leaveGroup()` schreibt sein `groupId: ""` selbst und explizit.

Der `"gone"`-Zweig räumt bewusst **nicht** mehr per `removeMember()` auf. `CloudGroup.fetch()` liefert `null` für jedes Leseergebnis ohne Dokument — aus einem Lesevorgang darf keine Löschung folgen.

### Drei Sperren, nicht eine: wann `pushNow()` den `groupId`-Zeiger anfassen darf

`groupSyncFailed` allein reichte nicht, weil es erst *mitten* im `try` von `startCloudSync()` gesetzt wird. `pushNow()` bündelt deshalb drei Bedingungen in `groupKnown`:

| Sperre | gesetzt in | schützt vor |
|---|---|---|
| `syncHandshakeOk` | `startCloudSync()`, unmittelbar vor dem Baseline-Push; zurückgesetzt in `stopCloudSync()` | Abbruch **vor** dem Gruppen-Handshake. `syncUid` ist dann schon gesetzt, die App pusht also weiter — ohne diese Sperre schriebe der nächste `save()` `groupId: ""`. |
| `groupSyncFailed` | bei `enterGroupSync() === "error"`, im `catch` von `startCloudSync()`, `activateGroup()` und `joinGroup()` | ungeklärte Mitgliedschaft nach einem gescheiterten Zugriff |
| `groupTransition` | für die Dauer von `activateGroup()`/`joinGroup()`, `finally` räumt auf | Debounce-Push im Fenster zwischen Cloud-Write und `switchGroup()`, in dem `syncGid` der Cloud absichtlich nachhinkt. Beide Funktionen rufen beim Eintritt zusätzlich `clearTimeout(pushTimer)`. |

Ist `groupKnown` false, fehlen `groupId` **und** `plans` im geschriebenen Objekt — sie stehen damit auch nicht in `mergeFields`, der Cloud-Stand bleibt unangetastet. Das reguläre Verlassen ist davon nicht betroffen: `leaveGroup()` schreibt sein `groupId: ""` selbst und explizit.

Aus derselben Logik behandeln die Listener leere Ergebnisse als *ungeklärt*, nicht als Austritt: `watchMembers()` meldet Lesefehler als `null` statt als leere Liste, `onMembersRemote()` steigt bei leerer Liste aus (eine bestehende Gruppe hat immer ≥ 1 Mitglied; das echte Auflösen kommt über `onGroupRemote()`), und `onRemote()` löst bei leerem `remoteGid` **kein** `switchGroup(null)` mehr aus, solange eine Gruppen-Session läuft.

Seit dem Firestore-Offline-Cache gilt dieselbe Vorsicht zusätzlich für `fromCache`-Ergebnisse, nicht nur für leere: siehe „Firestore-Offline-Cache" oben und `docs/TROUBLESHOOTING.md` („`fromCache` ist kein Beweis").

### Das Kontodokument wird feldweise ersetzt, nicht blattweise gemischt (24.08.2026)

```js
setDoc(doc(db, "users", uid), data, { mergeFields: Object.keys(data) })
```

**Die Regel:** Was der Aufrufer schickt, wird **ganz** gesetzt; was er weglässt, bleibt liegen.
Das ist die Semantik, auf die sich `groupKnown`, `leaveGroup()` und die Teil-Schreibvorgänge
(`{ pendingGroupId: … }`) schon immer verlassen haben.

Bis zum 24.08.2026 stand dort `{ merge: true }` — und das ist etwas anderes: ein **tiefer** Merge
über Blattpfade. Eine Map, die ohne `diet` ankam, löschte `goal.diet` in Firestore nicht.
„Vegetarisch → Alles" war damit überhaupt nicht wegzuschreiben, `goal.manual` überlebte den
Rechner, ein entfernter Trainingstag blieb stehen. Ausführlich in `docs/TROUBLESHOOTING.md`,
Ziffer 108.

**Zwei Felder ändern dadurch ihre Bedeutung — beide gewollt:**

* `plans` (nur außerhalb einer Gruppe, siehe `groupKnown`) wird **ersetzt**. `state.plans` ist
  durch `pruneWeeks()` auf aktuelle + nächste Woche beschnitten; die Cloud verliert damit alte
  Wochen, die sie bisher als Rest mitschleppte. Beim Lesen läuft `pruneWeeks()` ohnehin — der
  Datensatz wird ehrlicher, nicht ärmer.
* `weightGoals`, `deleted`, `weightConsent` und `planned` werden ebenfalls **ersetzt**. Alle vier
  vereinigt `onRemote()` **vor** dem Speichern lokal (`mergeWeights`, `mergeTombstones`,
  `mergeConsent`, `unionIds`), der lokale Stand ist also bereits der vollständige. Ersetzen ist
  hier nicht nur unschädlich, sondern die einzige Variante, in der ein Löschen ankommt.

**Nicht betroffen sind die Gruppen-Plandokumente** (`CloudGroup.savePlanWeek`). Dort ist der
blattweise Merge genau richtig: Zwei Geräte sollen sich nur im selben Slot ins Gehege kommen,
nicht im ganzen Wochendokument.

**Dazu `ignoreUndefinedProperties: true`** in beiden Zweigen von `initializeFirestore()` (auch im
Fallback ohne persistenten Cache). Damit verhält sich die Cloud wie `JSON.stringify` und
`canonJSON()`: Fehlt ein Wert, fehlt das Feld. Es ist ein Netz unter den Sanitizern, kein Ersatz
für sie — ein still fallengelassenes Feld ist eine Notbremse, kein sauberer Datensatz.

**`pushNow()` unterscheidet jetzt Netz- von Datenfehlern.** Ein Netzfehler (`unavailable`,
`deadline-exceeded`, `cancelled`, `resource-exhausted`) bleibt stumm und meldet nur „offline“;
alles andere geht einmalig über `noteError("sync:push", …)` samt Toast hinaus. Der Grund steht in
Ziffer 108: Ein Datenfehler heilt nicht von selbst, und als „offline“ gemeldet bleibt er
unsichtbar — obwohl er das gesamte Kontodokument blockiert.

### Selbstheilung des Zeigers

`wantGid` in `startCloudSync()` ist `remote.groupId || state.groupId`. Hat ein Fehlerpfad den Cloud-Zeiger geleert, während `groups/{gid}` und die Mitgliedschaft weiterbestehen, holt der nächste Start die Gruppe zurück und `pushNow()` trägt den Zeiger wieder ein. Der reguläre Austritt auf einem anderen Gerät bleibt korrekt: dort ist der eigene Mitglieder-Eintrag gelöscht, `enterGroupSync()` liefert `"gone"`, der Zeiger wird geräumt.

Scheitert `enterGroupSync()` in `startCloudSync()` direkt nach einer gerade erst geglückten Start-Aktivierung (z. B. Netzabbruch im selben Moment), wird `pendingGroupId` wiederhergestellt statt beide Zeiger zu verlieren — sonst wäre die (für den Beitretenden längst aktive) Gruppe für den Owner nicht mehr auffindbar. Scheitert die Aktivierung selbst (live oder beim Start), wird `watchPendingGroup()` erneut angehängt statt die Sitzung dauerhaft ohne Listener zu lassen.

### Sicherheitsnetz gegen wiederholtes `switchGroup()`: `lastGroupAttempt`

`onRemote()` löst bei jedem Snapshot mit `remoteGid !== syncGid` `switchGroup()` aus — das ist der reguläre Weg, auf dem ein Beitritt/Austritt auf einem anderen Gerät ankommt. Scheitert der dadurch angestoßene `enterGroupSync()` (liefert `"error"`), bleibt `syncGid` `null`, während das Kontodokument die Gruppe weiter nennt (`pushNow()` schreibt `groupId` bei `groupSyncFailed` ja gerade **nicht** zurück, siehe `groupKnown`). Jeder weitere Snapshot sähe also wieder `remoteGid !== syncGid` und stieße `switchGroup()` erneut an — und `switchGroup()` ruft als Erstes `stopCloudSync()`, das `groupSyncFailed` zurücksetzt. Ohne ein zusätzliches Gedächtnis läuft der gescheiterte Versuch damit bei **jedem** Snapshot neu an.

`lastGroupAttempt` merkt sich, für welche `remoteGid` der letzte Versuch bereits gescheitert ist. `onRemote()` prüft `groupSyncFailed && remoteGid === lastGroupAttempt` (`retryingFailedAttempt`) und überspringt `switchGroup()` in diesem Fall — der restliche Snapshot (Ziel, Gewichte, Profilbild) wird trotzdem verarbeitet, genau wie beim verwandten `staleEmptyGid`-Fall nebenan. Wechselt die Gruppe wirklich (andere `remoteGid`), greift das Netz nicht, kein Dead-Lock.

**Wichtig, weil hier ein erster Anlauf falsch lag:** `lastGroupAttempt` darf **nicht** in `onRemote()` gesetzt werden, wenn `switchGroup()` angestoßen wird. `switchGroup()` ruft `stopCloudSync()` **vor** `startCloudSync()` auf, und `stopCloudSync()` räumt `lastGroupAttempt` (wie `groupSyncFailed`) wieder auf — ein in `onRemote()` gesetzter Wert wäre zum Zeitpunkt des eigentlichen Scheiterns längst wieder `null`, das Sicherheitsnetz wirkungslos. Gesetzt wird `lastGroupAttempt` deshalb **an den vier Stellen, die `groupSyncFailed` setzen** — dort, wo der Versuch tatsächlich scheitert, nach dem Aufräumpfad:

* `startCloudSync()`, **im `try`** nach `enterGroupSync()`: `if (groupSyncFailed) lastGroupAttempt = wantGid || null`. Der häufigste Fall und kein `catch` — `enterGroupSync()` fängt seine Fehler selbst ab und gibt `"error"` **zurück** (Netz weg, Regeln nicht veröffentlicht, leerer Mitglieder-Snapshot), wirft also nie.
* `startCloudSync()`, `catch`-Block: `lastGroupAttempt = state.groupId || null` (greift nur bei geworfenen Exceptions weiter oben, z. B. `CloudSync.load()`)
* `activateGroup()`, `catch`-Block: `lastGroupAttempt = gid || null`
* `joinGroup()`, `catch`-Block: `lastGroupAttempt = (inv && inv.gid) || null` (bewusst `inv.gid`, nicht `prevGid` — der gescheiterte Versuch galt der neuen Gruppe, nicht der alten). `inv` ist dort mit `let` **vor** dem `try` deklariert und die Null-Prüfung ist Pflicht: `try{}`/`catch{}` sind eigene Blöcke, ein `const inv` innerhalb des `try` wäre im `catch` gar nicht sichtbar, und scheitert schon `fetchInvite()` selbst, ist `inv` noch `null`.

**Lehre:** Ein Flag, das ein Aufräumpfad zurücksetzt, darf nicht vor diesem Aufräumpfad gesetzt werden — sonst ist die Reihenfolge „setzen, dann aufräumen" statt „aufräumen, dann setzen", und das Netz greift nie. `stopCloudSync()` räumt `lastGroupAttempt` weiterhin auf; das ist korrekt, weil alle vier Stellen, die es setzen, zeitlich **nach** dem zugehörigen `stopCloudSync()`-Aufruf laufen.

**Zweite Lehre, aus derselben Nacht:** Der erste Anlauf deckte nur die drei `catch`-Blöcke ab und übersah den vierten und häufigsten Ort — `groupSyncFailed = groupResult === "error"` mitten im `try` von `startCloudSync()`. `enterGroupSync()` fängt seine Fehler nämlich selbst ab und **liefert** `"error"` zurück, statt zu werfen; ein `catch` sieht diesen Fall nie. Wer ein Fehler-Flag absichert, muss `grep`en, wo es überall gesetzt wird — nicht annehmen, Fehler kämen ausschließlich als Exception. Gefunden haben das `kvp` und `website-security` unabhängig voneinander.

## Mitgliederlimit: `memberCount` (16.08.2026)

Eine Gruppe trägt höchstens **vier** Personen. Die Zahl steht an zwei Stellen —
`MAX_GROUP_MEMBERS` im Client und `maxMitglieder()` in `firestore.rules`. **Verbindlich ist
ausschließlich die Regel**; die Konstante ist die freundliche Oberfläche davor.

**Rules können nicht zählen** — es gibt kein `count()` auf eine Unterkollektion. Deshalb führt
das Gruppendokument ein Feld `memberCount`, das per `getAfter()` hart an die Mitgliedschaft
gekoppelt ist: `get()` liefert den Stand **vor** dem Batch, `getAfter()` den **danach**. Wer
beitritt, muss im selben Batch hochzählen; wer austritt, herunter. Einzelne Schreibvorgänge
werden abgelehnt.

Die vier Zweige von `allow update` auf `groups/{gid}`:

| Zweig | Wer | Bedingung |
|---|---|---|
| 1 | Inhaber | Name/Einstellungen/`status`, Zähler **unverändert** — oder erstmalig nachgetragen (Migration) |
| 2 | Beitretender | genau `+1`, `< 4`, vorher **kein** und nachher Mitglied |
| 3 | Austretender | genau `−1`, vorher Mitglied und nachher **nicht** |
| 4 | Inhaber | genau `−1` (entfernt jemanden) |

`zaehlerNurUm(delta)` prüft zusätzlich `affectedKeys().hasOnly(['memberCount'])` — ohne das
ließe sich unter dem Deckmantel eines Beitritts auch der Inhaber austauschen.

### Vier Stellen schreiben Mitgliedschaft — alle atomar

`CloudGroup.joinAtomic()` / `leaveAtomic()` bündeln Mitglied und Zähler in einem `writeBatch`,
mit `increment()` statt eines gelesenen Werts: Zwei gleichzeitige Beitritte lägen sonst auf
derselben veralteten Basis, und die Regel wiese den zweiten ab.

* `joinGroup()` → `joinAtomic`
* `leaveGroup()` → `leaveAtomic`
* Mitglied entfernen im Gruppen-Modal → `leaveAtomic`
* `CloudAuth.deleteAccount()` → eigener Batch (siehe `docs/TROUBLESHOOTING.md`)

`CloudGroup.dissolve()` bleibt **unverändert** — die `delete`-Regel nimmt es über
`!existsAfter(grpPath(gid))` aus, weil dort das Gruppendokument im selben Batch verschwindet.

### Migration

`migrateMemberCount()` trägt das Feld bei einer Gruppe aus der Zeit davor einmalig nach —
**nur der Inhaber**, nur wenn es fehlt, und nur bei nichtleerer Mitgliederliste (eine leere
Liste ist ein ungeklärtes Leseergebnis, kein Beweis). Genau dafür ist der Migrationszweig in
Regelzweig 1 da. Läuft ohne `await` neben `syncMyMember()`, darf den Start also nicht aufhalten.

## Gruppen-Wochenplan

Der Plan wird als ein Dokument pro ISO-Woche gespeichert.

Slots sind flach aufgebaut, z. B.:

`mon_fr: ["r1"]`

Schreibvorgänge verwenden:

`setDoc(..., { merge: true })`

und eine Baseline über:

`lastPushedSlots`

Ziel ist, dass parallele Änderungen nur denselben Slot kollidieren lassen und nicht den gesamten Wochenplan überschreiben.

### Die vier Slots kommen aus `MEALS`

`MEALS` (`fr`, `mi`, `ab`, `sn`) ist die einzige Quelle für die Mahlzeiten eines Tages. Alles
Nachgelagerte iteriert darüber und zieht bei einer Erweiterung von selbst mit: `makeEmptyPlan()`,
`normalizePlan()`, `flattenWeek()`/`unflattenWeek()`, Einkaufsliste, „Woche leeren", `dayNut()`
und der Druck.

**Bestandsdaten brauchen keine Migration.** Ein fehlender Schlüssel wird über `makeEmptyPlan()`
leer angelegt, und `flattenWeek()` schreibt leere Slots ohnehin nicht in die Cloud. Ein Gerät mit
älterem Stand kennt `mon_sn` nicht, überliest es beim Lesen und überschreibt es beim Schreiben
nicht — die Snacks bleiben erhalten, sind dort nur unsichtbar.

**Die eine Stelle, die nicht mitzog:** `makeEmptyPlan()` hatte die drei Slots hart verdrahtet
(`{ fr: [], mi: [], ab: [] }`). Ohne Korrektur wäre `state.plan[tag].sn` überall `undefined`
gewesen und der erste Zugriff hätte die App mitgerissen. Wer `MEALS` erweitert, prüft zuerst, ob
es noch eine solche Liste gibt.

**Kategorie-Bindung:** `CAT_TO_MEAL` bindet `Snack` und `Dessert` ausschließlich an `sn`,
`Frühstück` an `fr`, `Hauptgericht` an `mi`/`ab`. Das wirkt **nur auf die Auswahlliste**
(`catFitsMeal()` im Picker, mit „Alle anzeigen" als Auslass) — bereits verplante Einträge bleiben
unangetastet, `normalizePlan()` filtert nach Meal-Existenz, nicht nach Kategorie.

## Gerichte-Zuweisung (Gemeinsam planen)

Ein Slot-Eintrag in `state.plan[day][meal]` ist entweder:

* ein blanker String (Rezept-ID) — "für alle" Gruppenmitglieder, unverändertes Bestandsformat
* ein Objekt `{ id, uids }` — nur die genannten Mitglieder essen dieses Gericht

Keine Migration nötig: Bestandsdaten (reine String-Arrays) sind bereits gültig, und
`flattenWeek()`/`pushGroupPlan()` kopieren beide Formen typneutral durch.

Helper (neben `asIdList()`):

* `entryId(e)` / `entryUids(e)` (`null` = für alle) / `entryIsShared(e)`
* `makeEntry(id, uids)` — vereinfacht automatisch zurück zu einem blanken String, wenn `uids`
  **jedes aktuelle** Gruppenmitglied abdeckt (Mengenabdeckung per `groupMembers.every(...)`,
  nicht nur `uids.length`, sonst würde eine veraltete UID eines ausgeschiedenen Mitglieds einen
  Eintrag fälschlich zu "für alle" kollabieren lassen)
* `slotIsShared(day, meal)` — prüft, ob ein ganzer Slot noch ausschließlich geteilte Einträge hat

`unflattenWeek()` sanitisiert empfangene `{id,uids}`-Objekte: `uids`-Elemente müssen Strings
sein, auf 24 Einträge gedeckelt (das Dokument kommt von einem anderen Gerät und wird nicht
vertraut). `normalizePlan()` filtert weiterhin über `entryId(e)` gegen bekannte Rezept-IDs.

Zuweisen-UI (Personen-Symbol, nur ab `groupMembers.length >= 2`): bei genau zwei Mitgliedern ein
Klick-Zyklus ("für alle" → "nur ich" → "nur die andere Person" → "für alle"), ab drei ein
Chip-Popover mit Mehrfachauswahl. Das Popover hängt sich an `document.body` (nicht an die Karte),
weil `.day` `overflow: hidden` für die mobilen Karussell-Streifen trägt und ein daran verankertes
Popover abschneiden würde.

**Nach `asIdList()` darf kein Vergleich mehr auf den rohen Eintrag zeigen** — kein `.filter`,
`.indexOf`, `.includes` oder `.has`, immer über `entryId(e)`. `dropRecipeIds()` tat es bis zum
28.08.2026 doch (`idSet.has(x)`) und ließ damit jedes gelöschte Meal, das jemandem
**zugewiesen** war, als Geisterverweis im Plan stehen — während dieselbe Löschung in der
„für alle“-Form sauber durchlief. `dropRecipeIds()` und `rewritePlanIds()` müssen über
dieselben Einträge dieselbe Menge treffen; `docs/TROUBLESHOOTING.md` 127.

**Der Orphan-Schutz gilt auf BEIDEN Wegen** — seit dem 28.08.2026 auch eingehend.
`unflattenWeek()` liess `{ id, uids: [] }` durch (`uids ? … : …` — ein leeres Array ist
truthy) und erzeugte es aus einer nur mit Nicht-Strings gefüllten Liste sogar selbst. Ein
solcher Eintrag ist sichtbar, aber für jede Auswertung unsichtbar: `dayNutOf()` zählt ihn
niemandem an, die Einkaufsliste skaliert ihn auf null, und `slotOpenForMe()` meldet den Slot
als frei — der Auto-Planer plant darüber. Eingehende Waisen werden jetzt entfernt, wie es der
Zuweisungs-Dialog lokal seit jeher tut. `docs/TROUBLESHOOTING.md` 130.

Orphan-Schutz: Würde eine Abwahl `uids.length === 0` ergeben, wird stattdessen der komplette
Eintrag entfernt (derselbe Pfad wie `unassign`, inklusive Undo-Toast) — ein Gericht ohne
zugewiesene Person darf nie im Datenmodell existieren.

**Geprüft seit dem 28.08.2026** durch `tools/pruefstand-einkauf-gruppe.py`: der Vertrag
`sharedQty * per + assignedQty`, dieselbe Zutat aus beiden Arten im selben Lauf, und die
Zusage aus `planDaysAhead()`, dass Einkaufs- und Vorkochliste dieselbe Woche beschreiben.
`buildBatchList()` zählt dieselben Esser (`uids ? uids.length : persons`).

**„Einkauf für alle rechnen“ steuert BEIDE Summanden** (28.08.2026). Bis dahin folgte nur der
„für alle“-Anteil der Einstellung; der zugewiesene trug seinen Faktor fest im Eintrag
(`uids.length`) und blieb bei **Aus** doppelt — bei einem Schalter, der „Mengen × Mitglieder“
heißt. `shopCountsMembers()` ist die gemeinsame Bedingung für `buildShoppingList()` und
`buildBatchList()`; bewusst **nicht** an `per` gehängt, weil `per` auch aus einer von Hand
gesetzten Personenzahl stammen kann. Die Zuweisung sagt weiterhin, *wer* isst — nur nicht mehr
allein, *wie viel* eingekauft wird. `docs/TROUBLESHOOTING.md` 132.

Die Einkaufsliste (`buildShoppingList()`) trennt pro Zutat `sharedQty` (aus "für alle"-Gerichten,
skaliert erst mit dem globalen `per`-Personenfaktor) von `assignedQty` (aus individuell
zugewiesenen Gerichten, bereits pro Gericht auf `uids.length` skaliert — jede zugewiesene Person
braucht ein eigenes Meal). Endsumme: `sharedQty * per + assignedQty`. Bewusste Entscheidung:
"für alle"-Einträge verhalten sich exakt wie vor diesem Feature, nur abweichend zugewiesene
Gerichte werden zusätzlich skaliert.

Der frühere Teiler `r.portions` ist am 15.08.2026 entfallen (ein Meal = eine Portion). Er war
die einzige Stelle, an der das Feld überhaupt rechnete — und genau deshalb widersprüchlich:
Bei "für alle" wurde er nie angewandt, die Tagesbilanz kannte ihn ohnehin nicht.

Farbring/Initiale (`--member-1` bis `--member-6`) nur bei "eigenen"/"anderen" Karten, nie bei
"gemeinsam". Maximal 2 Badges pro Karte, der Rest sammelt sich in einem "+N"-Badge
(`BADGE_MAX`).

**Farbvergabe (`memberColorSlot()`) ist kollisionsfrei, nicht nur gehasht.** Ausgangspunkt
bleibt ein UID-Hash (`memberColorHash()`) — bewusst **nicht** der Index in `groupMembers`, der
aus `getDocs()` ohne `orderBy` kommt. Der reine Hash allein reichte aber nicht: bei sechs Farben
hatten **65 % aller Gruppen mit 2–6 Mitgliedern** mindestens eine Doppelfarbe (gemessen über
2000 simulierte Gruppen). Deshalb wird die nach UID **sortierte** Mitgliederliste durchlaufen und
bei Belegung der nächste freie Slot genommen — sortiert, damit jedes Gerät unabhängig von der
Ladereihenfolge dasselbe Ergebnis berechnet. Ab sieben Mitgliedern sind Doppelungen unvermeidbar,
dann greift wieder der reine Hash (sonst suchte die Schleife einen freien Slot, den es nicht
gibt). Bewusst in Kauf genommen: Verlässt jemand die Gruppe, kann die Farbe eines anderen
Mitglieds umspringen — seltener und akzeptabler als eine dauerhafte Doppelfarbe.

**Das Kürzel im Badge ist so lang, wie es zur Unterscheidung sein muss.** `memberBadgeIni()`
zeigt normalerweise einen Buchstaben; trägt ein **anderes** aktuelles Gruppenmitglied denselben
Anfangsbuchstaben, bekommen **beide** ein zweistelliges Kürzel (`memberIni(name, 2)`: Vor- +
Nachname-Initiale, ohne Nachnamen die ersten zwei Buchstaben des Vornamens — "Anna"/"Alex" →
"AN"/"AL"). Der Farbring allein trägt die Unterscheidung nicht: er ist `aria-hidden` und fällt
bei Farbfehlsichtigkeit aus. Zweistellige Kürzel sind breiter — zwei davon passen noch (34 px),
zwei davon **plus** "+N" liefen 5 px links aus der Karte heraus. Nur in dem Fall geht
`memberBadgeHtml()` auf **einen** Kreis plus "+N" zurück. Die Badges liegen als Flex-Reihe
(`.r-badges`, `row-reverse`, Überlappung per negativem `margin-right`) statt einzeln absolut
positioniert: feste `right`-Werte je `nth-child` setzten eine feste Badge-Breite voraus.

**`dayNutOf()` filtert nach Person, nicht nur nach Sichtbarkeit.** Die Tages-/Wochen-
Nährwertsumme läuft gegen das **persönliche** `state.goal` — ein nur der anderen Person
zugewiesenes Gericht darf das eigene Kalorien-/Makroziel nicht belasten. Deshalb zählt
`dayNutOf()` einen `{id,uids}`-Eintrag nur, wenn `uids` entweder leer/`null` ("für alle") ist
oder die eigene `syncUid` enthält. Andere Konsumstellen von `state.plan`-Einträgen (z. B.
`buildPrintable()` für den Strg+P-Ausdruck) sind dagegen personen-neutrale Übersichten über den
ganzen Haushalt und brauchen nur `entryId(entry)` statt der rohen ID — dort zählt Sichtbarkeit,
nicht Zurechnung.

## Wichtige Gruppen-Sync-Regeln

Wenn `syncGid` gesetzt ist **oder `groupSyncFailed` gesetzt ist**:

`dataJSON` darf `plans` nicht enthalten (`plans: (syncGid || groupSyncFailed) ? null : plansField(d)`).

Der zweite Fall ist ebenso wichtig wie der erste: `pushNow()` schreibt `state.plans` bei
`groupSyncFailed` ebenfalls nicht (siehe `groupKnown`). Bliebe `plans` in `dataJSON` trotzdem
drin, läge `state.plans` (möglicherweise der persönliche Stand von vor einem gescheiterten
Beitrittsversuch) dauerhaft quer zu `data.plans` — derselbe Endlos-Vergleich wie im regulären
Gruppenfall, nur ausgelöst durch einen Fehlerzustand statt durch eine echte Mitgliedschaft.

Sonst können:

* `state.plans`
* `data.plans`

gegenseitig Snapshot-Vergleiche auslösen und Endlosschleifen erzeugen.

Leere Slots werden aus der Baseline entfernt.

Nicht als `"[]"` speichern.

Ein Fehlerzustand darf nie zu einem Schreibvorgang werden. `syncGid === null` bedeutet nicht „nicht in einer Gruppe", sondern kann auch „Gruppen-Start gescheitert", „Start nie fertig geworden" oder „Beitritt läuft gerade" heißen — deshalb schreibt `pushNow()` `groupId`/`plans` nur bei `groupKnown` (`syncHandshakeOk && !groupSyncFailed && !groupTransition`, siehe Gruppenmodus). Gleiche Bauart wie `recipesSyncFailed` bei den Meals. Ein Schutzflag muss den gesamten Zeitraum abdecken, in dem der Zustand ungeklärt ist — nicht nur den Abschnitt, in dem es gesetzt wird.

## Rollen

Gruppenrollen:

* `owner`
* `edit`
* `view`

Die UI-Sperre sitzt primär im zentralen Event-Delegation-Choke-Point:

* `WRITE_ACTIONS`
* `blockedByRole()`

Zusätzliche nicht-delegierte Pfade müssen ebenfalls berücksichtigt werden:

* `photoInput.change`
* Datei-Drop
* Strg+V
* `dragstart`

**Die UI-Sperre ist keine Sicherheitsgrenze.**

Verbindlich sind die Firestore Security Rules.

## Datenmodell und Datenschutz

Ein Meal speichert bei `by` ausschließlich die UID.

Der Name wird erst bei der Anzeige über `groupMembers` aufgelöst.

E-Mail-Adressen gehören nicht in Gruppen-Mitgliederdokumente.

Grund:

* weniger redundante personenbezogene Daten
* einfachere Löschung
* keine n-fache Nachpflege von Meal-Dokumenten

### Reiter und ihre Renderer

`render()` verzweigt über `state.tab` auf genau einen Renderer; `TAB_ORDER` gibt zugleich die
Reihenfolge in der Leiste und die Richtung des Schiebe-Übergangs vor:

```
TAB_ORDER = ["home", "plan", "recipes", "progress"]
```

* `renderHome()` — `appHeroHtml()` + `weekNutHtml()`
* `renderPlan(sameTab)`
* `renderRecipes()`
* `renderProgress()` — `rueckblickHtml()` + `kalenderHtml()` + `weightHtml()` (seit 30.08.2026, B7)

`renderProgress()` braucht kein `initCarousel()` (kein `.wg-cols`), aber `initWeightChart()`
und `initRueckblick()` — beide messen bzw. binden erst nach dem Einsetzen des Markups.

Ein neuer Reiter berührt immer vier Stellen: Markup-Knopf, `TAB_ORDER`, die Verzweigung in
`render()` und die Spaltenzahl der mobilen Kapsel (siehe `.tab-ind` weiter unten).

### Gewichtsverlauf: eine Wiegung je **Woche**

`state.weights` ist eine aufsteigend sortierte Liste `{ m, kg }`. Seit 13.08.2026 (B2) ist `m`
ein **ISO-Wochenschlüssel** (`"2026-W33"`) — dasselbe Format wie `state.plans` und
`state.weekStats`. Monatsgenau war für Trainierende zu grob; taggenau wäre kein Gewinn, weil
Tagesschwankungen größer sind als der Fortschritt einer Woche.

Das Feld heißt weiterhin `m` — es steckt in gespeicherten Daten und in der Cloud
(Namensdualität, `CLAUDE.md` §21).

`sanitizeWeights()` rechnet **beide Altformate** um, statt sie zu verwerfen:

* taggenau (`d: "2026-07-22"`, erste Fassung) → Woche dieses Tages
* monatsgenau (`m: "2026-07"`) → Woche, die den **15.** enthält (Monatsmitte als ehrlichste
  Näherung, wenn der Tag nicht mehr bekannt ist)

Hilfsfunktionen: `weightKeyNow(dt)`, `validWeightKey(s)`, `weekNumOf(s)`, `weekMonday(key)`
(über den 4. Januar, der per ISO immer in KW 1 liegt) und `weekKeyLabel(key)` →
`"KW 33 · 10.08."`.

**`weekKeyLabel`, nicht `weekLabel`** (24.08.2026): Der Name kollidierte mit einer zweiten
Top-Level-Funktion, die einen Wochen-**Offset** als Zahl erwartet (`appHeroHtml()`). Durch
Hoisting gewann die spätere für alle Aufrufer, und der Gewichtsverlauf zeigte live
„Woche NaN · NaN. undefined". Siehe `docs/TROUBLESHOOTING.md` 112.

Das Diagramm verteilt die Wochennummer 1–52 über die feste Jahresbreite und zeichnet ab vier
Messungen zusätzlich den **gleitenden Durchschnitt über vier Messungen** (`.wch-avg`); die
Rohkurve tritt dann optisch zurück. Gerechnet wird über die letzten vier *vorhandenen* Werte,
nicht über vier Kalenderwochen — bei einer Lücke wäre der Schnitt sonst leer.

`syncGoalWeight()` zieht das Kalorienziel weiterhin an der jüngsten Messung nach — **außer**
bei `state.goal.manual` (siehe unten).

### Ziel von Hand justieren: `state.goal.manual`

`openGoalTuneForm()` (B4) schreibt `kcal`, `carbs`, `protein`, `fat` direkt und setzt
`manual: true`. Ohne diese Marke hätte die nächste Wiegung die Anpassung still überschrieben,
weil `syncGoalWeight()` mit `computeGoal()` neu rechnet. Bei gesetzter Marke zieht nur noch das
`weight`-Feld mit (daran hängt der Trainingstag-Aufschlag `dayTrainKcal()`).

Ein Durchlauf des Rechners hebt die Marke automatisch auf — `computeGoal()` baut ein frisches
Objekt ohne `manual`.

### Slot-Einträge: zwei Formen

Ein Eintrag im Wochenplan ist eines von zwei Dingen:

| Form | Bedeutung |
|---|---|
| `"rid"` | für alle — der Normalfall, bewusst ein blanker String |
| `{id, uids}` | nur für bestimmte Gruppenmitglieder |

**Zurückgenommen (13.08.2026): der Portionsfaktor `{id, p}`.** Er war einen Tag lang als B5
eingebaut (½ / 1 / 1½ / 2 am Slot) und ist auf Ansage wieder entfernt worden: Der Knopf saß am
selben Vorschaubild wie die Zuweisung und beantwortete eine sehr ähnliche Frage („wie viel
davon, für wen"), ohne dass beide zusammen gedacht waren. Zwei gleich große Bedienelemente
nebeneinander, die Verwandtes tun, sind schlechter als eines.

**`unflattenWeek()` lässt Objekte ohne `uids` weiterhin ausdrücklich zu** und führt sie auf die
String-Form zurück. Das ist kein toter Code: Auf einem anderen Gerät kann noch ein
`{id, p}` liegen, und ein Filter, der ein `uids`-Array verlangt, würde ihn lautlos verwerfen —
das Gericht wäre dort aus dem Plan verschwunden (`docs/TROUBLESHOOTING.md` §73). `p` fällt beim
Einlesen weg; damit räumt sich der kurze Zwischenstand von selbst auf.

### Einstieg: welcher Bildschirm wann (D1b)

`handleCloudUser(user)` entscheidet, was nach dem Start zu sehen ist:

| Lage | Bildschirm |
|---|---|
| Cloud-Nutzer, E-Mail bestätigt | App + `startCloudSync()` |
| Cloud-Nutzer, unbestätigt | Warteseite |
| niemand angemeldet, **kein** Profil | `renderAuthChoice()` — die Wahl, lokal als Standard |
| niemand angemeldet, **lokales** Profil | direkt in die App |
| niemand angemeldet, **Cloud-Profil** | Anmeldemaske (die Daten liegen in der Cloud) |

Vor D1b stand in den letzten drei Zeilen immer die Cloud-Anmeldung. Damit sah auch jemand mit
fertigem lokalem Profil eine Anmeldemaske, obwohl seine Daten auf dem Gerät liegen.

`enterLocalMode()` (Firebase nicht erreichbar, Timeout nach 6 s, Platzhalter-Config) überspringt
die Wahl bewusst: Ohne Cloud gibt es nichts zu wählen, der zweite Knopf wäre eine tote
Alternative.

`authMode` bleibt die einzige Quelle dafür, ob gerade Cloud-Funktionen möglich sind — daran
hängen Teilen-Links, Gruppen und der Sync-Punkt in der Kopfzeile.

### Pro-Berechtigung: `entitlements/{uid}` und `isPro()` (D1)

Der Pro-Status liegt in einer **eigenen Firestore-Sammlung**, die der Client nur lesen darf:

```
entitlements/{uid} = { pro: true, source: "manual"|"apple"|"google", until: timestamp|null }
```

**Warum nicht in `users/{uid}` oder in `state`:** Beides darf der Client schreiben. Ein Feld
`pro` im Kontodokument wäre mit den Entwicklerwerkzeugen sofort auf `true` gesetzt, und die
Firestore-Regel (`request.auth.uid == uid`) würde es anstandslos annehmen — die „Grenze" wäre
eine Anzeige. `state` liegt zusätzlich im localStorage und würde einen abgelaufenen Status über
jeden Neustart retten.

Der Status ist deshalb eine **Laufzeitvariable** (`proInfo`), gesetzt ausschließlich vom
`onSnapshot`-Listener in `startCloudSync()` und in `stopCloudSync()` wieder auf `null`. Ohne
Zurücksetzen erbte das nächste Konto auf demselben Gerät den Pro-Status des vorigen.

`isPro()` ist der **einzige** erlaubte Check. Er prüft bei jedem Aufruf auch den Ablauf — eine
App, die über Mitternacht offen bleibt, verliert Pro sonst nie. Spätere Sperrpunkte (D2b) fragen
`isPro()`, niemals `proInfo` direkt.

`sanitizeEntitlement()` behandelt das Dokument wie jede fremde Quelle: nur ein echtes `true`
zählt (kein `"true"`, keine `1`), unbekannte `source`-Werte fallen auf `"manual"`, und ein
**unbrauchbares `until` ergibt kein Pro** statt eines unbefristeten (siehe
`docs/TROUBLESHOOTING.md` §76).

Sichtbar ist der Status als „Pro"-Marke im Profilmenü.

### Die Sperrpunkte (D2b, 15.08.2026)

**Gesperrt ist genau eine Sache: das Gründen einer Gruppe samt Einladen.** Cloud-Sync ist
ausdrücklich frei, und das Beitreten zu einer Gruppe ebenfalls — dort zahlt der Inhaber
(`docs/PRODUCT.md`).

Zwei Punkte im Client, beide an der Gruppe:

| Ort | Ohne Pro |
|---|---|
| `prepareGroup()` | bricht mit einem freundlichen Hinweis ab, bevor irgendetwas in Firestore entsteht |
| `createInviteLink()` | wirft; die beiden Aufrufer zeigen den Grund an |

Dazu das Gruppen-Blatt: Zustand A zeigt ohne Pro statt „Person einladen" einen Hinweis —
**„Einladung scannen" bleibt stehen**, denn eingeladen werden soll niemand vor einer
Bezahlschranke landen.

**Der Sync selbst kennt `isPro()` nicht.** `pushNow()`, `syncRecipes()`, `onRemote()` und
`startCloudSync()` fragen die Berechtigung an keiner Stelle ab. Das ist eine bewusst
wiederhergestellte Eigenschaft: Ein Torwächter im Sync-Pfad hatte in der ersten Fassung von
D2b gleich drei Folgefehler erzeugt (`docs/TROUBLESHOOTING.md` 77–79), und keiner davon war
beim Lesen sichtbar.

**Serverseitig** (`firestore.rules`, Fassung vom 15.08.2026 — **im Repo scharf, in der Konsole
noch nicht veröffentlicht**):

* `users/{uid}` und `users/{uid}/recipes/*`: unverändert `read, write` für das eigene Konto.
  Keine Pro-Prüfung.
* `groups/{gid}`: `create` nur mit eigenem Pro. Schreiben in `plans`/`recipes` prüft
  `groupOwnerHasPro(gid)` — das Gruppendokument liefert den Inhaber, dessen `entitlements`
  entscheiden. Mit dem Mitglieder-`get()` sind das drei bis vier von zehn erlaubten.
* **Lesen und Löschen bleiben in der ganzen Gruppe frei**, auch wenn die Berechtigung des
  Inhabers ausläuft. Sonst verlören Dritte den Zugriff auf ihre eigene Planung, weil jemand
  anderes nicht verlängert hat — und `pruneWeeks()` könnte alte Wochen nicht mehr aufräumen.
* `invites`: `create` nur für den Inhaber **mit** Pro.

**Löschung (Art. 17 DSGVO):** `deleteAccount()` entfernt `entitlements/{uid}` mit, bevor das
Kontodokument fällt. Dafür erlaubt die Regel dem Client genau eine Schreibart: `delete`.
`create` und `update` bleiben gesperrt — löschen kann sich der Nutzer nur selbst zum Nachteil
gereichen, und ein Store-Webhook würde das Dokument beim nächsten Ereignis neu schreiben. Ohne
diese Ausnahme bliebe ein verwaistes Dokument mit Personenbezug stehen, das niemand mehr
entfernen kann. Gelöscht wird über `deleteBestEffort()`: Der Normalfall ist, dass es das
Dokument gar nicht gibt — eine fehlende Berechtigung darf die Kontolöschung nicht blockieren
(dieselbe Falle wie in `docs/TROUBLESHOOTING.md` §48).

**Farbe:** Für Pro gibt es zwei Tokens, `--gold` (Fläche und Rand) und `--gold-ink` (Schrift,
je Theme ein eigener Wert). Gold kommt in der normalen UI **nicht** vor — es ist für Premium
reserviert und trägt im Light-Theme nicht als Fläche. Beide Werte sind gemessen, nicht
geschätzt (siehe `docs/TESTING.md`).

**Fehlerfall ist „kein Pro".** Der `onSnapshot`-Fehlerpfad setzt den Status auf `null`, statt
den letzten bekannten zu behalten. Das ist bewusst restriktiv (fail closed): Eine Berechtigung,
die bei Netz- oder Regelfehlern weiterläuft, ist keine Grenze. Der Preis ist, dass ein zahlender
Zugang bei einem Ausfall kurz auf Gratis fällt — sobald mit D2b tatsächlich gesperrt wird, ist
das erneut abzuwägen (`CLAUDE.md` §33: Sicherheit vor Komfort).

**Offen, bewusst unverändert:** Das JSON-LD im `<head>` nennt `"price": "0"`. Das bleibt richtig,
solange es nichts zu kaufen gibt — nachzuziehen ist es erst mit der Bezahlabwicklung (D7/Store),
nicht mit D1.

### Vorkochen: `buildBatchList()`

Dritte Auswertung desselben Wochenbestands, neben `buildShoppingList()` (Zutaten) und dem
Wochenplan selbst (Tage). Gruppiert nach Rezept-ID:

```
{ r, portions, days[] }
```

* `portions` = Σ Esser je Eintrag, wobei Esser = `uids.length` bzw. `shopPersons()`.
  Seit dem 15.08.2026 ist das zugleich die **Anzahl der Meals** — ein Eintrag ist eine Portion.
* `runs`/`perRun` (Kochdurchgänge) sind entfallen: Mit `portions` am Rezept fiel der Nenner weg,
  „4× kochen à 1 Portion" wäre nur eine umständliche Wiederholung der Zahl daneben.
* Zeitraum identisch zu `buildShoppingList()`: aktuelle Woche ab heute, nächste Woche ganz

Kein eigener State, kein neues Datenfeld — reine Ableitung. Die Ansicht (`openBatchCooking()`)
ist ein Modal ohne Bedienzustand, der Einstieg liegt im Überlaufmenü des Wochenplans
(`togglePlanMenu()`).

### Wochenarchiv `state.weekStats`

`pruneWeeks()` hält nur die aktuelle und die nächste Woche. Bevor eine vergangene Woche
verworfen wird, sichert `archiveWeek()` ihre Kennzahlen — bewusst **nur Zahlen**, keine
Meal-Referenzen und keine Fotos:

```
weekStats["2026-W29"] = { kcal, days, hit, target, d }
```

* `kcal` — Ø geplante Tageskalorien über die geplanten Tage
* `days` — Anzahl geplanter Tage (1–7)
* `hit` — Tage innerhalb ±10 % des Tagesziels
* `d` — **7-Zeichen-Maske** wie `"1101100"`, Index 0 = Montag bis 6 = Sonntag: welche
  Wochentage beplant waren. Erzeugt von `weekMaskOf(pl)`, gezählt von `maskDays(m)`.

  **Warum ein Festlängen-String und keine Zahl 0–127:** Jeder Unfall (`Number("")` → 0,
  `parseInt` auf Müll → `NaN`) würde lautlos zu „nichts geplant" und wäre von einer echt
  leeren Woche nicht mehr zu unterscheiden. `/^[01]{7}$/` trifft oder trifft nicht. Dazu
  ist `"1101100"` in der Firestore-Konsole lesbar, `108` nicht.

  **Seit 29.08.2026 (Paket 6, Schritte B3 und B5) läuft `d` durch den ganzen Sync.**
  `sanitizeWeekStats()` validiert die Maske (`/^[01]{7}$/` auf einem String), und
  `mergeWeekStats()` vereinigt sie über beide Geräte. Bis dahin schrieb `archiveWeek()` das
  Feld zwar, aber `sanitizeWeekStats()` kannte es nicht und warf es **beim eigenen Push**
  wieder weg — nicht erst beim Zusammenführen.

  Das war derselbe Fehlertyp wie in `docs/TROUBLESHOOTING.md` Punkt 115 („ein neues
  Sync-Feld braucht zwei Merge-Stellen") — nur an einer **dritten** Stelle, weil
  `sanitizeWeekStats()` jedes Objekt neu aufbaut und dabei alles Unbekannte verliert. Als
  eigener Punkt festgehalten in `docs/TROUBLESHOOTING.md` Punkt 138.

  **Kaputtes `d` kostet das Feld, nie den Datensatz** — sonst würde aus einem
  Übertragungsfehler eine gelöschte Woche. `d` und `days` korrigieren sich dabei ausdrücklich
  **nicht** gegenseitig: `sanitizeWeekStats()` läuft auf Bestandsdaten, und `days` gegen die
  Maske zu ziehen zerlegt jede Woche, die vor der Maske archiviert wurde. Der Widerspruch
  bleibt gewollt stehen — `days` trägt den Rückblick, `d` den Kalender.

`mergeArchived(alt, neu)` führt beim **lokalen** Archivieren den neu berechneten Datensatz
mit einem schon gespeicherten zusammen, statt ihn zu überschreiben: Masken werden vereinigt
(ODER), `days` nimmt das Maximum, `hit`/`target` bleiben als Paar zusammen. Das ist nicht
dasselbe wie `mergeWeekStats()` weiter unten — jenes führt zwei **Geräte** zusammen.
* `target` — **das damals gültige** mittlere Tagesziel (seit 13.08.2026, B10)

`target` ist der Kern: Ohne es misst der Rückblick jede vergangene Woche gegen das heutige
Ziel, und eine Zieländerung schreibt die Bedeutung der gesamten Historie um. Trainings- und
Ruhetage haben unterschiedliche Ziele, deshalb der Schnitt über die geplanten Tage.

`sanitizeWeekStats()` klemmt alle Werte, hält die **drei jüngsten Kalenderjahre**
(siehe „Archivfenster" unten — angeboten werden davon nur zwei) und übernimmt `target` nur
im plausiblen Bereich (500–20 000 kcal). Wochen ohne `target` sind vor B10 archiviert; der
Rückblick fällt dort auf das heutige Ziel zurück (`avgDailyTargetToday()`). Eine Migration
gibt es nicht — der alte Zielstand ist nicht rekonstruierbar.

Der Rückblick selbst (`rueckblickHtml()`) normiert jeden Balken auf **sein eigenes**
Wochenziel und kann das ±10-%-Band deshalb als feste Fläche zeichnen. Siehe
`docs/TROUBLESHOOTING.md` Punkt 72 für den Zustand davor.

#### Synchronisation (seit 25.08.2026)

**Bis dahin war `weekStats` gerätelokal** — es fehlte in `dataJSON()`, in der
`pushNow()`-Nutzlast und wurde in `onRemote()` nie gelesen. Ziel, Gewichte, Plan und Favoriten
liefen längst über die Cloud, der Rückblick nicht: Wer sich auf einem zweiten Gerät anmeldete,
hatte dort Streak 0 und ein leeres Diagramm. Diese Seite hat das früher **nicht erwähnt**, was
den Zustand wie eine Entscheidung aussehen liess — er war keine.

Das Feld läuft jetzt im Kontodokument mit. Weil `CloudSync.save` mit `mergeFields` schreibt und
ein Feld damit **ganz** ersetzt, wäre blosses Mitschreiben ein Datenverlust: Beide Geräte
archivieren dieselbe Vergangenheit unabhängig (`pruneWeeks()` läuft bei jedem Laden), das
zuletzt schreibende hätte die Wochen des anderen gelöscht. Zusammengeführt wird deshalb mit
`mergeWeekStats()`, wie bei `shares`, `weights` und `deleted`:

* **Vereinigung, nie Ersetzen.** Eine Woche, die nur ein Gerät kennt, bleibt.
* **Bei derselben Woche gewinnt der Eintrag mit mehr `days`** — wer mehr geplante Tage sah,
  hatte den vollständigeren Plan. Danach entscheiden `hit`, `kcal`, `target`.
* **Der Tiebreak ist rein wertbasiert und kennt kein „remote gewinnt".** Sonst nähme A den Wert
  von B und B gleichzeitig den von A — die beiden täuschten eine Runde lang. Wertbasiert kommen
  beide unabhängig zum selben Ergebnis. Belegt durch `tools/pruefstand-weekstats-sync.py`, das
  genau dafür `merge(A,B) === merge(B,A)` prüft.
* **Die Maske `d` steht bewusst nicht im Tiebreak.** Der Rang entscheidet, welche Seite ihre
  *Zahlen* durchsetzt; `d` wird unabhängig davon ODER-verknüpft, und `days` steigt danach auf
  `max(a.days, b.days, maskDays(d))`. Würde die Maske in den Rang eingehen („mehr Einsen
  gewinnt"), löschte man genau die Tage, die nur ein Gerät kennt — der Fehler, gegen den das
  Feld gebaut wurde. Hat keine Seite eine Maske, entsteht auch keine: `"0000000"` wäre eine
  erfundene Aussage über eine vor der Maske archivierte Woche.
* Anschliessend läuft `sanitizeWeekStats()` über das Ergebnis: Die Vereinigung kann Wochen
  aus einem dritten Jahr einbringen, wenn ein Gerät lange nicht geladen hat.

⚠️ **`mergeArchived()` und `mergeWeekStats()` sehen sich seit B5 sehr ähnlich — sie dürfen
trotzdem nicht zusammengelegt werden.** Sie unterscheiden sich in genau einem Punkt, und der
ist der ganze Sinn: `mergeArchived()` bevorzugt bei Gleichstand den **neuen** Lauf (`>=`), weil
der frisch gerechnete Wert der aktuellere ist. `mergeWeekStats()` darf das nicht — dort muss
der Gleichstand richtungsunabhängig aufgelöst werden, sonst nimmt Gerät A den Wert von B und
B gleichzeitig den von A. Wer die beiden vereinheitlicht, baut TROUBLESHOOTING 34/44 wieder ein.

### Erste Schritte: ein Gerüst, das den Bildschirmwechsel überlebt (seit 30.08.2026)

Bis dahin baute `renderOnboardStep()` bei **jedem** Schritt die ganze Ansicht über
`view.innerHTML` neu. Seither entsteht das Gerüst einmal je Durchlauf:

```
.onb > .onb-top + .onb-stage-wrap > .onb-stage + .onb-foot
```

`renderOnboardStep()` tauscht nur noch den Inhalt der Bühne und gleicht Fuß und Fortschritt
an Ort und Stelle ab. Vier Dinge hängen daran:

* **Der Höhenübergang** (`onbSwapStage()`): alte Höhe messen → am **Wrapper** fixieren →
  Bühne tauschen → neue Höhe setzen. Am Wrapper, weil die Bühne bei jedem Schritt neu
  entsteht und keinen Vorher-Zustand hätte (`docs/TROUBLESHOOTING.md` 39). Freigegeben wird
  über `transitionend` **und** einen Sicherheitstimer — bleibt die Höhe inline stehen, ist
  die Bühne auf der Höhe von gestern eingefroren und ein längerer Schritt wird lautlos
  abgeschnitten.
* **CSS statt WAAPI**, und das ist kein Geschmack: Die globale `reduced-motion`-Regel
  erzwingt `transition-property: opacity, color, background-color, border-color, box-shadow`.
  Eine `height`-Transition ist damit unter „weniger Bewegung" kostenlos abgeschaltet.
* **Gerichteter Wechsel**: `onbGo(delta)` setzt `pendingOnbDir`, `renderOnboardStep()` reicht
  es an `slideIn(stage, dir)` — 16 px, Dauer und Kurve aus `MOTION`, dasselbe Muster wie
  Reiter- und Wochenwechsel. Die alte, hartkodierte und richtungslose `onbin`-Regel auf
  `.onb-stage` ist entfallen; die Keyframes bleiben für die gestaffelten Kacheln.
* **`renderOnboardStep(gleicherSchritt)`**: Eine Kachel antippen ist **kein**
  Bildschirmwechsel. In diesem Fall kein `slideIn`, und `.onb-still` legt die gestaffelte
  Kachel-Einblendung still. Vorher flog der ganze Bildschirm bei jedem Tipp neu ein — wer
  auf dem Trainingsschritt vier Tage antippt, sah das viermal.

⚠️ **Was der Umbau NICHT leistet:** Der Weiter-Knopf steht am Ende immer noch woanders — die
Bildschirme sind unterschiedlich hoch, gemessen 64 bis 538 px. Er wandert jetzt weich statt
zu springen. Ein wirklich stehender Knopf bräuchte einen fixierten Fuß; das ist eine eigene
UX-Entscheidung und war in Paket 5 nicht vorgesehen.

⚠️ **Zwei Knoten, die jetzt überleben, brauchen Schutz vor sich selbst:**
`animateOnbProgress()` führt eine **Laufmarke** (`onbProgressLauf`). Solange `#view` bei
jedem Schritt ersetzt wurde, schrieb eine noch laufende rAF-Schleife in einen abgehängten
Knoten und war wirkungslos. Jetzt bleibt der Knoten stehen — ohne Laufmarke überholen sich
mehrere Schleifen gegenseitig (gemessen: „Schritt −54 von 8").

#### Archivfenster: drei Jahre behalten, zwei anbieten (seit 29.08.2026)

Vorher war es ein **rollendes halbes Jahr** (`slice(-26)`). Der Fortschritt-Kalender zeigt
ganze Jahre — ein rollendes Fenster hätte ihm den Januar weggeschnitten, sobald der Juli da
ist. Getrimmt wird nach dem **ISO-Jahr-Präfix des Schlüssels**, nicht nach echtem
Kalenderdatum: `"2026-W01"` kann real im Dezember 2025 liegen.

```javascript
function archivJahre(anzahl) { … }                          // die eine Quelle
function archivJahreBehalten() { return archivJahre(3); }   // was gespeichert bleibt
function archivJahreZeigen()   { return archivJahre(2); }   // was angeboten wird (weightYears)
```

⚠️ **Funktionen, nicht `const`** — und das ist kein Stil, sondern Pflicht:
`sanitizeWeekStats()` hängt an `load()`, und `load()` läuft in `let state = load()` sehr
früh auf Modulebene. Eine `const` an dieser Stelle wäre dort noch in der temporalen Totzone
und brächte die App zum Stillstand — bei sauberem Syntax-Check. Passiert am 29.08.2026,
`docs/TROUBLESHOOTING.md` Punkt 139.

**Die beiden Zahlen sind mit Absicht verschieden — das ist der Kern.** Das Fenster bestimmt
sich zur Laufzeit über `new Date().getFullYear()`. Wären sie gleich, verschwände am
1. Januar schlagartig ein Jahrgang, den der Nutzer am 31. Dezember noch im Umschalter hatte
— beim blossen Laden. Und weil `weekStats` in `dataJSON()` steht, löst genau das einen
**Push** aus: Ein einziges Gerät, das am Neujahrstag startet, käppte das Archiv auch in der
Cloud und auf allen anderen Geräten, unwiederbringlich.

Mit dem Puffer fällt am Stichtag nur ein Jahrgang, der bereits **ein volles Jahr lang
unsichtbar** war. Es verschwindet nie etwas, das gestern noch zu sehen war. Kosten: rund
3,7 KB — ein Jahrgang à 53 Wochen à knapp 70 Byte.

Verworfen wurde, gar nicht mehr zu trimmen (das Archiv wüchse unbegrenzt) und ein rollendes
Wochenfenster (bringt das Januar-Problem zurück, deshalb schon am 25.08.2026 abgelehnt).

ℹ️ **Wer das Fenster für zu gross hält, weil der Rückblick nur acht Balken zeichnet, irrt.**
`rueckblickHtml()` zeigt acht Wochen (`zielKeys.slice(-8)`), aber die **Streak-Schleife
unmittelbar davor läuft rückwärts durch das gesamte Archiv**, solange die Wochen lückenlos
`STREAK_MIN_DAYS` erfüllen. Ein Nutzer mit zwei Jahren durchgehender Planung hat einen Streak
von über 100 Wochen — ein kürzeres Fenster würde ihn schlicht kappen. Das Archiv wird also
schon heute in seiner vollen Tiefe genutzt, nicht erst mit dem Kalender. Die datenschutz&shy;-
rechtliche Einordnung dazu: `docs/DATENSCHUTZ-INTERN.md`, Abschnitt 2a.

⚠️ **Die Anzeige muss ihre Jahre über `archivJahreZeigen()` beziehen** — nie
über `Object.keys(weekStats)` und nie über ein aus dem Schlüssel gerechnetes Datum. Beides
höbe den Puffer wieder auf: Im ersten Fall bietet der Umschalter das Pufferjahr mit an, im
zweiten driften Trimmung und Darstellung auseinander (Wochen, die der Umschalter unter 2026
zeigt, wären unter 2025 weggeworfen worden).

Belegt durch `tools/pruefstand-wochenmaske.py`, Abschnitt 6 — darunter die Zeile, die die
Entscheidung selbst misst und dabei ohne Zeitreise auskommt: *Was der Umschalter heute
anbietet, muss im morgigen Behalten-Fenster noch vorkommen.* Gegenprobe mit
`archivJahreBehalten()` auf zwei Jahrgänge gestellt: vier Zeilen fallen durch, darunter
„verloren: 2025".

**Wer die Jahre anbietet: `weightYears()` — ein Umschalter für beide Karten (seit
30.08.2026, B6).** Die Fortschritt-Seite bekommt keinen zweiten Jahrwechsler für den
Kalender; `weightYears()` liefert weiterhin die Jahre mit Messung oder Jahresziel plus das
laufende Jahr, **zusätzlich die Archivjahre aus `archivJahreZeigen()`**. Damit hat auch ein
Konto ohne eine einzige Wägung einen Umschalter, der sein Planungsjahr kennt, und beide
Karten teilen sich `state.viewYear`.

Zwei Feinheiten, die dabei zusammengehören:

* Die Archivjahre werden **gefiltert** (`zeigen.indexOf(y) !== -1`), nicht aus den
  Schlüsseln übernommen — sonst stünde das Pufferjahr im Umschalter, und der Puffer wäre
  keiner mehr. Das Jahr kommt aus dem Schlüssel-Präfix, dieselbe Trimm-Regel wie oben.
* **Die Gewichtsjahre bleiben ungefiltert.** Das Fenster gilt für `weekStats`; eine zehn
  Jahre alte Messung ist ein eigenes Datum mit eigener Löschlogik und darf nicht
  mitverschwinden.

Belegt durch `tools/pruefstand-jahresumschalter.py`; die Gegenprobe gegen `91c202b` fällt durch.

#### Die Ansicht: ein Band, zwei Leser (seit 30.08.2026, B7/B8)

`renderProgress()` zeichnet seit dem 30.08.2026 drei Karten statt zwei —
`rueckblickHtml() + kalenderHtml() + weightHtml()`, dazu `initKalender()` neben
`initRueckblick()`. Reihenfolge: acht Wochen, dann das Jahr, dann das Gewicht; von der
kurzen zur langen Sicht. **Kein fünfter Reiter** — der Kalender beantwortet dieselbe Frage
wie der Rückblick („wie lief es bisher?"), nur über einen längeren Zeitraum.

`kalenderHtml()` ist eine echte `<table>` mit `table-layout: fixed`, sieben Zeilen
(Wochentage) mal 52 oder 53 Spalten. **Kein Grid und kein `display: contents` auf
Tabellenelementen**: das nimmt Screenreadern die Tabellenrollen, und genau die sind hier
die ganze A11y-Antwort — 371 `aria-label` wären keine. Sichtbar beschriftet sind jeder
zweite Monat (Drei-Buchstaben-Kürzel) und Mo/Mi/Fr/So; der volle Name steht in jeder Zelle
als `.visually-hidden` daneben.

**`kalWoche(wk)` ist die eine Quelle für die Bits** und kennt drei Antworten:

| Rückgabe | Bedeutung | Darstellung |
|---|---|---|
| `{ mask: "1101100", tage: 4 }` | Tage bekannt — aus `state.plans` (laufende Wochen, über `weekMaskOf()`) oder aus `weekStats[..].d` | gefüllt bzw. leer mit Kante |
| `{ mask: null, tage: n }` | Woche geplant, Tage unbekannt (vor dem 29.08.2026 archiviert, kein `d`) | neutral gefüllt (grau) |
| `null` | über die Woche ist nichts bekannt | transparent, ohne Kante |

Die mittlere Zeile ist die inhaltlich wichtige: Eine solche Woche als sieben Nullen zu
zeichnen wäre eine Aussage, die niemand erhoben hat. Zukunft und die Zeit vor der ersten
Nutzung sehen dagegen absichtlich gleich aus — beides ist „keine Aussage", ein Unterschied
wäre eine erfundene.

**`dayStreak()`** zählt Tage am Stück über dieselbe Funktion. Ist heute noch nichts geplant,
beginnt die Zählung bei gestern — der eine bewusste Off-by-one; ein Vormittag darf keine
Serie abräumen. Eine Woche ohne Maske **beendet** den Lauf (unterschätzen statt lügen),
Deckel bei 400, Anzeige ab zwei Tagen. Die Wochenserie (`STREAK_MIN_DAYS = 5`) bleibt
unangetastet: andere Einheit, andere Aussage, und die Flamme gehört ihr allein.

Die Doppelung zwischen beiden Zählweisen wird über den geteilten Maskenzugriff vermieden,
**nicht** über gemeinsame Streak-Logik — die Regeln sind verschieden.

**Tastatur: ein Tabstopp, Pfeiltasten darin** (roving `tabindex`). Genau eine Zelle trägt
`tabindex="0"` — bevorzugt *heute*, im Vorjahr die erste; die übrigen `-1`. `initKalender()`
bewegt den Fokus mit den Pfeiltasten sowie `Home`/`End` und zieht den Tabstopp mit, sodass
man beim Zurückkommen dort landet, wo man war. Der `focus`-Handler zeigt denselben Tipp wie
Klick und Hover.

371 fokussierbare Zellen wären das Gegenteil von barrierefrei: Wer die Karte nur
überspringen will, drückte 371-mal Tab. Umgekehrt wäre eine rein mausbediente Zelle für
sehende Tastaturnutzer eine echte Lücke — die Tabellensemantik hilft nur, wer ohnehin einen
Screenreader benutzt. Gemessen in `tools/pruefstand-kalender.py`, Abschnitt 9 und 10.

⚠️ **Die Kartenschale `.wg-col` hat `overflow: hidden`.** Ein zu breites Band läuft deshalb
nicht über das Dokument, es wird lautlos abgeschnitten. Wer Layoutfehler am Dokument misst,
sieht davon nichts (`tools/pruefstand-kalender-layout.py`, gemessen wird
`tab.scrollWidth <= wrap.clientWidth`).

**Zwei Merge-Stellen, nicht eine.** `onRemote()` deckt den laufenden Betrieb ab; der
Baseline-Merge in `startCloudSync()` den Start. Fehlt das Feld dort, ist die Vereinigung
wirkungslos — der Baseline-Push läuft direkt danach und ersetzt das Cloud-Feld mit dem
lokalen Stand. Siehe `docs/TROUBLESHOOTING.md` Punkt 115.

Grössenordnung: rund 159 Wochen (drei Jahrgänge) à knapp 70 Byte, also gut 10 KB —
unkritisch gegen `CLOUD_DOC_MAX = 900000`.

### Merkmale eines Meals: `tags[]` und `mealPrep`

Zwei optionale Felder, seit 13.08.2026. Sie sind die Grundlage für den Meal-Filter, die
kuratierte Bibliothek und den späteren Auto-Wochenplaner — ohne sie ist keines davon baubar.

* **`tags`**: Array aus **festen Schlüsseln** — `highprotein`, `lowcarb`, `vegetarisch`,
  `vegan`, `glutenfrei`, `laktosefrei` (Quelle: `RECIPE_TAGS`). Bewusst **keine Freitext-Tags**:
  die schriebe jeder Nutzer anders (`lowcarb`/`Low Carb`/`low-carb`) und weder Filter noch
  Planer könnten damit rechnen. Die **Schlüssel** stecken in Nutzerdaten und geteilten Meals und
  dürfen sich nie ändern; die Beschriftungen dürfen es.
* **`mealPrep`**: Boolean, „lässt sich vorkochen".

**Ein drittes Feld `difficulty` (Aufwand, 1–3) gab es einen Tag lang** und ist am 13.08.2026
wieder entfernt worden: Es wurde gesetzt und angezeigt, aber von nichts ausgewertet — weder vom
Filter noch vom geplanten Auto-Planer. Ein Feld ohne Abnehmer ist Pflegeaufwand ohne Gegenwert
(es muss sanitisiert, synchronisiert, dokumentiert und in jedem Prüfstand mitgedacht werden).
`sanitizeRecipe()` **löscht** einen Alt-Wert aktiv, statt ihn nur nicht mehr zu setzen — sonst
kopierte `Object.assign()` ihn aus Altdaten und geteilten Meals dauerhaft weiter.

Die Faustregel daraus: Ein Datenfeld wird angelegt, wenn ein konkretes Feature es liest — nicht,
weil es später einmal nützlich sein könnte.

### Nährwerte an den Zutaten — und warum sie dort stehen müssen

Ein Rezept, dessen Zutaten keine eigenen Nährwerte tragen, lässt sich **nicht nachrechnen**:
Wer beim Bearbeiten 200 g Reis auf 150 g ändert, bekommt weiterhin die alten Gesamtwerte
angezeigt. Sie sind dann still falsch. Deshalb trägt jede Zutat der `COOKBOOK`-Rezepte
`kcal`, `carbs`, `protein`, `fat`.

**Die Bezugsgröße unterscheidet sich je Einheit** (`ingContrib()`):

| Einheit | Nährwert gilt | Faktor |
|---|---|---|
| `g` / `ml` | je **100** | `menge / 100` |
| `st` / `el` / `tl` | je **Einheit** | `menge` |

`tools/rezept-makros.py` schlägt die Werte in `FOODS` nach, rechnet die Rezeptsumme gegen und
meldet Abweichungen über 12 % (Garverluste und Rundungen liegen darunter). Makros **unter 5 g**
werden dabei nicht prozentual bewertet: 1,5 g gerechnetes Fett gegen 2 g angegebenes sind −20 %,
obwohl die Rundung auf ganze Gramm richtig ist — ein Werkzeug mit einem dauerhaft unbehebbaren
Treffer wird überlesen, und mit ihm der echte. `--anwenden`
schreibt sie in die `COOKBOOK`-Zutaten — aber **nur**, wenn keine Zutat mehr ohne Wert ist:
Halbe Daten sind schlimmer als keine, weil die Summe dann still danebenliegt.

**Zwei Fallen, beide am 15.08.2026 real aufgetreten:**

* **Geschätzte statt gerechneter Werte.** Die ersten neun Katalog-Rezepte lagen bis zu 86 %
  daneben. Ohne Gegenrechnung fällt das niemandem auf — die Zahlen sehen plausibel aus.
* **Falsch zugeordnetes Lebensmittel.** „Zuckerschoten" matchte auf „Zucker" (400 statt
  42 kcal). Präfixe zählen deshalb nur an der **Wortgrenze**. Ein falscher Treffer ist
  gefährlicher als ein fehlender, weil er nicht auffällt.

Daraus folgt für die Rezepte: **Zutatennamen müssen den `FOODS`-Namen entsprechen** („Zwiebeln",
nicht „Zwiebel"; „Ei, Größe M", nicht „Eier"), und **Öl gehört als Zutat, nicht in den
Freitext** — als Freitext fällt es aus jeder Rechnung, und das Fett lag um bis zu 69 % zu
niedrig.

### Rezeptbuch: `COOKBOOK` als Katalog (15.08.2026)

Ein **Katalog, kein Bestand.** Die kuratierten Meals liegen in der Konstanten `COOKBOOK` und
**nicht** in `state.recipes`. Gezeigt werden sie im Meals-Reiter unter „Rezeptbuch"; erst beim
Übernehmen entsteht eine Kopie im eigenen Konto.

**Warum nicht der ganze Katalog direkt in die Sammlung:** 36 fremde Meals im eigenen Bestand
erdrücken die eigenen, kosten bei jedem Konto denselben Cloud-Speicher, und ein Veganer
schleppt zwei Drittel mit, die er nie kocht. Der Katalog kostet nichts, bis jemand zugreift.

```
COOKBOOK[i].id    → dauerhafter Schlüssel (NICHT der Dateiname, siehe img)
COOKBOOK[i].img   → Dateiname in img/library/ (das eigens erzeugte Bild)
COOKBOOK[i].photo → Schlüssel aus PHOTOS (Rückfall, wenn kein eigenes Bild da ist)
state.recipes[i].lib = "<COOKBOOK id>"   → Herkunft der Kopie
```

`lib` ist **die Bibliotheks-ID, kein Boolean.** Damit lässt sich später eine korrigierte
Fassung zuordnen („In der Bibliothek gibt es eine neuere Version") — mit einem Ja/Nein-Feld
wüsste hinterher niemand mehr, welches Rezept gemeint war. Die Katalog-`id` wird beim
Übernehmen **nicht** als Rezept-`id` verwendet: `state.recipes` braucht eigene Schlüssel
(`uid()`), sonst kollidieren zwei Konten in derselben Gruppe.

`isAdopted()` prüft über `lib`, nicht über den Namen — wer die Kopie umbenennt, soll sie nicht
ein zweites Mal angeboten bekommen.

**Der Katalog wird seit dem 24.08.2026 vollständig gezeigt** — `paintCookbook()` und
`renderRecipes()` lesen `COOKBOOK`, nicht mehr `cookbookVisible()`. Die Einschränkung durch das
Ernährungsprofil entsteht jetzt über **vorbelegte Filter-Chips** und ist damit sichtbar und
abschaltbar (Begründung in `docs/PRODUCT.md`).

`seedCookbookFilters()` belegt `cookbookFilters` aus `state.goal.diet`/`.avoid` vor. Zwei Dinge
daran sind bewusst so:

* **Die Schlüssel brauchen keine Übersetzung.** `DIETS`/`AVOIDS` und `RECIPE_TAGS` verwenden
  dieselben Bezeichner — es fehlt nur das Präfix `"tag:"`, das `recipeFilterHtml()` setzt.
* **Auslöser ist eine Signatur, kein Flag.** `cookbookSeedSig` ist `diet + "|" + avoid.join(",")`;
  ändert sie sich, wird neu vorbelegt. Ein Flag nach dem Muster von `collapsedCatsSeeded` müsste
  an **drei** Stellen von Hand zurückgesetzt werden — erste Schritte, „Ziele neu berechnen" und
  `onRemote()` (Cloud-Snapshot). Eine davon übersieht der nächste Umbau, und die Ansicht filterte
  danach still nach dem alten Profil weiter. `avoid` wird für die Signatur aus `AVOID_KEYS` neu
  aufgebaut, damit die Tippreihenfolge sie nicht verändert (dieselbe Überlegung wie bei
  `toggleAvoid()`).

Ein von Hand abgewählter Chip überlebt innerhalb der Sitzung jeden weiteren Aufbau; erst ein
Profilwechsel belegt neu vor.

**`cookbookVisible()` bleibt unverändert** und behält seine drei Aufrufer, bei denen das Profil
eine **harte** Grenze ist: `addStarterMeals()` (`docs/TROUBLESHOOTING.md` 91), `pickerQuellen()`
und der Auto-Planer. Durchlässig wird nur die Ansicht, nie die Automatik.

**Klappbare Kategorien: nur die Textsuche schaltet sie ab.** `filtering` in `paintCookbook()`
und `paintRecipeGroups()` hängt seither allein an der Suche (`!!q`), nicht mehr an aktiven Chips.
Sonst wären die Kategorien praktisch nie mehr klappbar — ein aktiver Chip ist hier ja jetzt der
Regelfall. Die Klapp-**Vorbelegung** (`collapsedCatsSeeded`) prüft weiterhin beides: auf einem
gefilterten Bestand festgeschrieben, wäre „erste Kategorie mit Inhalt" die erste des Filters.

Im Meals-Reiter selbst wird der eigene Bestand unverändert **nicht** nach dem Profil gefiltert
(siehe `docs/PRODUCT.md`).

**Warum kein eigener Reiter:** Der `ux-reviewer` hat den Entwurf am 15.08.2026 geprüft und
zwei tragende Einwände gebracht. Erstens sind die vier Reiter Tätigkeiten — orientieren,
planen, verwalten — und „entdecken" ist der Schritt **vor** dem Verwalten, nicht daneben; ein
übernommenes Rezept landet ohnehin in den eigenen Meals. Zweitens hätte der ursprüngliche Plan
(Fortschritt-Reiter opfern, Gewicht zurück auf Home) genau den Zustand wiederhergestellt, den
B8 zwei Tage zuvor aufgelöst hatte. Der Umschalter nutzt deshalb dieselbe gleitende Pille wie
der Wochenwechsel (`.week-switch`/`.ws-ind`, `syncWeekSwitchPill()`, `CLAUDE.md` §11).

Mit Pro wächst genau diese Ansicht auf die große Bibliothek, die monatlich wechselt — deshalb
dieselbe Struktur und derselbe Übernahme-Weg.

#### Der Katalog wird nachschlagbar (17.08.2026)

Der Zwei-Personen-Gruppentest vom 16.08.2026 hinterließ im Bestand 61 Rezepte bei nur 51
Namen - zehn Paare mit gleichem `lib`, verschiedener `id`. Zwei Zuflüsse trugen dazu bei, und
beide sind seither trockengelegt:

1. **Der Planer kopierte.** `planAdopt()` legte für jedes eingeplante Katalog-Rezept eine
   Bestandskopie an - drei Planerläufe an einem Abend erzeugten drei neue Meals. `planAdopt()`
   ist **ersatzlos entfallen**; `planId()` in `autoPlanWeek()` liefert seither einfach `r.id`,
   auch für Katalog-Kandidaten. Ein Planerlauf lässt `state.recipes.length` unverändert.
2. **Der Gruppenbeitritt glich nicht ab.** `copyOwnRecipesToGroup()` lud jedes eigene Meal
   hoch, ohne den Gruppenbestand zu kennen - zwei Konten mit gleichem `lib` (Startmeals sind
   je Ernährungsform fest verdrahtet, `STARTER`) erzeugten garantiert Dubletten.

**Grund für das frühere Kopieren war eine inzwischen überholte Annahme:** `normalizePlan()`
speichert im Plan nur IDs und filterte jeden Eintrag gegen `state.recipes` - ein Slot, der auf
eine Katalog-`id` zeigte, wäre beim nächsten Laden lautlos verschwunden. Das Rezeptbuch ist
aber mitgeliefert, auf jedem Gerät identisch und trägt vollständige `ingredients`/`nutrition` -
ein Planeintrag darf also direkt auf eine Katalog-`id` zeigen. Drei Bausteine tragen das:

```
getRecipe(id)      → state.recipes zuerst, bei Fehltreffer Rückfall auf COOKBOOK.find()
normalizePlan()     → das ids-Set enthält jetzt auch alle COOKBOOK-IDs
rewritePlanIds(von, nach)  → ein Plan-Verweis wird in ALLEN gespeicherten Wochen umgebogen,
                              inkl. state.planned (Planer-Gedächtnis)
```

`recipeIndex` (der render()-Cache für `getRecipe()`) bleibt bewusst **nur** aus
`state.recipes` gebaut - der Katalog kommt erst beim Fehltreffer dazu, nicht als weitere 34
Einträge in jedem Render-Durchlauf.

**„Meals" enthält damit nur noch, was der Nutzer selbst angelegt oder bewusst übernommen hat**
(siehe `docs/PRODUCT.md`). Der Wochenplan greift auf Bestand *und* Katalog zu.

**`rewritePlanIds()` ist der gemeinsame Helfer für zwei Stellen**, die beide einen Plan-Verweis
umbiegen müssen, weil eine `id` nicht mehr gilt:

* `adoptFromCookbook()` - nach dem Übernehmen (auch aus einem Wochenplan-Slot heraus, per
  Übernehmen-Knopf im Nur-Lese-Zweig der Meal-Ansicht) zeigt der Plan sonst weiter auf das
  unveränderte Original, und eine spätere Bearbeitung der Kopie bliebe unsichtbar. Das
  Rückgängig-Machen biegt in Gegenrichtung zurück.
* `copyOwnRecipesToGroup()` - siehe unten.

**Katalog-Objekte dürfen nie mutiert werden.** `getRecipe()` kann seit diesem Umbau ein
`COOKBOOK`-Objekt liefern statt einer eigenen Kopie. Drei Aufrufer schreiben auf ihr Ergebnis
(Foto per Drag & Drop, Foto per Einfügen, `deleteRecipe()`) und tragen deshalb einen Riegel
`if (!state.recipes.some(x => x.id === r.id)) return;` - praktisch unerreichbar, weil
Katalog-Rezepte nicht in der Meals-Liste stehen, aber ein späterer Umbau soll den Katalog nicht
still beschädigen können. Aus demselben Grund prüft `onRecipesRemote()` eine entfernte Löschung
direkt gegen `state.recipes`, nicht über `getRecipe()` - das würde für eine gelöschte
Katalog-`id` sonst fälschlich „noch vorhanden" melden.

**Gruppenbeitritt gleicht ab.** `copyOwnRecipesToGroup()` liest zuerst den vorhandenen
Gruppenbestand — seit dem 28.08.2026 ausdrücklich vom SERVER
(`CloudSync.loadRecipesFromServer(["groups", gid])`, Rückfall auf `loadRecipes`, falls ein
älterer Service-Worker-Stand die Funktion noch nicht kennt; `docs/TROUBLESHOOTING.md` 126)
— und baut eine Map
`lib → vorhandene id`. Ein eigenes Meal mit `lib` wird **nicht** hochgeladen, wenn die Gruppe
bereits eines mit demselben `lib` trägt - stattdessen biegt `rewritePlanIds()` die eigenen
Planeinträge auf die schon vorhandene Gruppen-`id` um, **vor** dem Hochladen des Plans (sonst
wirft `normalizePlan()` sie beim nächsten Laden weg). Meals **ohne** `lib` (selbst angelegte)
werden nie dedupliziert - ein Namensabgleich würde fremde Meals verschlucken; zwei Leute dürfen
je eine eigene „Banane" haben.

**Einmalige Migration (`dedupeAgainstCatalog()`, `state.dedupeV1`).** Räumt Altlasten aus der
Zeit vor diesem Umbau: eine Bestandskopie mit `lib`, die ihrem - über `sanitizeRecipe()`
sanitisierten - Katalog-Original in `name`, `category`, `nutrition`, `ingredients`, `steps`,
`time`, `tags` und `mealPrep` entspricht, wird gelöscht; ihre Planeinträge wandern vorher
(nicht nachher - sonst verwirft `normalizePlan()` sie) auf die Katalog-`id`. Ein eigenes Foto
macht die Kopie nicht abweichend. Unangetastet bleiben veränderte Kopien, Meals ohne `lib`,
Barcode-Produkte (`quick`) und Favoriten. Läuft idempotent (`state.dedupeV1`, nur lokal
persistiert, kein Cloud-Feld) und **in einer Gruppe gar nicht** (`if (syncGid) return;`,
ohne das Flag zu setzen) — sonst räumte sie den **gemeinsamen** statt des eigenen Bestands auf.
Bis zum 28.08.2026 stand hier `syncGid && !syncHandshakeOk`, sie lief also in der Gruppe,
sobald der Handshake stand; `state.dedupeV1` ist aber ein Geräte-Flag, und jedes weitere Gerät
liess sie erneut auf fremden Bestand los (`docs/TROUBLESHOOTING.md` 128). Aufgerufen in
`enterApp()` (lokaler Modus) und in `startCloudSync()` direkt nach `syncHandshakeOk = true`,
vor dem Baseline-`pushNow()` — dort greift der Ausstieg jetzt sofort, sobald `syncGid` gesetzt
ist. Nach dem Verlassen einer Gruppe holt sie es auf dem eigenen Bestand nach.

Ausschneide-Prüfstand: `tools/pruefstand-katalog-plan.py` → `pruefstand-katalog-plan.html`.

#### `photo`: kuratierte Bildwahl statt Stichwortraten (15.08.2026)

`photoFor()` prüft seit dem Ausbau auf 30 Rezepte in dieser Reihenfolge:

```
r.image (eigenes Foto, safeImage)
  → libPhoto(r)   (img/library/<datei>, das eigens erzeugte Bild)
  → r.photo       (Schlüssel in PHOTOS)
  → PHOTO_RULES → CAT_PHOTO → PHOTOS.neutral
```

#### `img` und `libPhoto()`: die eigenen Bilder der Bibliothek

```
COOKBOOK[i].img = "<dateiname>.webp"   → liegt in img/library/
LIB_IMG: Map(COOKBOOK id → Pfad), einmalig aufgebaut
libPhoto(r) → LIB_IMG.get(r.lib) || LIB_IMG.get(r.id)
```

**Der Dateiname steht am Eintrag, statt aus der `id` abgeleitet zu werden.** Eine `id` darf
einen Umlaut tragen (`rührei-avocadobrot`), ein Dateiname sollte keinen — die Ableitung
müsste in JavaScript dieselbe Slug-Regel nachbauen, die `tools/meal-bilder.py` in Python
anwendet. Zwei Fassungen derselben Regel laufen auseinander.

**Die Kopie speichert den Pfad nicht mit.** `libPhoto()` fragt über `lib` (Kopie) bzw. `id`
(Katalogeintrag) im Katalog nach. Ein später ersetztes oder zurückgezogenes Bild wirkt damit
sofort überall, und in den Nutzerdaten — Cloud, geteilte Meals — liegt kein Pfad, der eines
Tages ins Leere zeigt.

**Ein Eintrag ohne `img` ist vorgesehen, kein Fehler.** Bilder, die die Sichtprüfung nicht
bestehen, werden ausgemustert; die Karte fällt dann auf `photo` bzw. die mitgelieferten Fotos
zurück statt auf eine 404-Fehlstelle.

#### Der erste Bestand: `addStarterMeals()` statt `SEED` (15.08.2026)

**`SEED` ist ersatzlos entfallen**, ebenso `isExample()`, `clearExamples()` und die
Namensauflösung `SEED_IMG`/`seedPhoto()`. Die vier Gerichte stehen jetzt im Katalog (siehe
`COOKBOOK`), ihre Bilder laufen über `LIB_IMG`.

```
load()               → recipes: []            (kein Profilwissen vorhanden)
finishOnboarding()   → addStarterMeals()      (diet ist jetzt bekannt)
STARTER[diet]        → 5 ids, durch fitsDiet() gefiltert und aufgefüllt
copyFromCookbook(r)  → { …r, id: uid(), lib: r.id }
```

**Warum der Zeitpunkt der eigentliche Punkt ist:** `load()` läuft vor dem Onboarding — dort
Meals einzusetzen heißt, sie ohne Kenntnis der Ernährungsform zu wählen (siehe
`docs/TROUBLESHOOTING.md` 91).

**`copyFromCookbook()` ist der EINE Kopierweg** vom Katalog in den Bestand, benutzt von
`adoptFromCookbook()` und von den Startmeals. Zwei Kopierwege würden irgendwann verschiedene
Felder mitnehmen, und der Unterschied fällt erst beim Sync auf.

**Bedingung `state.recipes.length === 0`.** Sonst bekäme ein Cloud-Nutzer, der auf einem zweiten
Gerät das Onboarding durchläuft, fünf Dubletten.

**Startmeals sind echte Meals.** Sie tragen `lib`, werden synchronisiert und beim Gründen einer
Gruppe mitkopiert — die beiden `isExample()`-Filter in `mergeRemoteRecipes()` und
`copyOwnRecipesToGroup()` sind entfallen. Das ist der bewusste Preis dafür, die Sonderrolle
„mitgelieferte Attrappe" abzuschaffen: Der Nutzer hat sie nicht selbst gewählt, aber sie wurden
für sein Profil ausgewählt, und `isAdopted()` zeigt sie im Rezeptbuch korrekt als „In deinen
Meals".

**Folge für Bestandsnutzer:** Wer die vier alten Beispiele im Bestand hat, behält sie als normale
Meals. Sie verlieren den Chip „Beispiel" und ihr Bild (die Namensauflösung ist weg). Keine
Migration, kein Datenverlust.

#### Die Regel dahinter: ein Schlüssel darf in Nutzerdaten, ein Pfad nicht

`sanitizeRecipe()` **löscht `img` aktiv** — wie `difficulty` und `portions`. Es ist ein Feld der
mitgelieferten Daten, nie eines von Nutzerdaten:

| Feld | in Nutzerdaten? | warum |
|---|---|---|
| `lib`, `photo` | **ja** | stabile Schlüssel, werden zur Anzeigezeit aufgelöst |
| `img` | **nein** | ein Pfad. `Object.assign()` trüge ihn beim Kopieren in Bestand, Cloud und geteilte Meals; ein später ersetztes Bild wäre dort für immer eingefroren, bis er ins Leere zeigt |

Die Kopie verliert dadurch nichts: Sie trägt `lib` und findet ihr Bild darüber — auch die fünf Startmeals.

**Nicht in den Service Worker.** Die Bilder gehören **nicht** in `SHELL_ASSETS` — der
`fetch`-Handler liefert eigene Assets ohnehin cache-first und legt sie beim ersten Gebrauch
nach. Im Precache würden sie den Kaltstart um über ein Megabyte verteuern, für Bilder, die
viele Nutzer nie sehen. **Aber:** Wird ein Bild *ausgetauscht*, muss `VERSION` in `sw.js`
hoch — cache-first heißt sonst, dass Wiederkehrer die alte Datei behalten. Für *neue*
Dateien gilt das nicht.

**Warum ein eigenes Feld nötig war:** `PHOTO_RULES` sucht Stichwörter im *Namen* und ist für
selbst angelegte Meals richtig — im Katalog greift es aber sichtbar daneben, weil die Namen
Zutaten nennen. „Grüner Smoothie mit Spinat" landete über die Regel `spinat` auf dem
**Salatfoto**, „Schoko-Protein-Quark" über `quark` auf **Porridge**, „Dattel-Nuss-Bissen mit
Kakao" über `kakao` auf einem **Getränk**. An den Regeln zu drehen wäre der falsche Hebel: Sie
wirken auf jedes Nutzer-Meal, und Teilwort-Kollisionen sind dort die bekannte Falle
(`CLAUDE.md` §22). Gesetzt ist `photo` deshalb nur bei den elf Einträgen, bei denen die Regel
falsch liegt — nicht überall, sonst wäre die Zuordnung doppelt gepflegt.

Es ist ein **Schlüssel**, kein Pfad. Ein unbekannter Wert fällt still auf die Regeln zurück,
statt ein leeres Bild zu erzeugen; `safeImage()` bleibt für `image` zuständig und lässt
ohnehin nur `data:`-URIs zu, könnte also nie einen Bibliothekspfad tragen.

**In `sanitizeRecipe()` wird nur die FORM geprüft** (`/^[a-z]{2,20}$/`), nicht die Gültigkeit.
Ein Abgleich gegen `PHOTOS` wäre dort ein **TDZ-Fehler**: `sanitizeRecipe()` läuft schon in
`let state = load()`, `PHOTOS` ist erst weiter unten als `const` deklariert. Das ist keine
Lücke — `photoFor()` schlägt in der Konstante nach. Das Feld überlebt die Übernahme
(`Object.assign`) und wandert damit in Cloud und geteilte Meals, weshalb die Form überhaupt
geprüft wird.

**Wenn die eigenen Bilder aus `img/library/` kommen, ist `photo` der Anschlusspunkt** — dann
entscheidet die Kuration weiterhin, nur mit einer anderen Quelle.

#### Merkmal und Badge müssen dasselbe sagen

Der Tag `highprotein` (gepflegt, filterbar) und das Badge „Proteinreich" (gerechnet, aus
`macroBadges()`) stehen auf derselben Karte. Im Katalog müssen sie sich **deckungsgleich**
verhalten, sonst widerspricht die Karte ihrem eigenen Filter. Maßgeblich ist die Rechnung:

| Badge | Schwelle |
|---|---|
| Proteinreich | Protein ≥ 30 % der Makro-Kalorien |
| Low Carb | Kohlenhydrate ≤ 15 % **und** ≤ 20 g |

Vier der ersten neun Rezepte trugen `highprotein` bei 17–25 % Proteinanteil; die Tags sind am
15.08.2026 entfernt worden. Bei **selbst angelegten** Meals gilt das nicht — dort darf der
Nutzer taggen, wie er will. Geprüft wird es im Prüfstand (`docs/TESTING.md`).

### Ernährungsprofil: `state.goal.diet` und `state.goal.avoid` (15.08.2026)

```
state.goal.diet   = "alles" | "vegetarisch" | "vegan"     // genau eine, optional
state.goal.avoid  = ["glutenfrei", "laktosefrei"]         // Teilmenge, optional
```

**Zwei Felder statt einer Mehrfachauswahl:** `diet` ist eine Ernährungsform und schließt ein
(vegan ist immer auch vegetarisch), `avoid` sind Einschränkungen quer dazu. Eine gemeinsame
Liste erlaubte „vegetarisch + vegan", was keinen Sinn ergibt.

**Die Werte sind dieselben Schlüssel wie in `RECIPE_TAGS`** — so vergleichen Filter und Planer
ohne Übersetzungstabelle dazwischen.

Drei Helfer, und `fitsDiet()` ist der einzige, den Aufrufer benutzen dürfen:

| Funktion | Aufgabe |
|---|---|
| `dietOk(r, diet)` | Ernährungsform. `vegetarisch` lässt vegane Gerichte ausdrücklich zu |
| `avoidOk(r, avoid)` | Einschränkungen, UND-verknüpft, harte Grenze |
| `fitsDiet(r, goal)` | die Verknüpfung — **hier fragen, nie die beiden darüber** |
| `toggleAvoid(list, key)` | An/Abwählen; baut die Liste aus `AVOID_KEYS` **neu auf** |

`toggleAvoid()` steht als eigene Funktion da, obwohl sie nur ein Klick-Handler braucht: Sie ist
so im Prüfstand messbar, und sie tut mehr, als sie aussieht — durch den Neuaufbau aus
`AVOID_KEYS` ist die Reihenfolge unabhängig von der Tippreihenfolge. Ein umsortiertes Array wäre
gegenüber `canonJSON()` ein dauerhafter Diff und damit ein Endlos-Schreibzyklus (dieselbe Falle
wie bei `sanitizeTags()`).

**Nicht gesetzt bleibt nicht gesetzt.** `sanitizeGoal()` löscht unbekannte Werte, statt auf einen
Standard zu fallen, und `onbGoalInput()` schreibt „alles ohne Einschränkung" gar nicht erst —
sonst bekäme jedes Bestandsziel allein durchs Laden zwei neue Felder und damit einen
überflüssigen Cloud-Schreibvorgang (dieselbe Überlegung wie bei `tags`/`mealPrep`).

**`computeGoal()` reicht beide Felder ausdrücklich durch.** Seine Rückgabe zählt ihre Felder
einzeln auf — ein nicht genanntes Feld wäre nach jedem Neuberechnen verschwunden, und das Profil
überlebte weder eine Wiegung (`syncGoalWeight()`) noch „Ziele neu berechnen". Genau diese Falle
ist dort schon für `bodyfat` dokumentiert.

**Invariante, seit 24.08.2026: Jedes frisch berechnete Ziel geht durch `sanitizeGoal()`.**

```js
state.goal = sanitizeGoal(computeGoal(…));   //  IMMER, nicht nur meistens
```

Beide Aufrufer halten sich daran — der Wizard-Schritt `result` und `syncGoalWeight()`. Der Grund
ist kein Stilempfinden: `computeGoal()` gibt `diet`/`avoid` unverändert weiter, also auch das
`undefined`, mit dem `onbGoalInput()` „keine Einschränkung" ausdrückt. `JSON.stringify` verschluckt
das — Firestore lehnt dafür **das ganze Kontodokument** ab, und der Push wiederholte den Wurf bei
jedem `save()`. Ausführlich in `docs/TROUBLESHOOTING.md`, Ziffer 108.

`sanitizeGoal()` ist idempotent (im Prüfstand belegt), ein zusätzlicher Durchlauf kostet also
nichts. Wer eine dritte Stelle anlegt, die `computeGoal()` aufruft, zieht die Hülle mit.

**Onboarding:** ein Bildschirm (`diet`) zwischen Zielwahl und Ergebnis. Vorbelegt mit „Alles",
weil das die häufigste Antwort ist und niemand tippen soll, um weiterzukommen — anders als bei
den übrigen Fragen ist das keine unterstellte Angabe, sondern der Zustand, in dem die App ohne
das Feld ohnehin läuft. Kein `onbAutoNext`: Nach der Form kommen noch die Zusatz-Schalter.

### `portions` ist entfallen — ein Meal ist eine Portion (15.08.2026)

Nährwerte und Zutatenmengen beschreiben seitdem denselben Gegenstand. Wer mehr braucht, plant
das Meal zweimal ein; das ist zugleich die Grundlage dafür, dass der Auto-Planer in einer Gruppe
unterschiedliche Kalorienziele über die **Anzahl** der Einträge abbilden kann (`docs/PRODUCT.md`).

Der Ausbau war kein Aufräumen, sondern eine **Fehlerbehebung**: Das Feld wirkte nur an einer
einzigen Stelle als Teiler (individuell zugewiesene Gerichte in der Einkaufsliste). Die
Tagesbilanz kannte es gar nicht, und bei „für alle" — dem Normalfall — wurde es übersprungen.
Ein Meal mit `portions: 2` zählte also mit den Nährwerten **einer** Portion und kaufte die
Zutaten für **zwei** ein. Genau dieser Fehler steckte im eigenen Beispieldatensatz.

**Die Mengen werden deshalb umgerechnet, nicht nur das Feld gelöscht:** `sanitizeRecipe()` teilt
bei `portions > 1` jede Zutatenmenge durch den Wert und entfernt das Feld danach. Zwei
Eigenschaften machen das im Sanitizer statt in einer einmaligen Migration möglich:

* **Idempotent** — nach dem ersten Durchlauf fehlt `portions`, jeder weitere Aufruf ist wirkungslos.
  Damit ist es egal, wie oft und über welchen Eingang (Cloud, Teilen-Link, Import, Gruppe) ein
  Rezept läuft; jedes Gerät kommt zum selben Ergebnis.
* **Robust gegen Unsinn** — `nutNum()` liefert für `0`, negative Werte und Text eine `0`, die
  Bedingung `> 1` fängt sie ab. Keine Division durch null, keine erfundenen Mengen.

Freitext-Zutaten („Salz, Pfeffer") haben keine Menge und bleiben unberührt. Gerundet wird auf
eine Nachkommastelle, damit aus 200 g ÷ 3 nicht 66,66666667 wird.

`sanitizeTags()` lässt ausschließlich bekannte Schlüssel durch, entfernt Duplikate und stellt
die **feste Reihenfolge aus `RECIPE_TAG_KEYS`** her. Letzteres ist kein Schönheitsdetail: Ein
umsortiertes Array wäre gegenüber `canonJSON()` ein dauerhafter Diff und damit ein
Endlos-Schreibzyklus in `syncRecipes()`.

**Nicht gesetzte Felder bleiben ungesetzt** (`delete` statt Standardwert). Sonst bekäme jedes
Bestands-Meal allein durchs Laden ein neues Feld — und damit einen überflüssigen
Cloud-Schreibvorgang je Rezept.

Am Sync ändert sich nichts: `syncRecipes()` schreibt das ganze Rezept-Objekt, die Felder wandern
automatisch mit; dasselbe gilt für das Teilen per Link (`shareMealPayload()` überträgt `r`
vollständig, der Import läuft durch `sanitizeRecipe()`). Auch die Firestore-Regeln bleiben
unverändert — `users/{uid}/recipes/{id}` prüft den Besitzer, nicht einzelne Felder.

Eine Migration gibt es bewusst nicht: Meals ohne Merkmale sind schlicht Meals ohne Merkmale.

### Barcode-Schnellzugriff: `barcode` und `quick`

Ein per Barcode-Scan eingeplantes Fertigprodukt (`quickAddByBarcode()`) ist ein ganz normaler
Eintrag in `state.recipes` — kein eigener Datentyp, siehe „Bewusste Produktentscheidung:
Barcode-Schnellzugriff" in `docs/PRODUCT.md`. Zwei zusätzliche, optionale Felder:

* `barcode`: die gescannte EAN. Dient der **Dedupe**: vor dem Neuanlegen sucht
  `quickAddByBarcode()` per `state.recipes.find(r => r.barcode === code)` nach einem
  bestehenden Eintrag und plant bei Treffer direkt dessen ID ein, statt ein Duplikat zu
  erzeugen. Auch beim Fallback über `openRecipeForm(null, prefill)` (unsichere OFF-Daten)
  bleibt `barcode` erhalten, damit ein späterer erneuter Scan denselben Eintrag findet.
* `quick: true`: blendet den Eintrag im Reiter „Meals" aus. Maßgeblich ist dafür
  `libraryRecipes()` (`state.recipes` ohne `quick`) — genutzt von `paintRecipeGroups()`,
  vom Zähler `#recipe-count` und von der Sichtbarkeit des Suchfelds, damit Zähler, Leerzustand
  und Liste dieselbe Menge beschreiben. Seit dem Sheet-Umbau nutzt **auch `openPicker()`** diese
  Menge — eine Auswahlliste, die mit jedem gescannten Riegel länger wird, ist das Gegenteil von
  „Entscheidungen abnehmen"; über Plan, Einkaufsliste und Druck bleiben die Produkte erreichbar.
  Wird **nur** beim stillen Anlegen mit vollständigen OFF-Daten gesetzt —
  bestätigt der Nutzer stattdessen über das normale Formular, bleibt der Eintrag sichtbar, weil
  er ihn aktiv über den Standardweg angelegt hat.

Diese Felder sind additiv: `sanitizeRecipe()` kopiert unbekannte Felder unverändert durch
(`Object.assign({}, r)`), Plan, Einkaufsliste, PDF-Export und Ziel-Ringe kennen ausschließlich
`getRecipe(id)` und bleiben dadurch unverändert funktionsfähig.

### Schnelleintrag für Stück-Artikel: `qf`

Ein Apfel oder eine Banane soll ohne Meal-Formular in einen Slot kommen. `quickAddPiece(day,
meal, food)` benutzt dafür **exakt dasselbe Muster** wie `quickAddByBarcode()` — ein stilles
`quick: true`-Meal, nur ist die Datenquelle lokal (`pieceFoods()`) statt Open Food Facts und
damit immer vollständig; einen Formular-Fallback braucht es hier nicht.

* Drittes optionales Feld **`qf`**: der normalisierte Food-Schlüssel (`foodNorm(Name + Synonyme)`)
  als Dedupe-Anker — das Gegenstück zu `barcode`. Ohne ihn entstünde bei jedem Antippen ein neues
  Rezeptdokument, und die Einkaufsliste zeigte dreimal „1× Banane" statt einmal „3× Banane".
* Das Meal trägt `portions: 1`, seine `nutrition` gilt **je Stück**, und seine einzige Zutat ist
  `{name, grams: 1, unit: "st", …Nährwerte}`. Genau daran hängt die Einkaufsliste:
  `buildShoppingList()` aggregiert über `name|unit`, `qtyLabel()` macht „2× Banane",
  `shopCategory()` sortiert in die Warengruppe. Nichts davon ist ein Sonderfall.
* Aufgeräumt wird es vom bestehenden `pruneQuickRecipes()` (21 Tage TTL, nur wenn nirgends mehr
  eingeplant) — **kein zweiter Aufräumpfad.**
* Das Dedupe wirkt **lokal**, nicht über Geräte hinweg: legen zwei Geräte einer Gruppe offline
  dieselbe Banane an, entstehen zwei Rezepte mit gleichem `qf`, und die Einkaufsliste zeigt zwei
  Zeilen „1× Banane" statt einer mit „2×". Genau dasselbe gilt seit immer für `barcode` und ist
  bewusst nicht gelöst: eine geräteübergreifende Zusammenführung müsste fremde Plan-Einträge
  umschreiben, und das darf ein Aufräumschritt nicht. Nach 21 Tagen räumt sich der Rest von selbst.

Mengen werden nicht im Eintrag gezählt: zwei Bananen sind zwei Einträge im Slot. `unassign`
arbeitet index-basiert (`data-slot-src="tag:slot:index"`), doppelte IDs in einem Slot sind
deshalb unproblematisch, und die Einkaufsliste fasst sie ohnehin zusammen.

### Zutaten-Datenbank `FOODS`

Handgepflegte Rundwerte für generische Lebensmittel, bewusst kein Auszug aus einer fremden
Datenbank (Lizenz, siehe Kommentar im Code). Format:

```text
[Name, kcal, KH, Protein, Fett, Einheit?, Synonyme?, GrammJeStueck?]
```

Werte je 100 g/100 ml, bei `Einheit: "st"` je Stück; fehlende Einheit = `"g"`. Synonyme stehen nur
im Suchschlüssel, nie in der Anzeige. Das achte Feld ist das **Stückgewicht** (verzehrbarer Anteil
eines mittelgroßen Stücks) und steht absichtlich direkt neben den Nährwerten, auf die es sich
bezieht — eine zweite Tabelle „Name → Gewicht" wäre eine Namensverknüpfung, die bei jedem
Umbenennen still bricht.

Darauf setzen drei Helfer auf:

* `foodList()` — lazy Index mit `{name, kcal, carbs, protein, fat, unit, stk, key}`.
* `rankFoods(list, q, max)` — die gemeinsame Rangfolge (Wortanfang → Wortanfang später →
  mittendrin, ab 2 Zeichen). `foodSearch()` (Zutatenzeile) und `pieceSearch()` (Schnelleintrag)
  sind nur zwei Aufrufer davon; beide verhalten sich deshalb identisch.
* `pieceFoods()` — die zählbaren Einträge: entweder schon je Stück erfasst (`unit === "st"`, z. B.
  das Ei) oder mit Stückgewicht. Deren 100-g-Werte werden **einmal** aufs Stück hochgerechnet.
  `PIECE_TOP`/`pieceTop()` ist die kurze feste Auswahl, die der Picker ohne Suchbegriff anbietet.
  Sichtbar ist sie dort nur aufgeklappt: Der Abschnitt „Schnell" ist ein Aufklapper, dessen
  Zustand in einer Variablen des jeweiligen Pickers liegt (`pqOpen`, geschlossen vorbelegt) und
  **nicht** in einem `<details>` — die Liste wird bei jedem Tastendruck über `innerHTML` neu
  gebaut, ein DOM-Zustand ginge dabei verloren. Ab zwei Zeichen und bei leerer Meal-Auswahl
  (`libEmpty`) ist er zwingend offen und die Kopfzeile nur Beschriftung — dieselbe Unterscheidung
  wie `.cathead` / `.cathead.static` im Rezeptbuch.

`offServingSize(p)` (neben `fetchOffNutrition()`) wertet OFF's `serving_size`/`quantity`-Feld
aus und liefert `{grams, count, serving}` oder `null`:

* `grams`: das Gewicht **einer** Einheit — bei „1 Stück (65 g)" und „6 x 65 g" das eines
  einzelnen Stücks, bei reinem „500 g" das der ganzen Packung.
* `count`: nur bei erkannter Stückzahl gesetzt, sonst `null`.
* `serving`: `true`, wenn der Wert aus `serving_size` (echte Portionsangabe) stammt, `false`
  bei `quantity` (Packungsgröße). `serving_size` hat Vorrang.

Genutzt an zwei Stellen: `applyBarcode()` (Zutatenzeile im Meal-Formular) schaltet bei erkannter
Stückzahl die Einheit auf „Stück" und rechnet die vier Nährwerte auf je-Stück um;
`quickAddByBarcode()` rechnet auf **eine Portion** hoch (`ss.grams`, gegen 100 g) und akzeptiert
dafür nur `count || serving` — eine reine Packungsgröße („500 g" Nudeln, „1 l" Milch) ist keine
Portion und führt stattdessen in den Formular-Fallback, siehe `docs/TROUBLESHOOTING.md` Ziffer 41.
Dieser Fallback (`openRecipeForm(null, prefill)`) nimmt die gefundenen Nährwerte als vorbefüllte
Zutaten-Zeile (je 100 g, ohne Menge) mit — `updateMacroSum()` summiert die Meal-Nährwerte, sobald
der Nutzer die Menge einträgt.

### Live-Kamera: Bühnenformat und Fokus (`scanBarcodeLive()`)

Die einzige Live-Kamera-Stelle der App. Drei Dinge hängen zusammen und dürfen nur gemeinsam
geändert werden:

1. **Angeforderte Constraints.** `facingMode: {ideal: "environment"}`, `width/height` ideal
   1920×1080 und `aspectRatio: {ideal: hochkant ? 3/4 : 4/3}` — die Haltung des Geräts entscheidet.
   Alles bewusst `ideal`: eine harte Forderung bräche mit `OverconstrainedError` auf Kameras, die
   das Format nicht können, obwohl ein anderes völlig ausreicht.
2. **Die Bühne folgt dem echten Stream, nicht dem Breakpoint.** `.scanvid` trägt
   `--scan-ar` (Breite/Höhe als reine Zahl); `syncStage()` setzt sie aus
   `track.getSettings()` (Rückfall: `video.videoWidth/Height`, weil Safari `getSettings()` nicht
   immer gefüllt liefert). Ein entprellter `resize`-Listener zieht sie beim Drehen nach und fordert
   `aspectRatio` **nur dann** neu an, wenn Bild und Haltung wirklich quer zueinander liegen —
   ein `applyConstraints()` ohne Not lässt das Bild sichtbar zucken.
   `syncStage()` setzt außerdem `--scan-h`: die **gemessene** freie Höhe (Ebene minus Kopfzeile,
   Hinweis, Fuß, Abstände, Polster). Daraus rechnet das CSS die Breite
   (`min(100%, calc(var(--scan-h) * var(--scan-ar)))`) — so bleibt das Seitenverhältnis erhalten,
   ohne dass die Bühne den Kasten aus dem Bildschirm schiebt. Ein fester Anteil der Bildschirmhöhe
   war hier messbar falsch, siehe `docs/TROUBLESHOOTING.md` Punkt 63.
   Im Querformat auf niedrigen Bildschirmen (`orientation: landscape` und `max-height: 560px`)
   wechselt `.scanbox` per Grid von der Spalte auf **Bild links, Bedienelemente rechts** — gleiche
   Elemente, gleiche Reihenfolge, rund doppelte Bildfläche. Eine Hochformat-Sperre ist im Web auf
   iOS nicht möglich und eine Gegenrotation würde das Bild kippen (Punkt 65).
3. **Fokus.** `focusModes()` liest `track.getCapabilities().focusMode`, `applyFocus(mode)` setzt
   ihn über `applyConstraints({advanced: [{focusMode}]})`. Beim Start `continuous`; ein Tipp aufs
   Bild fordert `single-shot` nach. Beides nur, wenn die Capability da ist — sonst bleibt auch der
   Hinweistext stumm und verspricht nichts. Alles in `try/catch` und ohne `await`: die API kennt
   derzeit nur Chromium.

`cleanup()` bleibt die einzige Abbaustelle und meldet auch den `resize`-Listener und den
Entprell-Timer ab.

## Firebase Security

`firebaseConfig` ist kein Geheimnis.

Firebase-Web-Keys identifizieren das Projekt, autorisieren aber keinen Zugriff.

Die tatsächliche Sicherheit entsteht durch:

* Authorized Domains
* Firebase Authentication
* Firestore Security Rules

`firestore.rules` im Repository ist nur eine Vorlage.

Verbindlich ist der aktuell veröffentlichte Stand in der Firebase Console.

## Namensdualität

Sichtbar:

* Paddy's Mealplan
* Meal

Intern:

* `wochenkueche`
* `recipe`

Diese Namen nicht ohne Migrationsplan ändern.

Betroffen sind u. a.:

* `wochenkueche_v1`
* `wochenkueche_profile_v1`
* `app: "wochenkueche"`
* `state.recipes`
* `getRecipe`
* `data-tab="recipes"`
* `.rcard`
* `.recipes`

Alte Daten und Teilen-Links müssen kompatibel bleiben.

## Bilder

`photoFor(r)` verwendet diese Reihenfolge:

1. eigenes Bild
2. `PHOTO_RULES`
3. `CAT_PHOTO`
4. `PHOTOS.neutral`

`PHOTOS` und `PHOTO_CREDITS` müssen dieselben Schlüssel besitzen.

Neue Bilder nur mit belegter freier Lizenz.

### `thumbHtml(r, cls, eager)`

`eager` lässt `loading="lazy"` weg und setzt `decoding="sync"`. **Nur** der Plan-Slot in
`renderPlan()` übergibt `true` — dort stehen höchstens 21 winzige Thumbnails, alle sofort im
Blickfeld; `loading="lazy"` verschiebt selbst ein längst dekodiertes Bild um mindestens einen
Frame, sichtbar als Aufblitzen bei jedem `render()`. Meal-Raster (`cardImageHtml`) und die
Picker-Liste bleiben bei `lazy` — dort können deutlich mehr Bilder gleichzeitig im DOM stehen.

### Das Logo ist eine Datei, kein Base64

`--logoL` verweist auf `img/logo.png` (220×220 RGBA, 45 KB). Bis zum 10.08.2026 stand das Bild
als 60-KB-Base64 direkt in der CSS-Variablen — also im render-blocking `<style>`-Block, den jeder
Aufruf vollständig parsen muss, bevor das erste Pixel erscheint. Der CSS-Block ist dadurch von
264 KB auf 204 KB gefallen, `index.html` von 933 KB auf 860 KB.

`--logoD` und `--logo` bleiben unverändert davor geschaltet; die Light-/Dark-Mechanik ist nicht
berührt (beide Themes nutzen dieselbe Datei).

**`prepareLogoForPdf()` hängt daran.** Die Funktion braucht die rohen PNG-Bytes, um daraus
RGB- und Alpha-Streams für den PDF-Writer zu bauen, und las sie früher per `getComputedStyle`
aus `--logoL`. Sie holt sie jetzt per `fetch("img/logo.png", { cache: "force-cache" })`. Wer den
Pfad des Logos ändert, muss **beide** Stellen anfassen. Details und die `file://`-Einschränkung:
`docs/TROUBLESHOOTING.md`, Punkt 67.

### Was der Service Worker vorlädt

`SHELL_ASSETS` in `sw.js` enthält nur noch die Hülle: `index.html`, Manifest, das Logo und die
vier Icons. Die 32 Meal-Fotos und `vendor/zxing.min.js` sind seit dem 10.08.2026 **nicht** mehr
im Precache — sie kommen über den Cache-First-Zweig des `fetch`-Handlers nach und liegen danach
genauso dauerhaft im Cache. Das spart 927 KB bei der Installation.

Das Firebase-SDK aus `vendor/firebase/` (~690 KB) steht aus demselben Grund **nicht** im
Precache. Es fällt seit D4 unter den Cache-First-Zweig, weil es jetzt same-origin ist — und
genau der Seitenaufruf, der es holen würde, holt es ohnehin selbst. Ein Precache zöge die
690 KB nur auf die Installation vor, ohne einen Abruf zu sparen.

Alles wird Cache-First ausgeliefert: Wird ein Foto oder das Logo ausgetauscht, muss `VERSION`
hoch (aktuell `pm-v6`). Siehe `docs/TROUBLESHOOTING.md`, Punkt 68.

## Wochenplan auf dem Handy

Am Rechner ist `.week` ein Raster und die Tagesleiste `.daybar` steht auf `display: none`. Unter
680 px wird daraus ein waagerecht schnappender Streifen (`scroll-snap-type: x mandatory`, eine
Tageskarte pro Bildschirmbreite) mit einer klebenden Tagesleiste darüber.

### `initCarousel(scroller, bar, panelList, onChange, opts)`

Koppelt Streifen und Leiste über `scrollLeft` — bewusst nicht über `scrollIntoView`, das die
Seite auch senkrecht verschieben würde. Zwei Aufrufer: der Wochenplan (`.week` + `.daybar`) und
die Wochenziele auf der Startseite (`.wg-cols` + `.wgbar`, `{fixedHeight: true}`).

Alles, was pro Bild gebraucht wird, misst `measure()` **einmal** in einem Batch
(`lefts`, `widths`, `heights`, `maxScroll`, `clientW`, `step`). Der Scroll-Pfad liest danach nur
noch aus diesen Arrays. Grund: vorher wurden pro Bild `offsetLeft`/`offsetWidth`/`offsetHeight`
von bis zu sieben Karten gelesen **und** `style.height` bedingungslos zurückgeschrieben — ein
erzwungenes Layout pro Bild, genau während gewischt wurde.

`renderPlan()` baut die Leiste bei **jedem** `render()` neu. `measure()` läuft deshalb am Ende
jedes `initCarousel()`-Aufrufs, nicht in einer einmaligen Initialisierung. `resetCarousels()`
trennt vorher die alten `ResizeObserver`.

Zwei Nachkorrekturen sorgen dafür, dass der Streifen nie zwischen zwei Tagen liegen bleibt —
`fitHeight()` ändert die Höhe des Snap-Behälters mitten im Lauf, und der Browser kann sein
Snap-Ziel dabei verlieren:

* `settle()` in `go()` — für den programmatischen Sanftlauf (Tippen auf die Tagesleiste).
* `settleNative()` — für den Finger-Wisch, ausgelöst über `scrollend` (Rückfall: 220-ms-Timeout).
  Solange ein Finger auf dem Streifen liegt, wird nicht korrigiert.

Beide setzen hart auf `lefts[…]`, beide zielen auf den Tag, den die Tagesleiste ohnehin anzeigt.
Siehe `docs/TROUBLESHOOTING.md`, Punkt 42.

`resetInactiveScroll(idx)` dreht dabei den **senkrechten** Stand aller nicht aktiven Panels
(`.slots`) auf 0 zurück: Wer zu einem anderen Tag wischt, will ihn sehen und nicht dort
weiterlesen, wo er zuletzt war. Bewusst erst nach dem Einrasten — während der Geste ist die
verlassene Karte noch halb im Bild, ein Sprung wäre dort sichtbar.

**Optionen:**

* `fixedHeight` — Streifenhöhe auf das Maximum **aller** Karten (Wochenziele: zwei Karten, die
  gleich hoch wirken sollen).
* `noFit` — `fitHeight()` steigt sofort aus und räumt eine etwaige Inline-Höhe weg. Der
  Wochenplan nutzt das, weil er seine Höhe vom Sheet bekommt (siehe unten). Damit entfällt der
  Schreibvorgang, der Punkt 42 verursacht hat.

### Wochenplan mobil: Seiten-Scroll, klebende Bilanz

Im Handy-Zweig (`max-width: 680px`) scrollt die **Seite**. Die Tageskarte hat bewusst **keinen
eigenen Scroller** — ein Scroll-Container im Snap-Streifen fängt die Wischgeste ab und gibt sie
nicht mehr her (`docs/TROUBLESHOOTING.md`, Punkt 58). Wer dort `overflow`, `touch-action` oder
`overscroll-behavior` ergänzt, schaltet das Wischen zwischen den Tagen ab.

Zwischenzeitlich war der Reiter eine Fläche fester Höhe mit innerem Scroller. Das ist
zurückgebaut; `--sheet-top` und `--foot-h` sind ersatzlos entfallen.

Was fest bleiben soll, klebt per `position: sticky`:

* **Tagesleiste** — `.daybar`, `top: var(--head-h)`, unverändert seit jeher.
* **Tagesbilanz** — `#day-bal`, `bottom: calc(var(--tabbar-h) + 8px + safe-area)`. Sie liegt
  **außerhalb** von `.week`: Der Streifen ist wegen `overflow-x` auch senkrecht ein
  Scroll-Kontext, ein `sticky` darin richtete sich an ihm aus statt am Bildschirm. Nur mobil —
  am Rechner trägt jede der sieben Spalten ihre eigene Bilanz in der Karte.

`paintDayBalance(dayKey)` füllt die Leiste über dasselbe `dayNutHtml()` wie die Karte (kein
zweiter Renderpfad) und hängt am **vorhandenen** `onChange`-Rückruf von `initCarousel()`. Bei
einem leeren Tag liefert `dayNutHtml()` nichts; die Leiste bekommt dann `.is-empty` und
verschwindet, statt leer stehen zu bleiben.

Der Höhensprung beim Wischen (Ziffer 42) wird von **`fixedHeight`** abgefangen: Die Streifenhöhe
wird einmal auf das Maximum aller Karten gesetzt statt bei jedem Scroll-Bild nachgeführt. Das
laufende Nachführen war die Ursache.

Der Makro-Aufklapper löst auf dem Handy **kein** `render()` aus, sondern zeichnet nur die Leiste
neu — sonst würfe der Neuaufbau von `#view` die Scrollposition der Seite durcheinander.
Fallunterscheidung am Vorhandensein von `#day-bal`.

**Die Tagesbilanz ist ihr eigener Aufklapper.** `goalBarHtml()` nimmt einen optionalen
`toggle`-Parameter (`{ day, open }`); nur `dayGoalsHtml()` übergibt ihn, die Balken der
Wochenziele und im Rechner bleiben unverändert.

Der Knopf ist dabei **nur der Chevron**, aufgespannt über ein `::after { inset: 0 }` auf `.gm-tap`
— dasselbe Stretched-Link-Muster wie bei `.ing-view-name` und `.rcard-open`. Die ganze `.gm` zum
`<button>` zu machen wäre kürzer gewesen, hätte aber zwei Dinge gebrochen: `<button>` erwartet
Phrasing Content (`.gm` enthält drei `<div>`, darunter eine `role="progressbar"`), und der Name
eines Knopfes bildet sich aus seinem gesamten Inhalt — „Kalorien" wäre doppelt vorgelesen worden.

Wert und Chevron liegen zusammen in `.gm-vwrap`: `.gm-r` ist `space-between` und auf genau zwei
Kinder ausgelegt. Ein drittes verteilte den Raum auf zwei Lücken, der Wert stand dann 80 px vor
dem Pfeil in der Mitte.

**Slot-Überschriften** tragen dieselben Symbole wie die Kategorien im Meals-Reiter, über denselben
Helfer `iconSvg()`. `MEAL_ICON` ist eine eigene Zuordnung und nicht `CAT_ICON` durchgereicht:
Slots sind keine Kategorien, und „Hauptgericht" fällt auf `mi` **und** `ab`.

In `dayGoalsHtml()` stehen die Makros **vor** der Kalorienzeile, damit der Auslöser beim
Aufklappen stehen bleibt (Punkt 59).

### Tagesleiste als Segmented Control

Die Fläche liegt auf der Leiste, die Knöpfe sind transparent, und eine Pille (`.db-ind`) gleitet
darunter. Ihre Position ist eine **reine Funktion von `scrollLeft`**, synchron im
`scroll`-Ereignis geschrieben (nicht im `requestAnimationFrame`-Block — iOS-Safari drosselt den
während des Momentum-Scrolls). Dadurch braucht sie keine Transition, und
`prefers-reduced-motion` greift von selbst über `scroll-behavior: auto`.

Zustände der Leiste:

* `.db-b.is-today` — Punkt; auf dem Handy der einzige sichtbare „heute"-Träger, das Wort steht
  nur noch im `aria-label`.
* `.db-b.is-train` — Trainingstag; zeigt am **aktiven** Knopf ein Hantel-Icon.
* `.daybar.is-train` — von `setActive()` gespiegelt, sobald der aktive Knopf ein Trainingstag
  ist. Färbt Pille und aktive Schrift blau (`--train` / `--train-contrast`).

Trainingstag und Überschreitung werden nie allein über Farbe transportiert: Rot und Blau haben
nur 1,07:1 Kontrast. Auf der Karte tragen Rand, Icon und Wort, in der Leiste Pillenfarbe,
Hantel-Icon und `aria-label`.

### Anker-Regel für den angezeigten Tag

> Ein Sprungziel wird **nur** beim Reiterwechsel auf den Wochenplan und beim Wochenwechsel
> gesetzt. Jeder andere `render()` hält die Position.

Umgesetzt über drei Modul-Variablen: `pendingDayTarget` (Index oder `"today"`), `pendingWeekDir`
(Richtung des Übergangs) und `pendingWeekX` (die zu haltende waagerechte Scrollposition).
`renderPlan(sameTab)` verbraucht die Werte einmalig.

Praktisch: Reiterwechsel → heute. Aktuelle → nächste Woche → Montag. Zurück → heute. Meal
einplanen, entfernen oder ein Cloud-Snapshot → Position bleibt, keine Bewegung.

`sameTab` wird von `render()` **als Parameter durchgereicht**, weil `lastRenderTab` dort schon
auf `"plan"` gesetzt ist, bevor `renderPlan()` läuft — ein Reiterwechsel wäre daraus nicht mehr
erkennbar.

**Reihenfolge der Scroll-Wiederherstellung (Flacker-Schutz).** `render()` liest `.week`s
`scrollLeft` **vor** `view.innerHTML` in `pendingWeekX`, schreibt es aber nicht mehr selbst
zurück. `renderPlan()` setzt `weekStrip.scrollLeft = pendingWeekX` **direkt nach**
`view.innerHTML`, noch **vor** `resetCarousels()`/`initCarousel()`. Grund: `initCarousel()` misst
Position und Höhe (`markActive`/`fitHeight`/`syncIndicator`) sofort beim Aufbau — lag die
Wiederherstellung wie früher erst in `render()` **nach** `renderPlan()`, sahen diese Messungen
kurz den „Montag/Position 0"-Zwischenstand direkt nach `view.innerHTML`, und die CSS-Transitions
von `.db-b`/`.db-ind::after` machten die anschließende Korrektur als Zucken sichtbar. Die
zwischenzeitlich falsche Streifenhöhe verfälschte zusätzlich `window.scrollTo(0, keepY)` in
`render()`. Mit `pendingWeekX` sehen alle Messungen sofort die richtige Position.

`weekJumpDone` (früherer Sperr-Flag, der die `render()`-eigene `.week`-Wiederherstellung für
einen Sprung-Durchlauf abschaltete) entfällt ersatzlos: `render()` schreibt `.week` gar nicht
mehr selbst, es gibt nichts mehr zu sperren. Die Anker-Regel wirkt trotzdem weiter — springt
`renderPlan()` selbst (Reiterwechsel/Wochenwechsel), läuft `planCarousel.go(target, true)`
**nach** der `pendingWeekX`-Wiederherstellung und überschreibt die Position bewusst noch einmal
mit dem Sprungziel.

`.wg-cols` (Meal-Raster) ist von dieser Umstellung nicht betroffen — dort bleibt die
Wiederherstellung wie bisher in `render()`, nach dem jeweiligen `render*()`-Aufruf.

### Schiebe-Schema für gleichrangige Ansichtswechsel

Alle Wechsel zwischen gleichrangigen Ansichten (Wochentage, Home „Heute/Diese Woche",
„Aktuelle/Nächste Woche", untere Tab-Leiste) folgen derselben Bewegungssprache: Segmented
Control mit gleitender Pille plus gerichteter Enter-Bewegung des Inhalts. Drei Bausteine, je
nach DOM-Lebensdauer der Leiste:

* **`initCarousel()` / `.db-ind`** — für `.daybar` und `.wgbar`. Die Pille ist eine reine
  Funktion von `scrollLeft` (siehe oben), keine eigene Transition nötig.
* **`slideIn(el, dir)`** — gemeinsamer Enter-Helfer (WAAPI) für gerichtete Inhaltswechsel.
  Enter-only: der `innerHTML`-Austausch IST der Exit, eine Ausblendung davor wäre nur
  künstliche Latenz. `dir` ist das Vorzeichen der Richtung; `reducedMotion()` behält die
  Überblendung, verliert aber die Richtung (kein `transform`). Zwei Aufrufer: `renderPlan()`
  bei `pendingWeekDir` (`.week`) und `render()` bei echtem Tab-Wechsel (`view`, Richtung aus
  der Index-Differenz von `TAB_ORDER`).
* **`syncWeekSwitchPill(container, dir)`** — eigene WAAPI-Pille für `.week-switch` (`.ws-ind`).
  `.week-switch` wird bei **jedem** `render()` über `view.innerHTML` neu gebaut, eine
  CSS-`transition` griffe deshalb nie (die neu gebaute Pille stünde sofort am Ziel) — siehe
  `docs/TROUBLESHOOTING.md`. Position und Breite kommen aus `getBoundingClientRect()` der
  aktiven Schaltfläche, **nicht** aus einer 50 %-Rechnung: „Aktuelle Woche" und „Nächste Woche"
  sind unterschiedlich breit. Bei gesetztem `dir` läuft die Pille zusätzlich per `animate()` von
  der Gegenposition heran, mit denselben `MOTION.base`/`MOTION.ease`-Werten wie die
  `.week`-Slide. Geteilt mit dem Jahres-Umschalter im Rückblick (`.week-switch`/`.ws-btn`),
  der aber **kein** `.ws-ind` im Markup hat und deshalb bei der harten Umschaltung bleibt
  (`.week-switch:has(.ws-ind)` grenzt die Pillen-Optik im CSS auf den Wochen-Fall ein).
* **`.tab-ind`** — CSS-`transition` für die untere Tab-Leiste. Günstiger Sonderfall: `.tabs`
  liegt außerhalb von `view.innerHTML` im statischen Markup und überlebt jeden Neuaufbau, eine
  echte `transition: transform` funktioniert deshalb. Nur im 680-px-Breakpoint sichtbar, wo
  `.tabs` ein Grid mit **vier** gleich breiten Spalten ist (seit dem Reiter „Fortschritt",
  13.08.2026). `grid-template-columns: repeat(4, 1fr)` und `width: calc((100% - 12px) / 4)`
  gehören zusammen — wer eine Spalte ergänzt und die Pillenbreite vergisst, bekommt eine
  Pille, die neben ihrem Reiter steht. `translateX(i * 100%)` bleibt unverändert richtig: die
  100 % beziehen sich auf die Breite der **Pille**, nicht auf die der Leiste. Am
  Rechner sind die Tab-Knöpfe unterschiedlich breit (Meal-Zähler ändert die Breite) — dort
  bleibt `[aria-selected="true"]` die einzige Fläche. Position wird in `render()` gesetzt,
  **nach** der Scroll-Wiederherstellung, sonst animiert die View während ihre Position noch
  springt.

Bewusst kein echtes Wischen bei Woche und Tabs: das bräuchte alle Ansichten gleichzeitig im DOM
(ein horizontaler Scroller im horizontalen Scroller), auf Touch gewinnt immer der innere
Scroller, und `overscroll-behavior-x: contain` unterbindet die Weitergabe zusätzlich absichtlich.

## Zurück-Taste und Overlay-Stapel (D5, 23.08.2026)

Android hat eine Systemtaste „Zurück", iOS die Wischgeste am linken Rand. Ohne eigenen
History-Eintrag **beenden beide die App**, auch wenn gerade ein Modal offen steht. Das ist der
erste Griff jedes Android-Testers.

Der Mechanismus steht als ein Block direkt über dem Modal-Abschnitt in `index.html` und besteht
aus drei Teilen:

| | |
|---|---|
| `overlayStack` | die Schließfunktionen der offenen Overlays, unterstes zuerst |
| `overlayOpened(fn)` | ein Overlay ist aufgegangen: `fn` auf den Stapel, `pushState({pmOverlay: tiefe})` |
| `overlayClosed(fn)` | auf normalem Weg geschlossen: vom Stapel nehmen und den Eintrag zurücknehmen |

Angebunden sind genau zwei Stellen, weil es genau zwei Overlay-Ebenen gibt:

* **`openModal()` / `closeModal()`** — alle 22 Modals laufen hier durch, auch Bottom-Sheets und
  Bestätigungen.
* **`scanBarcodeLive()`** — der Live-Sucher hat eine eigene Ebene (`z-index` 80). Er wird von
  drei Stellen aus geöffnet, und **sie verhalten sich unterschiedlich**:

  | Aufrufer | Was vorher offen ist | Ebene |
  |---|---|---|
  | `openMealSheet()` (Zutaten-Barcode) | das Meal-Formular, das offen **bleibt** | zweite |
  | `openGroupModal()` → `scanInvite()` | das Gruppen-Modal, das offen **bleibt** | zweite |
  | Slot-Auswahl → `quickAddByBarcode()` | das Modal wird vorher **geschlossen** | erste |

  Der dritte Fall ist der heikle: `closeModal(); quickAddByBarcode(day, meal);` schließt und
  öffnet im selben Tick. Genau dafür erbt `overlayOpened()` einen noch nicht zurückgenommenen
  Eintrag, statt einen zweiten anzulegen.

### Drei Entscheidungen, die nicht offensichtlich sind

**Die Marke im Eintrag, nicht ein Zähler eigener Ereignisse.** `pushState` legt
`{pmOverlay: <Stapeltiefe>}` ab; der `popstate`-Handler schließt alles, was über der Marke des
angesteuerten Eintrags liegt. Der naheliegende Weg — mitzählen, wie viele `popstate` man selbst
ausgelöst hat — scheitert daran, dass ein Sprung über mehrere Einträge je nach Browser ein
Ereignis auslöst oder mehrere.

**Rücknahmen werden über einen `setTimeout(…, 0)` gebündelt.** Zwei `history.back()` im selben
Tick führt der Browser nicht beide aus (nachgemessen, siehe `docs/TROUBLESHOOTING.md` Punkt 107)
— und genau das passiert, wenn `closeModal()` erst den laufenden Sucher beendet und dann sich
selbst. Gebündelt wird daraus ein `history.go(-n)`.

**Wer im selben Tick schließt und wieder öffnet, erbt den Eintrag.** „Teilen" in der Meal-Ansicht
ruft `closeModal()` und direkt danach `shareRecipeNow()`. `overlayOpened()` prüft deshalb auf
offene Rücknahmen und verwendet den noch vorhandenen Eintrag per `replaceState` weiter, statt
einen zweiten anzulegen.

### Was bewusst offen bleibt

* **Ein abgebrochenes Schließen behält seinen Eintrag.** Das Meal-Formular ohne Namen verweigert
  über `modalCloseHook` das Schließen. Kam der Versuch über ✕ oder Escape, kommt `closeModal()`
  an `overlayClosed()` gar nicht erst an und der Eintrag bleibt einfach stehen. Kam er über die
  Zurück-Taste, ist der Eintrag zu diesem Zeitpunkt schon weg — deshalb **meldet `closeModal()`
  eine Verweigerung mit `false`**, und der `popstate`-Handler legt den Eintrag neu an. Am DOM
  ablesen ließe sich das nicht: Während der Exit-Animation steht das Overlay genauso noch da.
* **Ein Modal, das seinen Inhalt tauscht, bleibt ein Eintrag.** `openMealSheet()` wechselt per
  `openModal()` in den Bearbeiten-Zweig, ohne vorher zu schließen. `openModal()` misst deshalb
  **vor** dem Leeren, ob schon etwas offen war.
* **Reiterwechsel und der Onboarding-Wizard hängen nicht am Stapel.** Zurück verlässt dort die
  App. Das ist eine Entscheidung, keine Lücke: D5 deckt Overlays ab. Ein Wizard-Schritt zurück
  hätte einen eigenen Zustandsbegriff gebraucht und wäre mit dem separaten `Zurück`-Knopf in
  Konkurrenz getreten (CLAUDE.md, Ziffer 10).
* **Nach einem Neuladen mit offenem Overlay** steht ein Eintrag ohne zugehöriges Overlay in der
  History. Der erste Druck auf Zurück tut dann nichts Sichtbares. Ein Overlay über einen Reload
  hinweg wiederherzustellen wäre der falsche Preis dafür.

Belegt durch `tools/pruefstand-zurueck-taste.py` (48 Prüfungen, zwei Gegenproben) und einen
Durchlauf gegen die echte `index.html`.

## Meal-Ansicht: eine Oberfläche statt zweier (`openMealSheet`)

Ein Meal hatte früher drei getrennte Oberflächen: die Karte in der Liste, ein Ansehen-Modal
(`openRecipeDetail`) und ein Bearbeiten-Modal (`openRecipeForm`). `openMealSheet(id, prefill,
originEl)` ersetzt beide Modals durch eine einzige Ansicht, die am Rechner aus der Karte (bzw.
einem Wochenplan-Slot) per FLIP-Animation wächst, am Handy als Bottom-Sheet hochfährt, direkt
bearbeitbar ist und automatisch speichert. Details und der ursprüngliche Plan stehen in
dem Planungsdokument zum Umbau (Schritte 1–5). Das Dokument selbst gibt es nicht mehr —
umgesetzte Pläne werden gelöscht (`CLAUDE.md` §20); Code-Kommentare verweisen weiterhin
darauf, weil sie die damalige Begründung festhalten.

**Zwei Zweige, ein Einstiegs-Modus.** `openMealSheet(id, prefill, originEl, startInEdit)`:
`canEdit()` entscheidet weiter allein über die **Berechtigung** (Rolle `view` bekommt immer den
Nur-Lese-Zweig, ohne Eingabefelder, Autosave, Foto- oder Löschfunktion, Teilen bleibt erlaubt).
Ein bestehendes Meal öffnet seit der Abnahme Phase 2 (08.08.2026) **immer zuerst lesend** —
sowohl der Wochenplan-Slot (`.filled`) als auch die Karte im Meals-Reiter (`.rcard-open`).
Nachschlagen ("was esse ich Dienstag?", "was war da nochmal drin?") soll nirgends versehentlich
in eine Bearbeitung münden, in einer Gruppe sonst sofort aufs andere Gerät. `startInEdit` (bewusst
positiv formuliert statt der vorherigen doppelten Verneinung `forceReadOnly`) setzt nur der
„Bearbeiten"-Knopf im Kopf: ein Klick ruft `openMealSheet(id, null, null, true)` erneut auf und
tauscht den Knoten **ohne Eintrittsbewegung** aus (weder FLIP noch Hochfahren) — die Ansicht steht
schon an ihrem Platz. Zwei Ausnahmen
öffnen weiterhin direkt bearbeitbar, weil `isNew` in der Funktion selbst schon Vorrang vor
`startInEdit` hat: ein neues Meal (`new-recipe`, es gibt nichts anzusehen) und der Barcode-Weg
(`quickAddByBarcode` übergibt ein `prefill`, ist also ebenfalls `isNew`).

Beide Zweige teilen sich `mealStatsHtml(r)` (das `.nutfacts`-Kachelraster) für die große
Nur-Lese-Ansicht. Die Karte und der Ruhezustand der Makro-Zeile im Bearbeiten-Zweig nutzen einen
zweiten, bewusst *nicht* identischen Helfer, `cardStatsHtml(r)` — dieselben Zahlen aus
`recipeNut(r)`/`hasNut(r)`, aber als schlanke einzeilige Kurzform (kcal + farbige `KH/P/F`-Kürzel)
ohne Kacheln, Rahmen oder Textlabels. „Gemeinsames Bauteil" heißt hier gleiche
Zahlen/Farben/Reihenfolge, nicht identisches Markup — eine Karten-Liste mit vier Kacheln pro Meal
wurde als zu unruhig verworfen. Auf der Karte steht die Statistik-Zeile (`.cstats`) mit
`justify-content: space-between`: kcal links, die Makrogruppe rechtsbündig als ein
zusammenhängendes, nicht umbrechendes Element (`white-space: nowrap` auf `.cs-macros`) — bei
sehr schmalen Karten rutscht die ganze Gruppe als Block nach unten, statt KH/P/F einzeln
umzubrechen.

**`macroLineHtml(n)` — ein Helfer für die Makro-Kompaktzeile.** Kalorien und Makros folgen app-weit
derselben Regel (`CLAUDE.md`, Abschnitt „Makros und Nährwerte"): Kürzel `KH`/`P`/`F`, Reihenfolge
`kcal → KH → P → F`, kein `g` in der Kompaktform, Farbe ausschließlich über `--prot`/`--carb`/
`--fat` per `t-*`-Klasse. Statt das an jeder Stelle einzeln nachzubauen, liefert `macroLineHtml(n,
fmt)` (neben `nfmt()`) ausschließlich den KH/P/F-Teil als fertige `<span>`-Gruppe; kcal rendert
jeder Aufrufer weiter selbst, weil jede Stelle ihr eigenes Kcal-Markup hat (fette Zahl, `<small>`,
eigenes `<span class="u">` …). Fehlende Felder (`null`/`undefined`) fallen weg, statt als `0` zu
erscheinen — wichtig für `.ing-brief`, wo einzelne Zutaten-Nährwertfelder noch leer sein können.
Der optionale zweite Parameter `fmt` erlaubt eine abweichende Rundung (`.ing-brief` zeigt eine
Nachkommastelle statt ganzzahlig zu runden). Aufrufer: `cardStatsHtml()`, `paintIngView()`/
`roIngRowHtml()` (`.ing-view-macros`), `paintNut()` in `addIngRow()` (`.ing-brief`, dort als eigene
Gruppe `.ing-brief-macros`, damit die drei Werte beim Umbruch zusammenbleiben) und `dayNutHtml()`
(`.day-nut .macros`, Wochenplan-Tagesbilanz).

**Drei erlaubte Formen, eine Regel.** 1) **Kompaktzeile** über `macroLineHtml()` — Meal-Karte,
Zutaten-Anzeigezeile, Tagesbilanz. 2) **Kachelform** (`.nutfacts`, `mealStatsHtml()`) — Nur-Lese-
Zweig UND Bearbeiten-Zweig der Meal-Ansicht (dort als `.nutfacts.nutfacts-edit` mit Eingabefeldern
statt Text, siehe unten), behält Einheit und Textlabel in beiden Modi gleich. 3) **Balkenform**
(`.wg-macros`, `goalBarHtml()`/`goalMacrosHtml()`) — ausschließlich für
Fortschritt gegen ein Ziel, bleibt bei ausgeschriebenen Namen (`Kohlenhydrate`/`Proteine`/`Fett`):
frühere Kürzel scheiterten hier an schmalen Desktop-Tageskarten (~232 px), Wert und Kürzel standen
in zwei Zeilen übereinander. Die Reihenfolge zieht trotzdem mit (`goalMacrosHtml()` rendert die
Balken in KH→P→F). Eine vierte Form wird nicht erfunden.

**Makro-Zeile: dauerhaft vier Kacheln.** Ein kurzlebiger Ruhezustand (antippbare Kurzzeile
`#ms-nut-view`, `paintNutView()`, Umschaltung über `.ms-nut.editing`) wurde in der Abnahme Phase 2
(08.08.2026) wieder zurückgebaut — Ansichtsmodus und Bearbeiten-Modus sollen an dieser Stelle
gleich aussehen, der einzige Unterschied ist Text vs. Eingabefeld. Der Bearbeiten-Zweig zeigt
`#ms-nut` seitdem dauerhaft als `.nutfacts.nutfacts-edit`-Kachelraster, dieselbe Optik wie
`mealStatsHtml()` im Nur-Lese-Zweig (Farbpunkte/Reihenfolge kommen über dieselben
`.nutfacts .nf.t-kcal`/`.t-carb`/`.t-prot`/`.t-fat`-Regeln), nur dass `.v` statt Text ein
`<input>` enthält. Die vier Felder `#f-kcal`/`#f-carbs`/`#f-protein`/`#f-fat` sind unverändert:
`macroOverridden`, `updateMacroSum()` und der Autosave über die Event-Delegation blieben
unangetastet, nur der abschließende `paintNutView()`-Aufruf entfiel. Überschrift „Makros gesamt“
(`.nut-total > h4`) ohne Rahmen oder Erklärtext bleibt bestehen.

**Autosave statt Speichern-Knopf.** `input` mutiert nur lokal (`mutateLocal()`), `change`/
`focusout` committen (`commitNow()` → `save()`), zusätzlich ein 1500-ms-Leerlauf-Timer
(`scheduleCommit()`) als Netz. Ein neues Meal existiert zunächst nur als Entwurf im Speicher;
erst sobald ein Name eingetragen ist, zieht der Entwurf in `state.recipes` ein
(`draftPushed`-Flag, genau einmal).

**`openSheetId` — Sperre gegen den Remote-Merge.** `onRecipesRemote()` (die Firestore-
Subcollection-Callback) **ersetzt** ein geändertes Rezept-Objekt, statt es zu mutieren. Hielte
`openMealSheet()` eine Referenz auf das alte Objekt, schriebe jeder weitere Tastendruck in ein
abgehängtes Waisenobjekt. Deshalb zwei Regeln:

1. **Nie eine Referenz halten.** Einziger Zugriffsweg ist `const rec = () => (recId ?
   getRecipe(recId) : draft);` — jeder Zugriff holt frisch aus `state.recipes`.
2. **Modulweites `openSheetId`** wird beim Öffnen auf die ID des gerade bearbeiteten Meals
   gesetzt. `onRecipesRemote()` überspringt im „modified"-Zweig jeden Change mit `c.id ===
   openSheetId`, **ohne** die Baseline (`lastPushedRecipes`) mitzupflegen — der lokale Stand
   gilt beim nächsten `syncRecipes()` dadurch weiter als geändert und wird gepusht: lokal
   gewinnt, das andere Gerät zieht nach, sobald die Ansicht schließt.

**`openSheetRemovedCb` — Gegenprobe für den „removed"-Zweig.** Die `openSheetId`-Sperre deckt
nur ab, dass ein *geändertes* Objekt das offene Meal nicht ersetzt. Löscht ein **anderes** Gerät
genau das offene Meal, verschwindet es im „removed"-Zweig von `onRecipesRemote()` trotzdem aus
`state.recipes` — `mutateLocal()` guardet zwar gegen den Absturz (`rec()` liefert dann
`undefined`, `mutateLocal()` kehrt früh zurück), aber ohne weitere Maßnahme bliebe die Ansicht
lautlos offen und jede weitere Eingabe ginge ins Leere. `openMealSheet()` trägt deshalb eine
Aufräumfunktion in die modulweite Variable `openSheetRemovedCb` ein (gleiches Muster wie
`photoDoneCb`), sobald ein echtes Dokument existiert (beim Öffnen eines bestehenden Meals, oder
sobald ein neuer Entwurf zum ersten Mal gespeichert wird). Trifft im „removed"-Zweig
`c.id === openSheetId`, ruft `onRecipesRemote()` diese Funktion auf: sie schließt die Ansicht
(ohne FLIP-Exit — das Ursprungselement ist gerade aus dem Raster verschwunden) und zeigt einen
freundlichen Toast. Keine stille Wiederauferstehung des Meals gegen die Löschung des anderen
Geräts.

**`closeModal()` / `modalCloseHook`.** `closeModal()` prüft zuerst `modalCloseHook`: ist er
gesetzt, ruft er ihn (und leert ihn) statt des Standard-Schließens. `openMealSheet()` nutzt das,
um beim Schließen ohne Namen abzubrechen (Fokus + Toast statt Verwerfen) und um die FLIP-Exit-
Animation zu spielen, bevor `modalRoot` geleert wird. Escape, Backdrop-Klick, das ✕ im Kopf und
„Fertig" im Fuß laufen alle über `closeModal()` — der Hook greift dadurch überall gleich, ohne
dass jeder Aufrufer ihn einzeln kennen müsste. `openModal(node, opts)` erlaubt zusätzlich ein
eigenes Fokusziel (`opts.focus`) statt der Standardsuche und eine zusätzliche Klasse am Overlay
(`opts.overlayClass`, heute nur `sheet-overlay`).

**FLIP als Motion-Baustein neben `slideIn` — am Rechner.** `flipIn(el, from, to)`/`flipOut(el,
from, to)` (neben `slideIn`, siehe oben) lassen die Ansicht sichtbar aus der angetippten Karte
bzw. dem Wochenplan-Slot wachsen/schrumpfen. Nur `transform` wird animiert (nie `width`/`height`),
zwei WAAPI-Animationen im selben Tick: der Container fährt von `translate(dx,dy) scale(s)` auf
`none`, der Inhalt blendet erst ab ~38 % ein. Öffnen misst das Ursprungsrect **beim Klick** (nicht
erst beim Animieren); Schließen sucht das Zielelement **neu** (`findMealOrigin()`), nie den beim
Öffnen gemerkten Knoten — Name, Kategorie oder Sichtfeld können sich geändert haben. Fehlt das
Ziel, fällt es auf reines Ausblenden zurück. `reducedMotion()` schaltet auf `.modal.flip-anim`
(Animation/Transition per CSS deaktiviert) und nur Überblendung, kein Transform — siehe
`docs/TROUBLESHOOTING.md`.

**Bottom-Sheet — am Handy (Nachtrag Abnahme, 08.08.2026).** Unter `max-width: 560px` gilt FLIP
nicht: dort ist die Karte fast so breit wie die Ansicht, und weil `flipDelta()` die Skalierung
allein aus der Breite ableitet, bleibt `s ≈ 1` und die Bewegung praktisch unsichtbar (Ziffer 53
in `docs/TROUBLESHOOTING.md`). Stattdessen steht die Ansicht sofort an ihrem Platz und gleitet nur ein kurzes Stück herein:
`translateY(48px) → none` zusammen mit `opacity 0 → 1` (`MOTION.slow`, `MOTION.ease`), beim
Schließen spiegelbildlich (`MOTION.base`, Exit kürzer als Entry). Der gemeinsame Helfer dafür ist
`sheetMove(node, keyframes, dur, fill)`.

**Warum der Weg kurz ist (Rückmeldung 08.08.2026).** Zuerst fuhr das Sheet über die volle
Bildschirmhöhe hoch (681 px). Am Gerät fiel dabei reproduzierbar der eine oder andere Frame aus —
sichtbar als kurz falsch stehende Fußzeile, umso häufiger, je länger die Zutatenliste war. Das
Layout war dabei nachweislich stabil (Höhe und Fußposition über die ganze Animation konstant); es
war die Rasterarbeit pro Bild. `sheetMove()` setzt deshalb zusätzlich `will-change` (wie
`flipIn()`) und stellt `.modal-body` für die Dauer der Bewegung auf `overflow: hidden`, damit kein
zweiter Scroll-Layer mitgerastert wird. **Beides muss in jedem Ausgang wieder weg** — bleibt
`overflow` hängen, lässt sich eine lange Zutatenliste nie wieder scrollen; der `finished`-Handler
räumt deshalb in beiden Zweigen auf, auch bei abgebrochener Animation. `fill: "forwards"` trägt
nur der Austritt, sonst blitzt das Sheet zwischen Animationsende und `closeModal()` ein Bild lang
wieder auf.

Drei Größen steuern die Verzweigung in `openMealSheet()`:

* `asSheet` (`sheetLayout()`, dieselbe `max-width: 560px`-Grenze wie das CSS) — das **Layout**.
  Gilt bewusst auch unter `reducedMotion()`: eine feste Sheet-Größe ist keine Bewegung.
* `withMotion` (`!reducedMotion()`) — nur die Animationen.
* `useAnimExit` — spielt dieser Vorgang überhaupt eine eigene WAAPI-Bewegung? Steuert sowohl den
  Exit als auch die Klasse `.flip-anim` (die die CSS-eigene `pop`-Animation abschaltet), bewusst
  aus **einer** Variablen: zwei Flags für dieselbe Frage laufen früher oder später auseinander.
* `sheetEnter` — das Hochfahren spielt nur, wenn **nicht schon** eine `.mealsheet` offen ist. Der
  „Bearbeiten"-Knopf tauscht den Knoten in-place aus und unterdrückte die Eintrittsbewegung am
  Rechner allein über `originEl = null`; am Handy hängt sie nicht mehr an `originEl`, ohne diese
  Prüfung führe das Sheet beim Moduswechsel ein zweites Mal hoch.

Das Layout selbst steckt im CSS-Block `.overlay.sheet-overlay` (bei den `.mealsheet`-Regeln): das
Sheet ist `92dvh` hoch (mit `vh`-Rückfall), dockt unten an, ist oben abgerundet und ein Raster aus
drei Reihen — Foto, scrollender Body (`1fr`, `min-height: 0`), feste Fußzeile mit
`env(safe-area-inset-bottom)`. `.mealsheet .modal-head` ist `position: absolute` und damit kein
Grid-Item. Dadurch ist die Ansicht **für jedes Meal gleich hoch**, Foto und „Schließen" sind
immer ohne Scrollen erreichbar. Die Klasse setzt `openModal(node, { overlayClass })` — eine
Ansicht kann damit ihr Außenlayout wählen, ohne dass es die übrigen Modals trifft; bewusst eine
echte Klasse statt `:has(.mealsheet)`.

**Gerätedrehung bei offener Ansicht.** Wer das Handy dreht, während die Ansicht offen ist, kann
die 560-px-Grenze überqueren: das CSS folgt sofort, eine beim Öffnen gemerkte Variable nicht.
`closeWithMotion()` fragt deshalb **beim Schließen erneut**, ob die Ansicht gerade wirklich als
Sheet dasteht — Klasse `sheet-overlay` (so geöffnet) **und** `sheetLayout()` (Breite greift noch).
Fällt einer der beiden Teile weg, übernimmt der FLIP-Zweig, der sein Ziel ohnehin frisch sucht;
sonst führe ein zentriertes Modal nach unten weg, statt zu seiner Karte zurückzuschrumpfen.

**Zutatenliste: Ruhezustand und Bearbeiten-Zustand.** `addIngRow()` erzeugt pro Zutat zwei
Blöcke im selben DOM-Knoten: `.ing-view` (ruhig, eine Zeile mit Menge/Name/kcal/Makros) und das
unveränderte Formular (`.ing-top`/`.ing-nut`). `.ing-row.editing` entscheidet per CSS, welcher
Block sichtbar ist — das Formular-DOM bleibt für jede Zeile immer im Dokument, `rowData()`/
`collectIngs()` lesen unverändert über `.value`. `.ing-view-name` ist ein Stretched-Link-Knopf
(`all: unset`, `::after { inset: 0 }`), der die Zeile öffnet; `.ing-view-del` sitzt mit höherem
`z-index` darüber. Ein „Fertig"-Knopf am Ende des aufgeklappten Bereichs ruft `closeIngRow(row)`
als sichtbaren vierten Schließweg neben Enter, Fokusverlust und dem Öffnen einer anderen Zeile.

## Auto-Wochenplaner (D2, 16.08.2026)

**Kein neues Datenfeld, kein neuer Speicherort.** Der Planer schreibt ausschließlich in
`state.plan[tag][slot]` — dieselben Einträge, die auch der Picker erzeugt, über denselben
Helfer `makeEntry()`. Damit gilt für ihn automatisch alles, was für den Wochenplan schon gilt:
`flattenWeek()`/`unflattenWeek()`, der Gruppen-Sync, die Einkaufsliste, das PDF und `pruneWeeks()`.
Ein Plan, der vom Planer stammt, ist von einem handgemachten **nicht unterscheidbar** — und das
ist Absicht: Ein Herkunftsvermerk am Eintrag hätte durch Sync, Undo und Zuweisung mitgeführt
werden müssen, ohne dass irgendetwas ihn auswertet.

### Ablauf von `autoPlanWeek()`

| Schritt | Was passiert |
|---|---|
| Riegel | `canEdit()`, `goalTargets(1)`, Pro (`isPro() \|\| syncGid`), genug Kandidaten |
| 1 | `planKandidaten()` — eigene (`libraryRecipes()`) **plus Katalog** (`cookbookVisible()` ∩ `!isAdopted()`), beide ∩ `fitsDiet()` ∩ `kcal > 0` |
| 2 | `planWochengerichte(kand, slot, budget, letzte)` je Slot-Art: mischen, nach `planRang()` sortieren, aus den besten `PLAN_POOL` (8) drei **gewichtet ziehen**. `ab` zieht aus der Menge **ohne** die `mi`-Gerichte |
| 3 | je Tag `goalTargetsForDay(tag)` — Trainingstage sind darin schon enthalten |
| 4 | fr/mi/ab: `anzahl = round(budget / kcal)`, gedeckelt auf **1** (allein) bzw. **2** (in der Gruppe) |
| 5 | sn: der **Rest** des Tages, gefüllt mit **verschiedenen** Snacks statt Vielfachen |
| 6 | `planId()` liefert seit dem 17.08.2026 einfach `r.id` (kein Kopieren mehr, siehe „Der Katalog wird nachschlagbar" oben), dann `makeEntry(id, syncGid ? [syncUid] : null)` je Eintrag einzeln. Im Übernahmefall wird die **erste** Portion stattdessen am vorhandenen Eintrag eingetragen (siehe unten) |
| 7 | Wochenbilanz gegen `goalTargetsForDays()` — **kcal und Protein**; > `PLAN_TOLERANZ` wird im Toast benannt |

**Schritt 7 prüft beide Säulen, weil Schritt 4 nur eine kennt.** Die Mengen entstehen aus dem
kcal-Budget; Protein wirkt ausschließlich über `planRang()`, also über die *Auswahl*. Ein
Bestand aus fettigen Kohlenhydraten trifft die Kalorien damit punktgenau und verfehlt das
Proteinziel deutlich — in einer Fitness-App der Fall, der benannt gehört. Beim Protein zählt nur
ein **Defizit** (Untergrenze, wie `goalState(…, "min")`), und es wird nur genannt, wenn die
Kalorien stimmen: Ein Toast mit zwei Zusätzen liest niemand.

**Warum `planRang()` mit Stufenabständen arbeitet** (100 / 10 / max. 9): Die Bewertung soll
nicht „ausgemittelt" werden. Eine exakt passende Kategorie muss jedes Meal-Prep-Gericht der
falschen Kategorie schlagen, und Meal-Prep jeden Proteinvorsprung. Mit Punkten in derselben
Größenordnung wäre die Reihenfolge Zufall.

**Warum erst mischen, dann sortieren:** `Array.prototype.sort` ist stabil. Der Zufall entscheidet
damit nur bei Punktgleichstand — zwei Aufrufe liefern nicht denselben Plan, aber nie ein
schlechteres Gericht vor einem besseren.

**Die Gerichtwahl je Tag ist eine Rotation** (`liste[tagIndex % liste.length]`), kein Zufall pro
Slot. Nur so wiederholt sich ein Gericht planbar über die Woche (Meal-Prep), und das Ergebnis
ist beim Ansehen nachvollziehbar.

**`slotOpenForMe()` stellt dieselbe Frage wie `dayNutOf()`:** Betrifft mich dieser Eintrag —
geteilt oder mir zugewiesen? Ein Eintrag, der nur anderen Mitgliedern gehört, lässt den Slot für
mich offen. Genau daran hängt Regel 5: `planUebernahme()` sieht dann nach, ob deren Gericht auch
zu meinem Profil passt, und nimmt dasselbe.

**`slotGemeinsam` — der Planer fragt jetzt dieselbe Frage wie der Picker** (16.08.2026). Vor dem
Einfügen wird `slotIsShared(tag, slot)` einmal ausgewertet; ist die Zeile leer oder rein
gemeinsam, bekommt der **erste** Eintrag `null` als `uids` („für alle"), jeder weitere
`meineUids()`. Vorher trug der Planer ausnahmslos die eigene UID ein — als einzige Stelle der
App, denn die fünf manuellen Einplan-Wege stellen die Frage seit jeher:

```js
state.plan[day][meal].push(slotIsShared(day, meal) ? id : makeEntry(id, [syncUid]));
```

`slotIsShared()` ist bei leerem Slot `true` (`every` auf leerem Array). **Der Wert muss VOR der
Portionsschleife festgehalten werden** — nach dem ersten Einfügen wäre die Antwort eine andere,
und die zweite Portion würde ebenfalls „für alle", also zwei Portionen für jeden statt zwei für
mich.

**`planUebernahme()` liefert `{ r, idx }`, nicht nur das Rezept** (16.08.2026). Der Index ist der
Grund für die Änderung: Der Planer legt im Übernahmefall **keinen zweiten Eintrag** mehr an,
sondern trägt sich am vorhandenen ein —

```js
state.plan[d][m][idx] = makeEntry(entryId(alt), entryUids(alt).concat(syncUid));
```

— und `makeEntry()` erledigt den Rest von selbst: Deckt die UID-Menge alle `groupMembers` ab,
kommt die schlichte String-Form zurück („für alle"). Aus zwei Karten wird eine, **ohne neue
Logik**. Nur die erste Portion tritt bei; braucht jemand zwei, kommt der zweite Eintrag regulär
dazu.

**Ersetzen, nicht mutieren** — das ist hier keine Stilfrage. `before` in `autoPlanWeek()` hält
nur eine **flache Kopie** des Slot-Arrays (`.slice()`). Ein `uids.push()` am vorhandenen Objekt
schlüge durch den Undo-Pfad durch und veränderte den fremden Eintrag dauerhaft. Siehe
`docs/TROUBLESHOOTING.md`.

Die Fälle „Eintrag ohne `uids`" und „`uids` enthält mich schon" können dabei nicht auftreten:
Beide machen den Slot über `slotOpenForMe()` für mich zu, der Planer läuft dort gar nicht erst.

**Der Verträglichkeits-Beitrag in `planRang()`** (max. 8, nur bei `syncGid && groupMembers.length
> 1`): vegan +5 bzw. vegetarisch +3, glutenfrei und laktosefrei je +1,5, zusammengefasst durch
`Math.min(8, …)`. Er steht **unter** dem Wiederholungs-Malus (40) — sonst stünde jede Woche
dasselbe vegane Gericht oben. Der Deckel steht bewusst im **Code**, obwohl die vier Tags von
selbst höchstens 8 ergeben: Eine fünfte Unverträglichkeit würde die Zusage sonst still brechen,
und keine Prüfung würde es merken (der Deckel ist mit vier Tags nicht erreichbar). Bewertet wird
allein das Gericht, **nie ein fremdes Profil**; Ziffer 8a der Datenschutzerklärung bleibt
unberührt. Ohne Gruppe ändert sich am Ergebnis nichts.

**`makeEntry()` wird je Eintrag neu gerufen**, nicht einmal und n-mal eingefügt. Sonst lägen bei
mehreren Portionen mehrere Verweise auf **dasselbe Objekt** im Plan, und eine spätere Änderung an
genau einem Eintrag (Zuweisung ändern) hätte alle mitgeändert.

### Zwei Kandidatenquellen — und warum der Katalog seit dem 17.08.2026 NICHT mehr kopiert wird

Seit dem 16.08.2026 zieht der Planer auch aus `COOKBOOK`. Katalog-Kandidaten tragen `__cb: true`
an einer **flachen Kopie** — nie am Katalogeintrag selbst, der ist gemeinsamer Bestand und würde
sonst die Rezeptbuch-Ansicht mitverschmutzen.

**Bis zum 17.08.2026 legte `planAdopt()` hier eine Bestandskopie an** (siehe „Der Katalog wird
nachschlagbar" oben) — der Grund war die damalige Annahme, `normalizePlan()` filtere jeden
Katalog-Eintrag sonst lautlos aus dem Plan. Genau das filtert `normalizePlan()` seither nicht
mehr aus: `planId(r)` liefert einfach `r.id`, auch für `r.__cb`-Kandidaten. Der Bestand wächst
dadurch nicht mehr mit jedem Planerlauf.

`isAdopted()` bleibt trotzdem als Filter in `planKandidaten()` bestehen: Ein bereits
übernommenes Rezept liegt im eigenen Bestand und käme sonst **zweimal** in die Kandidatenliste —
einmal als Kopie, einmal als Katalogeintrag.

**Undo nimmt nur noch die Slots und das Gedächtnis zurück.** Kopien gibt es seit dem Umbau
nicht mehr, die dabei extra entfernt werden müssten.

**Der Toast nennt die Katalog-Nutzung trotzdem** (`ausKatalog`-Set in `autoPlanWeek()`): Auch
ohne dass etwas in den Bestand wandert, bleibt „X Meals aus dem Rezeptbuch" eine relevante
Information darüber, woher die Abwechslung dieser Woche kommt.

### Abwechslung: drei Mechanismen, die zusammenwirken (16.08.2026)

**1. Getrennte Mengen für Mittag und Abend.** `wahl.ab` zieht aus `kand` ohne die `mi`-Gerichte;
reicht das nicht für `PLAN_VARIANTEN`, wird aus der vollen Menge aufgefüllt. Der Rückfall prüft
die Zahl der **gezogenen Abendgerichte**, nicht die Größe der Restmenge — die enthält ja noch
Frühstücke und Snacks und ist deshalb nie leer. Genau daran ist der erste Anlauf gescheitert:
Bei zwei Hauptgerichten im Bestand blieb der Abend die ganze Woche leer.

**2. Rotationsversatz und Kollisionsregel.** `ab` greift mit `di + 1` zu, und am Ende steht eine
harte Prüfung: Ist das Abendgericht dasselbe wie mittags, rückt die Liste weiter. Verglichen wird
über **Objektidentität** (trifft auch Katalog-Kandidaten, weil `kand` einmalig gebaut wird und
`mi`/`ab` dieselben Objektreferenzen ziehen) und — nur bei eigenen Meals — über die id.
`planId()` darf hier nicht gerufen werden: Seit dem 17.08.2026 kopiert es zwar nichts mehr,
merkt sich aber die Katalog-Nutzung fürs `ausKatalog`-Set des Toasts — ein Aufruf hier würde
einen gleich wieder verworfenen Kandidaten fälschlich mitzählen.

**3. Gewichtete Ziehung.** Aus den besten `PLAN_POOL` (8) werden `PLAN_VARIANTEN` (3) ohne
Zurücklegen gezogen, Gewicht `PLAN_POOL - index`. Jeder Lauf ergibt einen anderen Plan, ohne dass
je ein schwacher Kandidat ins Feld kommt.

### Gedächtnis: `state.planned`

`{ "<rezeptId>": "YYYY-Www" }`, geschrieben **nur** von `autoPlanWeek()` nach einem erfolgreichen
Lauf. Persönliches Feld nach dem Vorbild von `state.favs` — dieselbe Sync-Kette (load ×2,
`sanitizePlanned`, save, `dataJSON`, Push-Objekt, `onRemote` ×2) und dasselbe Miträumen beim
Löschen eines Meals. **`dataJSON()` ist die Stelle, an der ein neues Feld sonst still
verschwindet** (§73): Fehlt es dort, unterscheidet sich die Zeichenkette nicht und es wird nie
gepusht.

Bewertet wird in `planRang()`: vorige Woche −40, die davor −20 — über Meal-Prep (10) und Protein
(9), unter der Kategorie (100). Dazu `planRecentIds()`, das die **jeweils andere** der beiden
vorgehaltenen Wochen liest (kostenlos, erfasst auch von Hand geplante Gerichte).

**`weekKeyBack()` ist gepuffert, und das ist kein Feinschliff:** `planRang()` ruft es dreimal und
läuft selbst in der Vergleichsfunktion eines `sort()`. Ohne Puffer entstehen bei 150 Rezepten
tausende `Date`-Objekte je Slot — im Prüfstand war der Unterschied **über zwei Minuten gegen eine
Sekunde**. Der Puffer trägt den Tagesstempel mit, damit er über Mitternacht nicht falsch wird.

### Pro-Grenze

Der Planer ist die einzige Pro-Sperre, die **rein in der UI** liegt — und darf es sein: Er
schreibt nur Slots, die derselbe Nutzer auch von Hand schreiben dürfte. Es gibt nichts
serverseitig durchzusetzen, weil keine Datengrenze berührt wird (`CLAUDE.md` §18 betrifft den
Zugriff auf Daten, nicht den Komfort). In einer Gruppe (`syncGid`) entfällt die Sperre ganz —
dort zahlt der Inhaber.

## Einkaufsliste: der Abhak-Zustand hängt an der Woche (28.08.2026)

Die Liste selbst hat nie ein Wochenproblem gehabt: `buildShoppingList()` läuft über
`state.plan`, und das ist per `setViewWeek()` immer die gerade gezeigte Woche. Der **abgehakte
Zustand** dagegen lag bis zum 28.08.2026 als ein einziges flaches Set in
`localStorage["wochenkueche_shop_v1"]` — geteilt von beiden Wochenreitern.

Die Folge war ein Fehler, den man beim Einkaufen bemerkt und nicht davor: Wer in der aktuellen
Woche „500 g Hackfleisch" abhakte und auf **Nächste Woche** umschaltete, fand die Position dort
bereits erledigt — obwohl die nächste Woche eine ganz andere Menge braucht (`ab heute` gegen die
volle Woche). Und am Montag rückte derselbe Zustand stillschweigend nach: Die frische Woche
startete mit den Haken der vergangenen.

**Der Speicher ist deshalb nach ISO-Wochenschlüssel gegliedert** — denselben, unter dem auch
`state.plans` liegt:

```json
{ "2026-W35": ["hackfleisch|g", "nudeln|g"], "2026-W36": ["milch|ml"] }
```

| Funktion | Aufgabe |
|---|---|
| `loadShopDoneAll()` | liest das ganze Objekt; ein **flaches Array** aus der Fassung davor gilt als Bestand der *aktuellen* Woche |
| `loadShopDone()` | das Set für `activeWeekKey()` — genau die Woche, die der Reiter zeigt |
| `saveShopDone(set)` | schreibt diese eine Woche und wirft dabei alles außer `cur`/`next` weg |

Zwei Dinge fallen dadurch ohne eigene Logik ab:

* **Die Haken der nächsten Woche wandern beim Wochenwechsel von selbst mit.** Ihr Schlüssel
  ändert sich nicht — die Woche heißt am Montag nur nicht mehr „nächste", sondern „aktuell".
  Genau dieselbe Mechanik trägt schon `state.plans` (siehe „Wochen" oben), es gibt weiterhin
  keine Rotationslogik.
* **Der Eintrag wächst nicht ewig.** `saveShopDone()` behält nur die zwei bekannten Wochen —
  dieselbe Regel wie `pruneWeeks()` für die Pläne. Ohne das sammelte sich jede je abgehakte
  Zutat dauerhaft an, und niemand hätte es je gesehen.

Der Migrationspfad ist bewusst nicht „wegwerfen": Der Altbestand landet in der aktuellen Woche.
Alles andere wäre geraten — und hätte jedem Nutzer beim Update seinen halb abgehakten Einkauf
gelöscht.

`norm` (Zutatenname + Einheit, **ohne** Menge) bleibt unverändert der Schlüssel innerhalb einer
Woche. Dass die Menge nicht darin steckt, ist der Grund, warum ein Haken eine geänderte
Personenzahl überlebt.

### `planScopeLabel(todayIdx)` — welche Woche steht im Kopf?

Gegenstück zu `planDaysAhead()`: dieselbe Frage, nur in Worten. **Eine** Quelle für
Einkaufsliste, Vorkochliste *und* das PDF — alle drei ziehen ihre Tage aus `planDaysAhead()`
und müssen deshalb auch dieselbe Woche benennen.

`planScopeTitle()` ist dieselbe Angabe groß geschrieben, für den PDF-Kopf, wo der Zeitraum
als Titelzeile steht statt als Fortsetzung eines Satzes.

| `viewWeek` | `todayIdx` | Label |
|---|---|---|
| `"next"` | egal | `nächste Woche` |
| `"cur"` | `> 0` | `diese Woche ab heute` |
| `"cur"` | `0` (Montag) | `diese Woche` |

Ohne Komma: „diese Woche ab heute" ist **eine** Aussage — „ab heute" schränkt „diese Woche"
ein. Mit Komma lasen sich zwei Angaben hintereinander, als käme noch etwas.

Vorher stand für die nächste Woche fälschlich „diese Woche" da — der ternäre Ausdruck
`viewWeek !== "next" && todayIdx > 0 ? "ab heute" : "diese Woche"` fiel für `"next"` in den
zweiten Zweig. Das PDF (`shopPdfString()`) schrieb an derselben Stelle immer korrekt
„Nächste Woche", womit belegt war, dass es ein Versehen ist und keine Absicht.

Bei geöffnetem Modal ist der Wochenumschalter verdeckt — der Kopf ist dann der einzige Hinweis,
für welche Woche man gerade einkauft. Die Überschrift heißt seitdem nur noch „Einkaufsliste"
statt „Einkaufsliste der Woche": Mit einem Kicker, der die Woche genau benennt, stand sie sonst
zweimal da, einmal unbestimmt und einmal genau.

**Das PDF hing zunächst noch daneben.** `shopPdfString()` baute den Zeitraum bis zum
Nachzug am 28.08.2026 aus einer eigenen Zeile (`viewWeek === "next" ? "Nächste Woche" :
"Diese Woche"`). Die nannte zwar die richtige Woche, verschwieg aber das `ab heute`: Das PDF
trug „Diese Woche" über einer Liste, die nur die restlichen Tage enthält. Wer es ausdruckt,
sieht dem Blatt nicht an, dass Montag bis Mittwoch fehlen — **derselbe Fehler wie im
Modal-Kopf, nur andersherum.** Gefunden hat das der Agent `kvp` bei der nachträglichen
Prüfung, nachdem die Doku hier bereits „eine Quelle" behauptete.

### Der Dialogname trägt die Woche mit

`openShopping()` und `openBatchCooking()` setzen `aria-label="Einkaufsliste, diese Woche ab
heute"` statt nur `"Einkaufsliste"`. Grund: `openModal()` fokussiert den ersten Knopf, und
angesagt wird der **Dialogname** — der sichtbare Kicker wird erst beim Weiterlesen erreicht.
Solange die Überschrift „Einkaufsliste der Woche" hieß, trug wenigstens sie einen Hinweis;
seit der Kürzung wäre sonst gar keiner mehr im Namen. Die Kürzung hat den Kopf für Sehende
präziser gemacht und hätte ihn für Screenreader-Nutzer unbestimmter gelassen.

### Warum der Abhak-Zustand *nicht* in die Cloud geht

Er steht in keinem Feld von `dataJSON()`/`pushNow()` — und das ist eine Entscheidung, keine
Auslassung. In einer Gruppe hieße ein geteilter Haken „jemand hat es geholt": eine Aussage,
die niemand getroffen hat. Zwei Personen gehen getrennt einkaufen, und wer zuerst abhakt,
löschte dem anderen die Position von der Liste. Ein gemeinsamer Einkauf ist ein eigenes
Feature mit einer eigenen Frage („wer holt was?") — kein Nebeneffekt der Speicherung.

Wird er je synchronisiert, braucht `loadShopDoneAll()` **vorher** denselben Schlüssel-Regex
wie `sanitizeWeekStats()` (`/^\d{4}-W\d{2}$/`). Heute ist er entbehrlich: Der Wert ist rein
lokal, wer ihn manipuliert, hat den Browser ohnehin. Über Sync käme er von fremd.

### Bekannte Einschränkung: der Haken kennt die Menge nicht

`norm` ist Name + Einheit **ohne** Menge — deshalb überlebt ein Haken eine geänderte
Personenzahl. Er überlebt aber auch eine geänderte **Planung**: Wer „500 g Hackfleisch"
abhakt und danach ein weiteres Hackfleisch-Gericht einplant, sieht „750 g" mit gesetztem
Haken. Das ist die Kehrseite derselben Entscheidung, nicht ein übersehener Fehler.

Bewusst so belassen: Die Menge in den Schlüssel zu nehmen, hieße, dass jede Änderung der
Personenzahl sämtliche Haken zurücksetzt — der häufigere Fall, und der ärgerlichere. Wer den
Fall doch lösen will, braucht einen dritten Weg (etwa Haken behalten, aber die gewachsene
Differenz markieren), nicht den Schlüsseltausch.

→ Prüfstand: `tools/pruefstand-einkaufsliste.py` (fünf Läufe, siehe `docs/TESTING.md`)

## Architekturprinzip

Bei mehreren möglichen Lösungen gewinnt grundsätzlich die Lösung mit:

1. besserer Wartbarkeit
2. besserer Skalierbarkeit
3. klarerer Modularität
4. besserer UX
5. weniger technischer Schuld

Provisorische Lösungen nur dann, wenn eine saubere Lösung aktuell nicht sinnvoll machbar ist.
