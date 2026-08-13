# ARCHITECTURES.md

# Architektur von Paddy's Mealplan

Dieses Dokument beschreibt die technische Struktur, Datenflüsse, Persistenz und bewusst beibehaltenen Architekturentscheidungen.

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

Die Zeilennummern sind nur grobe Orientierung und dürfen nicht als stabile API betrachtet werden.

| Bereich                                  | Inhalt                           |
| ---------------------------------------- | -------------------------------- |
| `<head>` / CSS                           | Meta-Tags und gesamtes UI-System |
| `<header>` / `<main id="view">` / Footer | statisches Grundgerüst           |
| `type="module"`                          | Firebase und Cloud-Abstraktion   |
| normales `<script>`                      | eigentliche App                  |
| `PHOTO_CREDITS` / `PHOTOS`               | Foto-Metadaten                   |

Bei Änderungen immer mit `Grep` nach konkreten Markern suchen.

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
`noteError()` darin ist es nicht mehr — fehlte die Funktion, legte jede der 38 Stellen einen
`ReferenceError` nach und bewirkte das Gegenteil. Der Melder darf deshalb nie hinter etwas
rutschen, das vorher scheitern kann, und nichts nachladen.

**Eine Stelle bleibt bewusst leer:** `navigator.share(...).catch(() => {})`. Bricht der Nutzer
das Teilen-Blatt ab, kommt ein `AbortError` — Normalbetrieb, kein Fehler.

## Zwei-Script-Architektur

### Firebase-Modul

Das `type="module"`-Script läuft vor dem eigentlichen App-Script.

Es importiert Firebase v10 vom gstatic-CDN und stellt über `window` folgende Schnittstellen bereit:

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

`db` wird über `initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) })` initialisiert, nicht mehr über das flüchtige `getFirestore(app)`. Der Cache spiegelt Wochenplan, Meals und Gruppendaten in IndexedDB, damit die App nach einem Kaltstart ohne Netz nutzbar bleibt (Wochenplan im Supermarkt, Einkaufsliste im Keller). Der Multi-Tab-Manager ist Pflicht — ohne ihn schaltet ein zweiter geöffneter Tab die Persistenz für beide Tabs stillschweigend ab.

