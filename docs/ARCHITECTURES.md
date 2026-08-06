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

Standardweg ist `shareRecipeNow(recipeId)`: ein Tipp, danach direkt das native Share-Sheet (`shareLink()`, analog `shareShopPdf()`/`shareFileOrText()`). Voraussetzung sind eine echte Cloud-Anmeldung (`CloudShare.enabled && authMode === "cloud"` — `enabled` allein sagt nur, dass Firebase konfiguriert ist) und `canShare()` (Gerät hat `navigator.share`); sonst öffnet weiterhin das Modal `openShareRecipe()` mit „Meal-Link erstellen" und Zwischenablage.

`CloudShare.publish()` läuft bewusst ohne `await` parallel zu `shareLink()`, siehe `docs/TROUBLESHOOTING.md` Ziffer 40. `state.shares` wird erst ergänzt, wenn `publish()` erfolgreich war — unabhängig davon, ob der Nutzer das Share-Sheet danach abbricht oder durchführt.

### `window.CloudGroup`

Verantwortlich für:

`groups/{gid}`

mit:

* `members/{uid}`
* `plans/{weekKey}`
* `recipes/{rid}`
* `invites/{code}`

Das Gruppendokument selbst trägt `status: "pending" | "active"` (rein informativ, siehe Wartezustand unten) sowie `name` (per `setName`) und `settings`.

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

### Selbstheilung des Zeigers

`wantGid` in `startCloudSync()` ist `remote.groupId || state.groupId`. Hat ein Fehlerpfad den Cloud-Zeiger geleert, während `groups/{gid}` und die Mitgliedschaft weiterbestehen, holt der nächste Start die Gruppe zurück und `pushNow()` trägt den Zeiger wieder ein. Der reguläre Austritt auf einem anderen Gerät bleibt korrekt: dort ist der eigene Mitglieder-Eintrag gelöscht, `enterGroupSync()` liefert `"gone"`, der Zeiger wird geräumt.

Scheitert `enterGroupSync()` in `startCloudSync()` direkt nach einer gerade erst geglückten Start-Aktivierung (z. B. Netzabbruch im selben Moment), wird `pendingGroupId` wiederhergestellt statt beide Zeiger zu verlieren — sonst wäre die (für den Beitretenden längst aktive) Gruppe für den Owner nicht mehr auffindbar. Scheitert die Aktivierung selbst (live oder beim Start), wird `watchPendingGroup()` erneut angehängt statt die Sitzung dauerhaft ohne Listener zu lassen.

## Gruppen-Wochenplan

Der Plan wird als ein Dokument pro ISO-Woche gespeichert.

Slots sind flach aufgebaut, z. B.:

`mon_fr: ["r1"]`

Schreibvorgänge verwenden:

`setDoc(..., { merge: true })`

und eine Baseline über:

`lastPushedSlots`

Ziel ist, dass parallele Änderungen nur denselben Slot kollidieren lassen und nicht den gesamten Wochenplan überschreiben.

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

Wenn `syncGid` gesetzt ist:

`dataJSON` darf `plans` nicht enthalten.

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
  und Liste dieselbe Menge beschreiben. Der Meal-Picker im Wochenplan zeigt weiterhin **alle**
  Meals: ein einmal gescanntes Produkt soll sich ohne zweiten Scan erneut einplanen lassen.
  Wird **nur** beim stillen Anlegen mit vollständigen OFF-Daten gesetzt —
  bestätigt der Nutzer stattdessen über das normale Formular, bleibt der Eintrag sichtbar, weil
  er ihn aktiv über den Standardweg angelegt hat.

Beide Felder sind additiv: `sanitizeRecipe()` kopiert unbekannte Felder unverändert durch
(`Object.assign({}, r)`), Plan, Einkaufsliste, PDF-Export und Ziel-Ringe kennen ausschließlich
`getRecipe(id)` und bleiben dadurch unverändert funktionsfähig.

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
(Richtung des Übergangs) und `weekJumpDone` (schaltet die Scroll-Wiederherstellung `keepWeekX` in
`render()` für genau einen Durchlauf ab). `renderPlan(sameTab)` verbraucht die Werte einmalig.

Praktisch: Reiterwechsel → heute. Aktuelle → nächste Woche → Montag. Zurück → heute. Meal
einplanen, entfernen oder ein Cloud-Snapshot → Position bleibt, keine Bewegung.

`sameTab` wird von `render()` **als Parameter durchgereicht**, weil `lastRenderTab` dort schon
auf `"plan"` gesetzt ist, bevor `renderPlan()` läuft — ein Reiterwechsel wäre daraus nicht mehr
erkennbar.

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
  `.tabs` ein Grid mit drei gleich breiten Spalten ist (`translateX(i * 100%)` reicht). Am
  Rechner sind die Tab-Knöpfe unterschiedlich breit (Meal-Zähler ändert die Breite) — dort
  bleibt `[aria-selected="true"]` die einzige Fläche. Position wird in `render()` gesetzt,
  **nach** der Scroll-Wiederherstellung, sonst animiert die View während ihre Position noch
  springt.

Bewusst kein echtes Wischen bei Woche und Tabs: das bräuchte alle Ansichten gleichzeitig im DOM
(ein horizontaler Scroller im horizontalen Scroller), auf Touch gewinnt immer der innere
Scroller, und `overscroll-behavior-x: contain` unterbindet die Weitergabe zusätzlich absichtlich.

## Architekturprinzip

Bei mehreren möglichen Lösungen gewinnt grundsätzlich die Lösung mit:

1. besserer Wartbarkeit
2. besserer Skalierbarkeit
3. klarerer Modularität
4. besserer UX
5. weniger technischer Schuld

Provisorische Lösungen nur dann, wenn eine saubere Lösung aktuell nicht sinnvoll machbar ist.
