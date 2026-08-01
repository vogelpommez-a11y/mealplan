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

### `window.CloudGroup`

Verantwortlich für:

`groups/{gid}`

mit:

* `members/{uid}`
* `plans/{weekKey}`
* `recipes/{rid}`
* `invites/{code}`

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

## Gruppen-Wochenplan

Der Plan wird als ein Dokument pro ISO-Woche gespeichert.

Slots sind flach aufgebaut, z. B.:

`mon_fr: ["r1"]`

Schreibvorgänge verwenden:

`setDoc(..., { merge: true })`

und eine Baseline über:

`lastPushedSlots`

Ziel ist, dass parallele Änderungen nur denselben Slot kollidieren lassen und nicht den gesamten Wochenplan überschreiben.

## Wichtige Gruppen-Sync-Regeln

Wenn `syncGid` gesetzt ist:

`dataJSON` darf `plans` nicht enthalten.

Sonst können:

* `state.plans`
* `data.plans`

gegenseitig Snapshot-Vergleiche auslösen und Endlosschleifen erzeugen.

Leere Slots werden aus der Baseline entfernt.

Nicht als `"[]"` speichern.

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

## Architekturprinzip

Bei mehreren möglichen Lösungen gewinnt grundsätzlich die Lösung mit:

1. besserer Wartbarkeit
2. besserer Skalierbarkeit
3. klarerer Modularität
4. besserer UX
5. weniger technischer Schuld

Provisorische Lösungen nur dann, wenn eine saubere Lösung aktuell nicht sinnvoll machbar ist.