Die Initialisierung sitzt in einem eigenen `try/catch` mit Fallback auf `getFirestore(app)`: sie steckt mitten im großen `try`-Block, dessen `catch` `cloudauth:disabled` wirft und damit die **gesamte** Cloud-Anmeldung deaktiviert (siehe „Graceful Fallback" oben). Scheitert die Persistenz allein (Privatmodus ohne IndexedDB, exotische WebView), darf das nicht die ganze Cloud kosten — Persistenz ist ein Komfortgewinn, keine Voraussetzung.

**Wichtigste Konsequenz: `fromCache` ist kein Beweis.** Mit dem flüchtigen Cache warf `getDoc`/`getDocs` offline zuverlässig — erkennbar als Fehler. Mit Persistenz liefern beide still den letzten bekannten Stand aus IndexedDB, kenntlich nur über `snap.metadata.fromCache`. `CloudGroup.fetch()` und `fetchMembers()` geben dieses Flag deshalb mit zurück (`{ data, fromCache }` bzw. `{ members, fromCache }`), `watchMembers()` reicht es als zweiten Callback-Parameter durch. `enterGroupSync()` leitet aus einem `fromCache`-Ergebnis **nie** `"gone"` ab, sondern `"error"` — siehe „Drei Zustände statt true/false" unten, ausführlicher Fehlerfall in `docs/TROUBLESHOOTING.md`.

**Löschung:** `CloudSync.wipeCache()` ruft `terminate(db)` gefolgt von `clearIndexedDbPersistence(db)` — Reihenfolge zwingend, `clearIndexedDbPersistence()` verlangt eine beendete Instanz. `wipeLocalData()` ruft das als letzten Schritt auf, nach `localStorage` und der Bild-IndexedDB. Seitdem kann `wipeLocalData()` erstmals fehlschlagen; alle drei Aufrufer (`deleteAccountFlow()` beide Zweige, `deleteLocalDataFlow()`) fangen den Fehler mit einer ehrlichen Meldung ab, statt „gelöscht" zu behaupten und neu zu laden.

## Brücke zwischen Firebase und App

Die beiden Scripts teilen sich grundsätzlich keine direkte Implementierung.

Die einzige definierte Brücke ist:

`window.__onCloudAuth(user)`

Firebase ruft diese Funktion aus `onAuthStateChanged` auf.

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

Aktivierung (`finalizeGroupActivation()`) läuft auf zwei Wegen:

* **Live:** ein schlanker `CloudGroup.watchMembers()`-Listener (`watchPendingGroup()`), solange `pendingGroupId` gesetzt ist. Sobald `members.length > 1`, trägt sie neue/gelöschte Meals und noch leere Wochenplan-Slots nach (belegte Slots der beigetretenen Person werden nicht überschrieben), setzt `status: "active"` und `users/{uid}.groupId`, danach `switchGroup()`.
* **Beim Start:** `startCloudSync()` prüft `remote.pendingGroupId` einmalig über `fetchMembers()`, *bevor* `wantGid` ermittelt wird — gelingt die Aktivierung, wird `remote.groupId` im selben Durchlauf gesetzt und über `enterGroupSync()` normal eingelesen (kein rekursiver `switchGroup()`-Aufruf aus einem laufenden `startCloudSync()` heraus). Deckt ab, dass der Owner offline war, als jemand beitrat.

„Einladung zurückziehen“ im Wartezustand (`withdrawPendingInvite()`) löst die vorbereitete Gruppe vollständig auf (`dissolveGroupFirestore()`, auch von `dissolveGroup()` für aktive Gruppen genutzt) und leert `pendingGroupId`/`pendingInviteUrl` — danach ist der Zustand identisch zu vor dem Einladen.

Drei Randfälle werden bewusst behandelt, statt einen zweiten, verwaisten Gruppen-Zeiger entstehen zu lassen:

* **Konto löschen im Wartezustand:** `deleteAccountFlow()` sperrt nicht nur bei aktiver Eigner-Rolle (`syncGid`), sondern auch bei gesetztem `state.pendingGroupId` — sonst bliebe `groups/{gid}` als Karteileiche ohne erreichbaren Owner zurück.
* **Beitritt zu einer fremden Gruppe trotz eigener offener Einladung:** `joinGroup()` zieht eine eigene, andere `pendingGroupId` über `withdrawPendingInvite()` zurück — bewusst erst *nachdem* der Beitritt zur neuen Gruppe bereits geglückt ist (`putMember`/`copyOwnRecipesToGroup`/`CloudSync.save` liefen durch), nicht davor. Andernfalls würde ein Netzfehler zwischen Zurückziehen und Beitritt beide Gruppen kosten. Ohne das Zurückziehen würde ein späterer Beitritt über die alte Einladung `finalizeGroupActivation()` mit dem inzwischen fremden `state.recipes`-Bestand befüllen.
* **Eigene Einladung scannen/öffnen:** `openInviteModal()`/`joinGroup()` prüfen zusätzlich `state.pendingGroupId === inv.gid` — sonst würde die Firestore-Regel den Rollenwechsel auf sich selbst zwar verhindern, der Nutzer sähe aber nur einen generischen Fehler.

### Drei Zustände statt true/false: `enterGroupSync()`

`enterGroupSync()` liefert `"ok"`, `"gone"` oder `"error"`. Die Unterscheidung ist keine Kosmetik, sondern die Grenze zwischen „wir sind nachweislich draußen" und „wir wissen es gerade nicht":

* `"ok"` — drin, alle Listener hängen.
* `"gone"` — Gruppendokument existiert nicht mehr, oder man steht nicht in der Mitgliederliste. **Nur hier** darf `startCloudSync()` `state.groupId` leeren. Eine **leere** Mitgliederliste zählt ausdrücklich nicht dazu: `getDocs()` wirft offline nicht, sondern liefert das leere Cache-Ergebnis — das ergibt `"error"`.
* `"error"` — der Zugriff ist gescheitert (Netz, noch nicht veröffentlichte Regeln, Rate-Limit) oder `CloudGroup` ist gar nicht verfügbar. Über die Mitgliedschaft sagt das nichts aus, der Zeiger bleibt stehen, der nächste Start versucht es erneut.

Bei `"error"` setzt `startCloudSync()` zusätzlich `groupSyncFailed = true`. Dieses Flag hält `pushNow()` davon ab, die Felder `groupId` und `plans` überhaupt in das Kontodokument zu schreiben — dank `merge: true` bleibt der vorhandene Cloud-Stand dann unangetastet. Ohne das Flag würde der Fehlerzustand (`syncGid === null`) als `groupId: ""` hochgeschrieben und die Gruppe für **alle** Geräte des Kontos unauffindbar machen. Das reguläre Verlassen ist davon nicht betroffen: `leaveGroup()` schreibt sein `groupId: ""` selbst und explizit.

Der `"gone"`-Zweig räumt bewusst **nicht** mehr per `removeMember()` auf. `CloudGroup.fetch()` liefert `null` für jedes Leseergebnis ohne Dokument — aus einem Lesevorgang darf keine Löschung folgen.

### Drei Sperren, nicht eine: wann `pushNow()` den `groupId`-Zeiger anfassen darf

`groupSyncFailed` allein reichte nicht, weil es erst *mitten* im `try` von `startCloudSync()` gesetzt wird. `pushNow()` bündelt deshalb drei Bedingungen in `groupKnown`:

| Sperre | gesetzt in | schützt vor |
|---|---|---|
| `syncHandshakeOk` | `startCloudSync()`, unmittelbar vor dem Baseline-Push; zurückgesetzt in `stopCloudSync()` | Abbruch **vor** dem Gruppen-Handshake. `syncUid` ist dann schon gesetzt, die App pusht also weiter — ohne diese Sperre schriebe der nächste `save()` `groupId: ""`. |
| `groupSyncFailed` | bei `enterGroupSync() === "error"`, im `catch` von `startCloudSync()`, `activateGroup()` und `joinGroup()` | ungeklärte Mitgliedschaft nach einem gescheiterten Zugriff |
| `groupTransition` | für die Dauer von `activateGroup()`/`joinGroup()`, `finally` räumt auf | Debounce-Push im Fenster zwischen Cloud-Write und `switchGroup()`, in dem `syncGid` der Cloud absichtlich nachhinkt. Beide Funktionen rufen beim Eintritt zusätzlich `clearTimeout(pushTimer)`. |

Ist `groupKnown` false, fehlen `groupId` **und** `plans` im geschriebenen Objekt — dank `merge: true` bleibt der Cloud-Stand unangetastet. Das reguläre Verlassen ist davon nicht betroffen: `leaveGroup()` schreibt sein `groupId: ""` selbst und explizit.

Aus derselben Logik behandeln die Listener leere Ergebnisse als *ungeklärt*, nicht als Austritt: `watchMembers()` meldet Lesefehler als `null` statt als leere Liste, `onMembersRemote()` steigt bei leerer Liste aus (eine bestehende Gruppe hat immer ≥ 1 Mitglied; das echte Auflösen kommt über `onGroupRemote()`), und `onRemote()` löst bei leerem `remoteGid` **kein** `switchGroup(null)` mehr aus, solange eine Gruppen-Session läuft.

Seit dem Firestore-Offline-Cache gilt dieselbe Vorsicht zusätzlich für `fromCache`-Ergebnisse, nicht nur für leere: siehe „Firestore-Offline-Cache" oben und `docs/TROUBLESHOOTING.md` („`fromCache` ist kein Beweis").

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

