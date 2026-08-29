# SECURITY.md

# Sicherheitsmodell von Paddy's Mealplan

**Register** — was hier steht:

| Abschnitt | Frage, die er beantwortet |
|---|---|
| 1. Der eine Satz | Wo verläuft die Sicherheitsgrenze? |
| 2. Was geheim ist | Welche Werte erzwingen bei einem Leck eine Rotation? |
| 3. Was öffentlich sein darf | Was ist trotz Aussehen kein Geheimnis? |
| 4. Die Firestore-Regeln | Was setzen sie tatsächlich durch? |
| 5. Bedrohungsmodell | Wer greift an, womit, und was hält? |
| 6. Bekannte Kompromisse | Was ist bewusst offen? |
| 7. Was nicht prüfbar ist | Wo endet die lokale Prüfung — und was zuletzt in der Konsole nachgesehen wurde |
| 8. Im Ernstfall | Was tun bei einem Leck? |
| 9. Offene Härtung | Was bewusst noch fehlt — App Check, Backup, CSP, CI als Bremse |

Dieses Dokument beschreibt das Modell. Der **Meldeweg für Lücken von außen** steht in
`SECURITY.md` im Projektwurzelverzeichnis — das hier ist die interne Fassung.

---

## 1. Der eine Satz

> **Die Firestore Security Rules sind die einzige Sicherheitsgrenze. Alles andere ist
> Bequemlichkeit.**

Alles, was der Client tut — Rollen prüfen, Knöpfe ausgrauen, Ansichten verbergen, ein
Pro-Merkmal abfragen —, ist über die DevTools in Sekunden umgangen. Der Client ist keine
vertrauenswürdige Instanz; er ist die Software des Angreifers.

Daraus folgt die Arbeitsregel: **Jede neue Berechtigung wird zuerst in den Regeln
durchgesetzt und erst danach im Client abgebildet.** Nie umgekehrt.

---

## 2. Was tatsächlich geheim ist

Genau zwei Dinge. Beide liegen außerhalb des Repos, und ein Leck erzwingt bei beiden
**Rotation** — Löschen reicht nicht, weil die Git-Historie und Sitzungsprotokolle bleiben.

| Wert | Wo er liegt | Was ein Angreifer damit könnte |
|---|---|---|
| `GCP_SA_PRIVATE_KEY` — privater Schlüssel des Service-Accounts | Cloudflare Worker Secrets — **erst ab dem Deployment; der Worker läuft heute nicht** | Firestore **an den Regeln vorbei** lesen. Die Rolle ist auf „Cloud Datastore Viewer" beschränkt, also nur lesend — das begrenzt den Schaden, hebt ihn nicht auf. |
| `OPENAI_API_KEY` | lokale `.env`, gitignored | Auf Rechnung des Inhabers Anfragen stellen. |

Geschützt werden sie durch:
- `.gitignore` (`.env`, `*.key`, `*.pem`, `serviceAccount*.json`)
- den **Commit-Wächter** (`.claude/hooks/commit-waechter.py`) — prüft den Index, nicht die Regel.
  Seine `ERLAUBT`-Liste (seit 27.08.2026) nimmt ausschliesslich die vier eigenen Projekt-Skills
  aus, die im selben Ordner liegen wie die zugekauften. Sie steht in `bewerte()` **hinter** den
  harten Verboten (Endungen, Namensmuster): Ein `.env`, `.key`, `.pem` oder `serviceAccount*.json`
  bleibt auch in einem erlaubten Ordner blockiert. In der ersten Fassung stand sie davor und war
  damit ein Generalschlüssel — `docs/TROUBLESHOOTING.md` §123. `tools/wartung-check.py` prüft
  seither beide Richtungen: blockiert er genug, und blockiert er zu viel?
- den **Secrets-Filter** (`.claude/hooks/secrets-filter.py`) — hält `.env` aus Protokollen
- den CI-Lauf `.github/workflows/pruefung.yml`, Job *Keine Geheimnisse im Repo*