Orphan-Schutz: Würde eine Abwahl `uids.length === 0` ergeben, wird stattdessen der komplette
Eintrag entfernt (derselbe Pfad wie `unassign`, inklusive Undo-Toast) — ein Gericht ohne
zugewiesene Person darf nie im Datenmodell existieren.

Die Einkaufsliste (`buildShoppingList()`) trennt pro Zutat `sharedQty` (aus "für alle"-Gerichten,
skaliert erst mit dem globalen `per`-Personenfaktor) von `assignedQty` (aus individuell
zugewiesenen Gerichten, bereits pro Gericht auf `uids.length / (r.portions || 1)` skaliert).
Endsumme: `sharedQty * per + assignedQty`. Bewusste Entscheidung: "für alle"-Einträge verhalten
sich exakt wie vor diesem Feature (unbeeinflusst vom Rezept-`portions`-Feld), nur abweichend
zugewiesene Gerichte werden zusätzlich skaliert.

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
* `renderProgress()` — `rueckblickHtml()` + `weightHtml()` (seit 13.08.2026, B8)

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
(über den 4. Januar, der per ISO immer in KW 1 liegt) und `weekLabel(key)` → `"KW 33 · 10.08."`.

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

### Slot-Einträge: dritte Form `{id, p}` (Portionsfaktor)

Ein Eintrag im Wochenplan ist seit B5 eines von drei Dingen:

| Form | Bedeutung |
|---|---|
| `"rid"` | für alle, volle Portion — der Normalfall, bewusst weiterhin ein blanker String |
| `{id, uids}` | nur für bestimmte Gruppenmitglieder |
| `{id, p}` / `{id, uids, p}` | mit Portionsfaktor aus `PORTION_STEPS` (0,5 / 1 / 1,5 / 2) |

`entryPortion(e)` liefert immer einen der vier erlaubten Werte, `makeEntry(id, uids, p)` baut
die kleinstmögliche Form (`p === 1` erzeugt kein Feld). Die feste Leiter ist kein Detail: eine
freie Kommazahl wäre über `canonJSON()` ein Dauer-Diff (`0.30000000000000004`).

Der Faktor wirkt an drei Stellen — und muss dort auch wirken, sonst ist er Dekoration:
`dayNutOf()` (Tagesbilanz), `buildShoppingList()` (Einkaufsmengen) und `buildPrintable()`
(Ausdruck). Die kcal-Zeile auf der Slot-Karte zeigt ebenfalls den skalierten Wert.

**Falle beim Sync:** `unflattenWeek()` verlangte früher ein `uids`-Array und hätte ein
`{id, p}` von einem anderen Gerät lautlos verworfen — das Gericht wäre dort aus dem Plan
verschwunden. Der Filter lässt jetzt beide Objektformen zu und führt ein Objekt ohne `uids`
und ohne Faktor auf die String-Form zurück (sonst schriebe das Gerät es sofort anders zurück,
als es ankam).

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