Vier Schichten, weil das Repo öffentlich ist und ein Fehler dort nicht rückholbar wäre.

---

## 3. Was öffentlich sein darf — und warum

**Die `firebaseConfig` in `index.html`** (`apiKey: "AIzaSy…"`). Firebase-Web-Schlüssel sind
öffentlich by design: Sie identifizieren das Projekt, sie autorisieren nichts. Wer sie
kennt, kann genau das, was jeder Besucher der Seite ohnehin kann. Der Schutz kommt aus
**Authorized Domains** und den **Security Rules**. Das ist kein Leck und wird nie als
solches gemeldet.

**`firestore.rules` im Repo.** Eine Regel, die nur funktioniert, solange niemand sie kennt,
ist keine Regel. Die Offenlegung ist beabsichtigt und unproblematisch, solange die Regeln
selbst tragen — geprüft und bestätigt am 26.08.2026.

**`worker/og.js`.** Enthält nur die *Namen* der Secrets, nicht deren Werte.

**Name und Anschrift im Impressum.** Nach § 5 DDG vorgeschrieben.

---

## 4. Was die Firestore-Regeln tatsächlich durchsetzen

Stand der Vorlage: 15.08.2026. **Wirksam ist allein der in der Firebase-Konsole
veröffentlichte Stand** (siehe Abschnitt 7).

### Der wichtigste Unterschied im ganzen Regelwerk: `get` ist nicht `read`

`read` = `get` **und** `list`. Wer `allow read` schreibt, wo `get` gemeint ist, erlaubt
jeder angemeldeten Person, die **ganze Sammlung aufzulisten** — auch ohne eine einzige ID
zu kennen.

Genau dieser Fehler war einmal live: `shared/{id}` stand auf `allow read`, während die
Datenschutzerklärung „nur über den Link" zusagte. Jedes geteilte Meal war für jedes
angemeldete Konto auflistbar.

Deshalb steht heute überall dort, wo eine unerratbare ID der Schutz ist, ausdrücklich
`allow get` und daneben `allow list: if false`:

| Sammlung | Regel | Was sie verhindert |
|---|---|---|
| `shared/{id}` | `get`, `list` implizit aus | Auflisten fremder geteilter Meals |
| `groups/{gid}` | `get: isMember`, `list: false` | Auflisten fremder Gruppen |
| `invites/{code}` | `get`, `list: false` | Durchprobieren aller Einladungscodes |
| `entitlements/{uid}` | `get` nur eigene, `create/update: false` | Sich selbst Pro eintragen |

### Was sonst in den Regeln steht, nicht nur im Client

- **Eigene Daten**: `users/{uid}` nur für `request.auth.uid == uid`.
- **Rollen** (`owner`/`edit`/`view`) über `myRole()`/`canWrite()`/`isOwner()`.
- **Mitgliederlimit**: `maxMitglieder() = 4`, geprüft über `memberCount`.
- **Pro-Gating**: `hasPro()` und `groupOwnerHasPro()`. Cloud-Sync ist ausdrücklich gratis;
  Pro trägt nur das **Gründen** einer Gruppe — der Inhaber zahlt, das Beitreten ist frei.
- **UID-Bindung beim Erstellen**: `create` nur mit der eigenen `uid`, damit niemand
  Dokumente in fremdem Namen anlegt.

### Teilen-IDs

Erzeugt über `crypto.getRandomValues` mit 80 Bit Zufall — **nicht** `Math.random`, nicht
`Date.now`. Bei einer ID, die selbst der Schutz ist, ist die Zufallsquelle
sicherheitsrelevant: `Math.random` ist vorhersagbar.

---

## 5. Bedrohungsmodell

| Wer | Womit | Was hält — oder nicht |
|---|---|---|
| **Beliebiger Besucher** | Ruft die Seite auf, liest den Code | Sieht alles, was ohnehin öffentlich ist. Ohne Anmeldung kein Firestore-Zugriff. **Hält.** |
| **Angemeldeter Fremder** | Eigenes Konto, DevTools, direkte Firestore-Aufrufe | Kommt an nichts Fremdes: `list` ist überall aus, `get` braucht eine 80-Bit-ID. **Hält** — das ist der Hauptangreifer, gegen den die Regeln geschrieben sind. |
| **Gruppenmitglied mit `view`-Rolle** | Versucht zu schreiben | `canWrite()` in den Regeln, nicht nur im Client. **Hält.** |
| **Gruppeninhaber** | Manipuliert `memberCount` über DevTools | Kann sich **selbst** schaden (Zähler senken, ohne jemanden zu entfernen). Kein Zugriff auf fremde Daten. Bewusst in Kauf genommen, siehe Abschnitt 6. |
| **Empfänger eines Teilen-Links** | Schickt einen **manipulierten** geteilten Plan | **Die gefährlichste Quelle im ganzen System.** Fremde Inhalte landen im DOM — jede Ausgabe muss durch `esc()`. Ein vergessenes `esc()` ist hier eine echte XSS-Lücke, kein Schönheitsfehler. |
| **Angreifer auf dem Netzweg** | Liest oder verändert Verkehr | HTTPS überall, Auth-Antworten werden vom Service Worker nie gecacht. **Hält.** |
| **Mitbenutzer desselben Geräts** | Öffnet die App nach dem Vorbesitzer | `localStorage` und der SW-Cache sind **geräteweit, nicht kontoweit**. Deshalb muss die Konto-Löschung beide Speicher treffen. |
| **Wer den Service-Account-Schlüssel erbeutet** | Liest Firestore am Regelwerk vorbei | Nur lesend, aber vollständig. Deshalb Abschnitt 2. |

### Die zwei wiederkehrenden Fehlerklassen

1. **`esc()` vergessen** bei fremden Inhalten (geteilte Pläne, Gruppen-Dokumente).
2. **Eine neue Berechtigung nur im Client** gebaut und die Regel vergessen.

Beide sind schon vorgekommen. Sie stehen deshalb im Prüfauftrag von `website-security`.

---

## 6. Bewusste Kompromisse

Kein Versehen, sondern entschieden — und hier festgehalten, damit niemand sie „repariert",
ohne die Entscheidung zu kennen:

- **`memberCount` ist über DevTools vom Inhaber manipulierbar.** Der schlimmste Fall ist
  Selbstschaden. Eine regelseitige Absicherung wäre nur mit einer Cloud Function möglich.
- **Sieben bestehende Gruppen können seit dem 15.08.2026 nicht mehr gemeinsam planen**
  (lesen ja, schreiben nein), weil es nur ein `entitlements`-Dokument gibt. Das ist die
  Pro-Grenze, Entscheidung des Inhabers in Kenntnis der Folge.
- **Die Linkvorschau wird die Regeln bewusst umgehen — sobald sie läuft.** Der Worker
  `worker/og.js` soll mit einem Service-Account **Titel und Bild** eines geteilten Meals an
  *jeden* Aufrufer herausgeben, auch ohne Anmeldung; anders funktioniert keine Vorschau in
  Messengern.
  ⚠️ **Er ist NICHT deployt** (nachgemessen am 26.08.2026). Heute gilt unverändert: geteilte
  Meals sind nur für Angemeldete abrufbar, wie § 8 der Datenschutzerklärung es sagt.
  **Der Rechtstext wird erst MIT dem Deployment geändert, nicht vorher** — die Leitplanke
  steht in `docs/ARCHITECTURES.md`. Am 26.08.2026 wurde genau dagegen verstoßen und die
  Änderung wieder zurückgenommen; der vorbereitete Text liegt in
  `docs/DATENSCHUTZ-INTERN.md`, Abschnitt 7.
- **Pro-Gating ist zusätzlich clientseitig sichtbar.** Das ist Bequemlichkeit; die Grenze
  liegt in `groupOwnerHasPro()`.