Kein Feature ist bisher gesperrt — D1 legt nur die Grenze und den Lesepfad an. Sichtbar ist der
Status als „Pro"-Marke im Profilmenü. Die serverseitige Durchsetzung für Cloud-Sync und Gruppen
steht als vorbereiteter, **noch nicht aktiver** Helfer in `firestore.rules`; sie scharf zu
schalten, bevor D1b (lokaler Modus als Regelfall) steht, würde jeden bestehenden Zugang
aussperren.

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
{ r, portions, days[], runs, perRun }
```

* `portions` = Σ `entryPortion(entry) × Esser`, wobei Esser = `uids.length` bzw. `shopPersons()`
* `runs` = `Math.ceil(portions / r.portions)`, nur wenn `portions` am Rezept gepflegt ist
* Zeitraum identisch zu `buildShoppingList()`: aktuelle Woche ab heute, nächste Woche ganz

Kein eigener State, kein neues Datenfeld — reine Ableitung. Die Ansicht (`openBatchCooking()`)
ist ein Modal ohne Bedienzustand, der Einstieg liegt im Überlaufmenü des Wochenplans
(`togglePlanMenu()`).

### Wochenarchiv `state.weekStats`

`pruneWeeks()` hält nur die aktuelle und die nächste Woche. Bevor eine vergangene Woche
verworfen wird, sichert `archiveWeek()` ihre Kennzahlen — bewusst **nur Zahlen**, keine
Meal-Referenzen und keine Fotos:

```
weekStats["2026-W29"] = { kcal, days, hit, target }
```

* `kcal` — Ø geplante Tageskalorien über die geplanten Tage
* `days` — Anzahl geplanter Tage (1–7)
* `hit` — Tage innerhalb ±10 % des Tagesziels
* `target` — **das damals gültige** mittlere Tagesziel (seit 13.08.2026, B10)

`target` ist der Kern: Ohne es misst der Rückblick jede vergangene Woche gegen das heutige
Ziel, und eine Zieländerung schreibt die Bedeutung der gesamten Historie um. Trainings- und
Ruhetage haben unterschiedliche Ziele, deshalb der Schnitt über die geplanten Tage.

`sanitizeWeekStats()` klemmt alle Werte, hält höchstens 26 Wochen und übernimmt `target` nur
im plausiblen Bereich (500–20 000 kcal). Wochen ohne `target` sind vor B10 archiviert; der
Rückblick fällt dort auf das heutige Ziel zurück (`avgDailyTargetToday()`). Eine Migration
gibt es nicht — der alte Zielstand ist nicht rekonstruierbar.

Der Rückblick selbst (`rueckblickHtml()`) normiert jeden Balken auf **sein eigenes**
Wochenziel und kann das ±10-%-Band deshalb als feste Fläche zeichnen. Siehe
`docs/TROUBLESHOOTING.md` Punkt 72 für den Zustand davor.

### Merkmale eines Meals: `tags[]`, `mealPrep`, `difficulty`

Drei optionale Felder, seit 13.08.2026. Sie sind die Grundlage für den Meal-Filter, die
kuratierte Bibliothek und den späteren Auto-Wochenplaner — ohne sie ist keines davon baubar.

* **`tags`**: Array aus **festen Schlüsseln** — `highprotein`, `lowcarb`, `vegetarisch`,
  `vegan`, `glutenfrei`, `laktosefrei` (Quelle: `RECIPE_TAGS`). Bewusst **keine Freitext-Tags**:
  die schriebe jeder Nutzer anders (`lowcarb`/`Low Carb`/`low-carb`) und weder Filter noch
  Planer könnten damit rechnen. Die **Schlüssel** stecken in Nutzerdaten und geteilten Meals und
  dürfen sich nie ändern; die Beschriftungen dürfen es.
* **`mealPrep`**: Boolean, „lässt sich vorkochen".
* **`difficulty`**: `1 | 2 | 3` (Einfach / Mittel / Aufwendig). Zahl statt Text, damit später
  danach sortiert werden kann.

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
  `PIECE_TOP`/`pieceTop()` ist die kurze feste Auswahl, die der Picker ohne Suchbegriff zeigt.

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

## Meal-Ansicht: eine Oberfläche statt zweier (`openMealSheet`)

Ein Meal hatte früher drei getrennte Oberflächen: die Karte in der Liste, ein Ansehen-Modal
(`openRecipeDetail`) und ein Bearbeiten-Modal (`openRecipeForm`). `openMealSheet(id, prefill,
originEl)` ersetzt beide Modals durch eine einzige Ansicht, die am Rechner aus der Karte (bzw.
einem Wochenplan-Slot) per FLIP-Animation wächst, am Handy als Bottom-Sheet hochfährt, direkt
bearbeitbar ist und automatisch speichert. Details und der ursprüngliche Plan stehen in
`plans/MealAnsicht.MD` (Umbau abgeschlossen, Schritte 1–5).

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

## Architekturprinzip

Bei mehreren möglichen Lösungen gewinnt grundsätzlich die Lösung mit:

1. besserer Wartbarkeit
2. besserer Skalierbarkeit
3. klarerer Modularität
4. besserer UX
5. weniger technischer Schuld

Provisorische Lösungen nur dann, wenn eine saubere Lösung aktuell nicht sinnvoll machbar ist.