- **Der Auto-Wochenplaner ist bei Solo-Konten nur im Client Pro-gesperrt** (`isPro()` in
  `index.html:8645`). Er rechnet auf dem Gerät und schreibt in `users/{uid}` — dort darf
  der Nutzer ohnehin schreiben, und die Regel hat bewusst keine Pro-Prüfung
  (`firestore.rules:112-121`, Entscheidung vom 15.08.2026, damit Cloud-Sync frei bleibt).
  Den Regeln sieht ein fertiger Plan nicht an, wie er entstanden ist.
  **Entschieden am 26.08.2026: bleibt so.** Serverseitig zu rechnen würde den Planer vom
  Netz abhängig machen — gegen die Offline-Zusage und gegen eine Store-Anforderung. Wer die
  Lücke nutzt, braucht Entwicklerwerkzeuge; fremde Daten sind nie betroffen, der Schaden
  ist entgangener Umsatz. Begründung: `docs/PRODUCT.md`, „Wie Pro verkauft wird".
- **Die 34 Katalog-Rezepte in `data/cookbook.js` sind für jeden lesbar.** Sie sind der
  Gratis-Grundstock, das ist gewollt. Künftige **Pro**-Rezepte kommen dagegen aus Firestore
  hinter `hasPro()` — sonst wären sie ab Veröffentlichung im Quelltext öffentlich.

---

## 7. Was aus dem Repo heraus nicht prüfbar ist

Jede rein lokale Prüfung endet hier. **Mit Browser-Zugang zur Konsole ist einiges davon
sehr wohl prüfbar** — der Abschnitt sagt deshalb beides: was lokal nicht geht, und was
zuletzt tatsächlich nachgesehen wurde.

### Am 26.08.2026 in der Konsole gegengeprüft

| Punkt | Ergebnis |
|---|---|
| **Veröffentlichter Regelstand** | Letzte Veröffentlichung **17.08.2026, 20:46** — nach der letzten Änderung an `firestore.rules` (20:39). Der Kopf der veröffentlichten Fassung ist wortgleich mit der Repo-Vorlage. |
| **Regelwirkung, unangemeldet** | `LIST` auf `shared`, `users`, `groups`, `invites`, `entitlements` → **jeweils HTTP 403**. Gemessen gegen die Live-API, nicht aus dem Regeltext geschlossen. |
| **Authorized Domains** | `www.paddysmealplan.de`, `vogelpommez-a11y.github.io`, `localhost` sowie die beiden Firebase-Standarddomains. **Beide Ursprünge sind eingetragen.** |
| **Firebase-Dienstdatenfreigabe** | **aus** (Kästchen leer) |
| **Datenschutzbeauftragter** | keiner eingetragen (nach Art. 37 hier auch nicht erforderlich) |
| **Tarif** | Spark (kostenlos) |

**Die Verhaltensprüfung ist der bessere Beweis als das Lesen des Regeltexts** und dauert
Sekunden:

```bash
BASE="https://firestore.googleapis.com/v1/projects/paddys-mealplan/databases/(default)/documents"
for p in shared users groups invites entitlements; do
  curl -s -o /dev/null -w "$p: %{http_code}
" "$BASE/$p?pageSize=1"
done
# Erwartet: ueberall 403. Ein 200 waere ein Notfall.
```

Diese Prüfung gehört in jeden Sicherheitsdurchgang. Sie deckt allerdings nur den
**unangemeldeten** Fall ab — der gefährlichere Angreifer ist der *angemeldete Fremde*.
Dafür braucht es ein Testkonto (siehe `docs/TESTING.md`, Datenschutz-/Security-Regression).

### Weiterhin nur in der jeweiligen Konsole sichtbar

- Der **vollständige** veröffentlichte Regeltext Zeile für Zeile (der Editor lädt nur den
  sichtbaren Ausschnitt; geprüft wurden Kopf, Veröffentlichungszeitpunkt und Wirkung).
- Die tatsächlich gesetzten **Cloudflare-Secrets** und die Worker-Route. (Ob der Worker
  überhaupt läuft, ist dagegen sehr wohl messbar — siehe unten.)

**Läuft der Worker?** Drei Befehle, Sekunden:

```bash
curl -sI https://www.paddysmealplan.de/ | grep -i server
#   "GitHub.com" = kein Cloudflare davor.  "cloudflare" = Worker-Route aktiv.
curl -s -o /dev/null -w "%{http_code}\n" https://www.paddysmealplan.de/og/test.jpg
#   404 = nicht deployt.
```

Diese Frage vor jeder Aussage über die Linkvorschau stellen — auch in Rechtstexten.
- Die **IAM-Rolle** des GCP-Service-Accounts (soll „Cloud Datastore Viewer" sein).

Bei Aussagen über den Live-Zustand ist das jedes Mal dazuzusagen — mit Datum der letzten
Gegenprüfung.

---

## 8. Im Ernstfall

**Ein Geheimnis ist geleakt:**

1. **Sofort rotieren**, nicht erst aufräumen. Ein Schlüssel, der einmal irgendwo stand,
   ist verbrannt — auch wenn die Datei gelöscht wurde.
   - Service-Account: in der Google Cloud Console neuen Schlüssel erzeugen, alten löschen,
     Cloudflare-Secret aktualisieren.
   - OpenAI: Schlüssel widerrufen, neuen anlegen, `.env` ersetzen.
2. **Dann** die Spur beseitigen — und wissen, dass die Historie bleibt.
3. Prüfen, ob personenbezogene Daten betroffen sind. Wenn ja: **Art. 33 DSGVO, 72 Stunden**
   ab Kenntnis. Ablauf in `docs/DATENSCHUTZ-INTERN.md`.

**Eine Lücke in den Regeln:** Regel in der Firebase-Konsole korrigieren und
**veröffentlichen** — das wirkt sofort und unabhängig vom Deploy. `firestore.rules` im
Repo im selben Schritt nachziehen, sonst driften Vorlage und Wirklichkeit auseinander.

**Die App ist live kaputt:** siehe `/deploy`, Abschnitt „Wenn live etwas kaputt ist".

---

## Verwandtes

- `SECURITY.md` (Projektwurzel) — Meldeweg für externe Finder
- `docs/DATENSCHUTZ-INTERN.md` — Auftragsverarbeiter, Art. 30, TOM, Meldeweg
- `docs/TROUBLESHOOTING.md` Punkte 2, 3, 4, 12, 13 — die historischen Fälle
- `.claude/agents/website-security.md` — der Prüfauftrag, der daraus folgt

---

## 9. Offene Härtung — was bewusst noch fehlt

Aufgenommen am 26.08.2026 nach der Frage „was haben wir vergessen?". Jeder Punkt ist
nachgeprüft, nicht vermutet. Nach Gewicht sortiert.

### 9.1 Firebase App Check fehlt — die größte inhaltliche Lücke

**Kommt im ganzen Projekt nicht vor**: nicht im Code, nicht in einer Doku, in keinem Agenten.

App Check bindet Anfragen an die **echte** App. Er ist damit die naheliegende Antwort auf
zwei Probleme, die in diesem Dokument benannt und offen gelassen sind:

* das nur clientseitig durchgesetzte Pro-Gating am Auto-Wochenplaner (Abschnitt 6)
* fremde Skripte, die mit einem gültigen Konto direkt gegen die Firestore-API sprechen —
  der Hauptangreifer aus dem Bedrohungsmodell (Abschnitt 5)

**Warum es nicht nebenbei geht:** App Check braucht Code in `index.html`, Einrichtung in der
Firebase-Konsole (reCAPTCHA im Web, App Attest unter iOS) und eine Entscheidung über die
Durchsetzung. Falsch eingerichtet **weist er echte Nutzer ab** — er gehört in eine eigene
Sitzung mit Abnahme am echten Konto, nicht in einen Abend nebenher.

### 9.2 Kein Backup der Firestore-Daten

Art. 32 DSGVO nennt die Wiederherstellbarkeit ausdrücklich. Heute gilt: Wenn ein Fehler die
`weekStats` oder die Rezepte eines Kontos überschreibt, **gibt es keinen Weg zurück**.

Geplante Firestore-Exporte setzen den **Blaze**-Tarif voraus — das hängt damit an derselben
Entscheidung wie die Bezahlung (`docs/STORE.md`). Ein einfacherer Zwischenschritt wäre ein
Export über `tools/cdp.py` am eigenen Konto; das deckt allerdings nur das eigene ab.

Steht als offener Punkt auch in `docs/DATENSCHUTZ-INTERN.md`, Abschnitt 3.

### 9.3 Die CI ist eine Meldung, keine Bremse

`main` hat **keinen Branch-Schutz** (am 26.08.2026 über die API geprüft). Schwerer wiegt
aber etwas Strukturelles: **GitHub Pages baut aus dem Branch, die CI läuft erst danach.**
Sie kann melden, dass etwas kaputt ist — verhindern kann sie es nie.

Der echte Fix wäre, über Actions zu deployen statt aus dem Branch: bauen → prüfen → nur bei
grün veröffentlichen. Das ist ein Umbau der Auslieferung, kein Häkchen.

**Bis dahin gilt:** Die Bremse vor dem Push sind der Push-Wächter und `/pushcheck`, nicht
die CI. Wer sich auf die CI verlässt, verlässt sich auf eine Meldung, die zu spät kommt.

### 9.4 Content-Security-Policy nur zur Hälfte

Seit dem 26.08.2026 steht eine `<meta>`-CSP in `index.html`: `base-uri 'self'`,
`form-action 'self'`, `object-src 'none'` — dazu `referrer` auf
`strict-origin-when-cross-origin`. Das blockiert eine klassische XSS-Eskalation über ein
eingeschleustes `base`-Element und verhindert Abfluss über eingeschleuste Formulare.

**Was fehlt und warum:**

* **`script-src`** — die App ist vollständig inline geschrieben. Ohne Build-Schritt bliebe
  nur `'unsafe-inline'`, was genau das erlaubt, wogegen die Direktive schützt. Hashes
  müssten bei jeder Änderung neu berechnet werden; dafür gibt es hier keine Toolchain.
  **Das heißt: Ein vergessenes `esc()` ist weiterhin voll ausnutzbar.**
* **`frame-ancestors` und `X-Frame-Options`** — wirken nur als HTTP-Header und werden im
  `meta` ignoriert. GitHub Pages kann keine Header setzen. Gehört in den Cloudflare Worker,
  sobald der deployt ist — zusammen mit `Referrer-Policy` und `X-Content-Type-Options`.

### 9.5 Kontingent-Erschöpfung auf dem Spark-Tarif

Der Gratis-Tarif hat harte Tageslimits für Lese- und Schreibvorgänge. Wer sie leerläuft —
böswillig mit einem gültigen Konto oder durch einen Fehler in einer Schleife — legt die App
**für alle Nutzer** lahm, bis das Kontingent zurückgesetzt wird. Firestore-Regeln können
nicht drosseln; sie kennen keine Rate.

Auch hier wäre App Check (9.1) die wirksamste Gegenmaßnahme, weil er fremde Clients
aussperrt, bevor sie Kontingent verbrauchen.

### 9.6 Die Prüfstände laufen nirgends automatisch

Sie brauchen Edge und Windows, die CI läuft auf Linux. Seit dem 26.08.2026 gibt es
wenigstens `python tools/alle-pruefstaende.py` für den Reihenlauf auf diesem Rechner —
vorher musste man jeden einzeln aufrufen **und wissen, dass es ihn gibt.**

### 9.7 Was besser ist als erwartet

**GitHub-Secret-Scanning und Push Protection sind aktiv** (API-Abfrage am 26.08.2026).
GitHub blockiert einen erkannten Schlüssel also schon serverseitig, bevor der Push ankommt.
Der Secret-Scan in der eigenen CI ist damit eine **zweite** Schicht, nicht die einzige.

Dependabot ist deaktiviert — folgerichtig, weil es ohne `package.json` nichts zu prüfen
gäbe. Diese Rolle hat der Agent `lieferkette`.
