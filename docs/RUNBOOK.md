# RUNBOOK.md

# Betriebshandbuch

Für den Moment, in dem etwas nicht funktioniert und man **nicht** in Ruhe nachdenken kann.
Deshalb kurz, in Schritten, ohne Erklärungen, die man dann nicht lesen will.

**Register:**

| Lage | Abschnitt |
|---|---|
| Ich will veröffentlichen | 1. Deploy |
| Die Seite ist leer | 2. Erste Diagnose |
| Ich muss zurück | 3. Rollback |
| Sync spinnt | 4. Cloud-Störungen |
| Ein Schlüssel ist geleakt | 5. Notfälle |
| Wer hilft wobei | 6. Zuständigkeiten |

---

## 1. Deploy

Ausführlich als Skill: `/deploy`. Kurzform:

```powershell
python syntax-check.py --alles  # muss gruen sein
git push origin main
git ls-remote origin refs/heads/main    # muss...
git rev-parse HEAD                      # ...hiermit uebereinstimmen
```

Dann prüfen, ob GitHub Pages die neue Fassung wirklich ausliefert — mit Cache-Buster und
einer Zeichenfolge, die es nur im neuen Stand gibt. **HTTP 200 beweist nichts.**

Bei Änderung an `sw.js`: `VERSION` erhöht?

---

## 2. Erste Diagnose: die Seite lädt, aber ist leer

Das ist der häufigste Ernstfall und fast immer dieselbe Ursache.

**Schritt 1 — eine Sekunde:**

```powershell
python syntax-check.py --alles
```

Ein Syntaxfehler beendet das gesamte App-Script. Der statische Header bleibt sichtbar,
`#view` bleibt leer, HTTP ist 200. Sieht aus wie ein Server-Problem, ist keines.

**Schritt 2 — ist es lokal oder live?**

| lokal kaputt | live kaputt | Schluss |
|---|---|---|
| ja | ja | Der Code. Weiter mit Rollback oder Fix. |
| nein | ja | Auslieferung: alter Pages-Stand, Service-Worker-Cache, Cloudflare. |
| ja | nein | Ungespeicherte lokale Änderung. Nicht pushen. |

**Schritt 3 — bei „nur live":** Mit Cache-Buster (`?cb=123`) laden. Kommt dann die richtige
Fassung, hält ein Cache fest — `VERSION` in `sw.js` erhöhen und deployen.

---

## 3. Rollback

```powershell
git revert <kaputter-commit>
git push origin main
```

**`git revert`, nicht `reset --hard`.** Revert erzeugt einen neuen Commit, der die Änderung
zurücknimmt, ohne die Historie umzuschreiben. Ein erzwungener Push auf `main` zerstört den
Stand, auf den sich alles andere bezieht.

Danach erneut prüfen, ob Pages den Revert ausliefert. Der Revert ist erst live, wenn er
ankommt.

**Firestore-Regeln sind nicht Teil des Rollbacks.** Sie leben in der Firebase-Konsole. Eine
Regeländerung wirkt sofort und unabhängig vom Deploy — und ein Revert im Repo ändert dort
gar nichts.

---

## 4. Cloud-Störungen

**Anmeldung schlägt fehl, obwohl die App lädt**
→ Firebase Authorized Domains prüfen. **Beide** Ursprünge müssen eingetragen sein:
`www.paddysmealplan.de` und `vogelpommez-a11y.github.io`. Nach einem Domainwechsel ist das
der erste Verdacht (TROUBLESHOOTING 1).

**Zugriff verweigert, obwohl er erlaubt sein sollte**
→ Der veröffentlichte Regelstand in der Konsole weicht von `firestore.rules` ab. Das Repo
ist nur die Vorlage (TROUBLESHOOTING 2). Nachsehen, nur lesend:
`python tools/regeln-live.py`. Das Skript unterscheidet „nur Kommentare“ von „Regeln weichen
ab“ und **vermerkt jeden Lauf** in `.claude/.letzter-regelvergleich`.

**Zwei Geräte schaukeln sich hoch**
→ `updatedAt` **in der Cloud** beobachten, nicht die Anzeige. Steigt der Zeitstempel,
obwohl niemand etwas tut, schreiben sich die Geräte gegenseitig hoch
(TROUBLESHOOTING 34/44). Messweg: `/abnahme`.

**Etwas fehlt nach dem Sync**
→ Ein Sync-Feld braucht **zwei** Merge-Stellen. Ein isolierter Prüfstand sieht einen
fehlenden Aufrufer nicht — Beweis sind der Cloud-Lauf und der `git diff`.

**„Dein Austritt ist nicht ganz gespeichert“ / nach dem Austritt bei jedem Start
„Die Gruppe ist gerade nicht erreichbar“**
→ Die Mitgliedschaft ist beendet, im Kontodokument steht aber noch die alte `groupId`. Der
Nutzer kann das nicht selbst lösen. In der Firebase-Konsole unter `users/{uid}` das Feld
`groupId` auf `""` setzen (uid vom Nutzer erfragen oder in Authentication nachsehen), danach
App neu laden lassen. Vorher prüfen, dass `groups/{gid}/members/{uid}` wirklich fehlt —
sonst ist er noch Mitglied und das Problem ein anderes (TROUBLESHOOTING 192).

**Die Linkvorschau zeigt nichts**
→ Der Cloudflare Worker fällt bei jedem Fehler still auf die GitHub-Pages-Antwort zurück.
Das ist Absicht: Er darf die App nie blockieren. Prüfen: Route aktiv? Secrets gesetzt?
Token abgelaufen?

---

## 5. Notfälle

### Daten sind verloren oder überschrieben

Seit dem 17.09.2026 gibt es einen Weg zurück. **Nicht sofort zurückspielen** — erst sehen,
was passiert ist.

```powershell
# 1. Sofort sichern, WAS JETZT DA IST. Auch ein kaputter Stand ist Beweismaterial.
python tools/firestore-backup.py

# 2. Ansehen, was ein Rückspiel täte - das ist die Voreinstellung, es schreibt nichts.
python tools/firestore-restore.py --stand 2026-09-17-1430 --nur users/<uid>

# 3. Erst wenn die Liste stimmt:
python tools/firestore-restore.py --stand 2026-09-17-1430 --nur users/<uid> --schreiben
```

**Die Regeln dabei:**

* **`--nur users/<uid>` ist der Normalfall.** Der realistische Schaden trifft ein Konto, nicht
  die Datenbank. Alles zurückzuspielen überschreibt auch alles, was seit der Sicherung
  entstanden ist — bei anderen Leuten.
* **Der Trockenlauf ist keine Formalie.** Er zeigt jedes Dokument, das zurückkäme oder
  überschrieben würde, samt der Felder, die dabei wegfallen. Wer ihn überspringt, sieht den
  Schaden erst danach.
* **Gelöschte Konten nicht wiederbeleben.** Wurde ein Konto auf Verlangen gelöscht, darf ein
  Rückspiel es nicht zurückholen (`docs/DATENSCHUTZ-INTERN.md` 3a). Seit dem 30.09.2026
  erzwingt das Skript das selbst: Es fragt vor dem Schreiben Firebase Auth und meldet Dokumente
  toter Konten als `GESPERRT`. Scheitert die Abfrage, bricht es ab — dann erst die Anmeldung
  reparieren, nicht den Schalter setzen. Nur wenn die Person ausdrücklich um Wiederherstellung
  eines versehentlich gelöschten Kontos bittet: `--auch-geloeschte`.
* Zurückgespielt wird **nie gelöscht**: Was live steht und nicht in der Sicherung ist, bleibt.

Läuft die Anmeldung nicht: `gcloud auth login` — nicht `application-default login`, das Skript
fragt das Token über `gcloud auth print-access-token` ab. Die Sicherungen liegen in
`Mealplan-Backups/` neben dem Projektordner, **nie im Repo**.

Erster echter Lauf am 18.09.2026 (`2026-09-18-1515`): fünf Sammlungen, 500 Dokumente, rund
17 MB, etwa eine Minute. Das Skript kennt kein `--help` — jeder Aufruf **sichert sofort**.

**Meldet die Sicherung `ACHTUNG: … Elterndokument, das es nicht mehr gibt`:** Das sind Reste
einer Konto- oder Gruppenlöschung, in die ein zweites Gerät hineingeschrieben hat. Sie werden
bewusst **nicht** gesichert, und nach Ziffer 10 der Datenschutzerklärung müssten sie längst
weg sein. Die Meldung listet die Pfade auf. Diese Pfade in der Firebase-Konsole ansehen und
löschen. Stammen sie von einem **lebenden** Konto, ist das ein Fehler in der App und kein
Rest (`docs/TROUBLESHOOTING.md` §170).

**Jede Sicherung räumt vorher abgelaufene Löschsperren weg** (`loeschsperren/{uid}`, §172).
Das ist das Einzige, was das Skript in Firestore verändert. Eine TTL-Richtlinie würde das
automatisch erledigen, braucht aber den Blaze-Tarif. Deshalb gehört die Sicherung zur
**monatlichen Wartung**, Schritt 0 in der Wartungserinnerung, und Ziffer 10 der
Datenschutzerklärung sagt „bei unserer nächsten Wartung“ zu, ohne feste Frist.
`wartung-check.py --setze` verweigert das Abhaken, wenn die jüngste Sicherung älter als 24 h
ist. Scheitert das Aufräumen, läuft die Sicherung trotzdem, und der nächste Lauf versucht es
erneut. Ebenso verweigert es ohne Bericht `plans/rechtspruefung-*.md` der letzten 30 Tage
(`/rechtspruefung`, `docs/TESTING.md` 2j).
Ebenfalls zur Wartung (Schritt 3 der Erinnerung, ohne Sperre - bis 2027/28 gibt es dort
nichts zu tun): `tools/shared-aufraeumen.py` (abgelaufene Teilen-Links) und
`tools/konten-inaktiv.py` (24 Monate still). Ziffer 10 sagt beides „bei unserer nächsten
Wartung“ zu. Dazu `tools/fremde-uids-aufraeumen.py` als **Trockenlauf**: Er muss „Nichts zu tun“
melden. Fremde Kennungen in Kopien entstehen seit dem 01.10.2026 nicht mehr (die App bereinigt
beim Austritt und beim Start); meldet er doch etwas, war ein Gerät mit altem Stand unterwegs —
sichern, dann `--schreiben` (§183).
Ebenso `tools/mailnamen-aufraeumen.py` als **Trockenlauf** (Teil der E-Mail als Name in
Mitgliedereinträgen und Teilen-Links, Rechtsprüfung 17.10.2026): Er muss „Nichts zu tun“ melden —
die App schreibt den Rückfall seit dem 17.10.2026 nicht mehr. Meldet er etwas: sichern, dann `--schreiben`.

### Schritt 0b: der Live-Stand der Regeln

```powershell
python tools/regeln-live.py       # nur lesend, braucht `gcloud auth login`
```

**Warum das in die Wartung gehört und nicht in den Pushcheck** (Phase E5, angebunden am
20.09.2026): Die Firestore Security Rules sind die **einzige** Sicherheitsgrenze, und
`firestore.rules` im Repo ist nur eine Vorlage. Der veröffentlichte Stand kann sich ändern,
ohne dass im Repo eine Zeile anders wird — ein Push löst also gar nichts aus, an das man
sich hängen könnte.

> **Ein Beleg über den Live-Stand altert lautlos.** Genau deshalb braucht er eine Frist statt
> eines Auslösers.

`wartung-check.py` fährt den Vergleich **nicht selbst** — er braucht Netz und eine
gcloud-Anmeldung. Es liest nur den Vermerk und meldet:

| Lage | Meldung |
|---|---|
| nie belegt, unlesbar, oder älter als 30 Tage | **gelb** — einmal laufen lassen |
| letzter Lauf: `nur Kommentare` | **gelb** — Regeltext stimmt, `firestore.rules` nachziehen |
| letzter Lauf: `ABWEICHUNG` | **rot** — der durchgesetzte Regeltext ist ein anderer |
| letzter Lauf: `identisch`, keine 30 Tage her | still |

Ein **gescheiterter** Lauf schreibt bewusst nichts. Sonst sähe ein Abbruch wegen fehlender
Anmeldung aus wie eine bestandene Prüfung — und das ist der Fehler, den dieses ganze
Wartungssystem verhindern soll.

### Ein Schlüssel ist geleakt

**Rotieren, sofort — nicht erst aufräumen.** Ein Schlüssel, der einmal irgendwo stand, ist
verbrannt; die Git-Historie und Sitzungsprotokolle bleiben.

| Schlüssel | Weg |
|---|---|
| `GCP_SA_PRIVATE_KEY` | Google Cloud Console → Service-Account → neuen Schlüssel, alten löschen → Cloudflare-Secret aktualisieren |
| `OPENAI_API_KEY` | platform.openai.com → widerrufen → neuen anlegen → `.env` ersetzen |

Danach: Sind personenbezogene Daten betroffen? Wenn ja → **Art. 33 DSGVO, 72 Stunden ab
Kenntnis**, Ablauf in `docs/DATENSCHUTZ-INTERN.md`.

### Etwas Nichtöffentliches wurde committet

Wenn **noch nicht gepusht**:

```powershell
git reset --soft HEAD~1
git restore --staged <pfad>
```

Wenn **schon gepusht**: Es ist öffentlich. Das Löschen des Commits entfernt es nicht aus
Forks, Caches und Suchindizes. Reihenfolge: erst den Wert entwerten (Schlüssel rotieren,
Datei bei Personenbezug melden), dann die Historie bereinigen, dann prüfen, warum der
Commit-Wächter nicht gegriffen hat.

### Eine Lücke in den Regeln

Regel in der Firebase-Konsole korrigieren und **veröffentlichen** — wirkt sofort,
unabhängig vom Deploy. `firestore.rules` im Repo im selben Schritt nachziehen, sonst
driften Vorlage und Wirklichkeit auseinander.

---

### Löschung und Auskunft durch den Betreiber

Zwei Fälle, in denen nicht der Nutzer in der App löscht, sondern wir: ein **Löschantrag per
E-Mail** (Ziffer 10) und ein **verwaistes Konto** nach 24 Monaten (`tools/konten-inaktiv.py`).
Dazu die **Auskunft** nach Art. 15/20 (Ziffer 11). Alle drei müssen **dieselben Orte** erreichen
wie der App-Weg `kontoDatenLoeschen()` in `index.html` — nicht nur `users/{uid}`. Wer nur das
Konto löscht, lässt Name und Bild im Mitglieds-Eintrag, Teilen-Links und Einladungen stehen
(Rechtsprüfung 01.10.2026).

**Ablauf je Antrag:**

1. **Identität prüfen** (Art. 12 Abs. 6): Antwort nur an die E-Mail-Adresse, die im Konto
   hinterlegt ist (Firebase-Konsole → Authentication). Kommt der Antrag von einer anderen Adresse,
   dort nachfragen, nicht an die fremde Adresse antworten — eine Auskunft an die falsche Person
   ist selbst eine Datenpanne.
2. **Frist:** innerhalb eines Monats (Art. 12 Abs. 3). Eingang und Erledigung datieren.
3. **Sichern:** `python tools/firestore-backup.py`.
4. **Löschsperre setzen** — wie die App: Dokument `loeschsperren/{uid}` mit Feld `bis`
   (Zeitstempel, jetzt + 2 h) in der Firestore-Konsole anlegen. Ein bereits ausgestelltes
   ID-Token bleibt nach dem Löschen in Authentication noch bis zu einer Stunde gültig; ohne
   Sperre könnte ein angemeldetes Zweitgerät Reste neu schreiben (`docs/TROUBLESHOOTING.md`
   §172). Die Sperre räumt die nächste Sicherung weg.
5. **Die sieben Orte** unten abarbeiten, danach das Konto in **Authentication** löschen.
6. **Nachweis** (Art. 5 Abs. 2) — in `docs/DATENSCHUTZ-INTERN.md` Abschnitt 4, **ohne Klardaten**:
   Datum Eingang, Datum Erledigung, Art (Löschung/Auskunft), „sieben Orte geprüft“. Keine UID,
   keine E-Mail-Adresse.

| # | Ort | Löschen | Auskunft |
|---|---|---|---|
| 1 | `shared/{id}` mit Feld `uid` = UID | Dokument löschen | Liste der Links samt Inhalt |
| 2 | `groups/{gid}/members/{uid}` | löschen **und** `groups/{gid}.memberCount` um 1 senken | Rolle, Name, Bild |
| 3 | `groups/{gid}/recipes/*` mit `by` = UID | `by` auf `""` setzen (Meal bleibt der Gruppe) | betroffene Meals |
| 4 | `groups/{gid}/plans/*` — `by` = UID und Einträge mit UID in `uids` | `by` → `""`; UID aus `uids` nehmen, leere Liste → String-Form | betroffene Wochen |
| 5 | `invites/{code}` mit `by` = UID | Dokument löschen | offene Einladungen |
| 6 | `entitlements/{uid}` | Dokument löschen | Pro-Status |
| 7 | `users/{uid}` samt `users/{uid}/recipes/*` | alles löschen | vollständig, inkl. Fotos in den Meals |

Die App räumt Gruppendaten nur für die **aktuelle** Gruppe (`profil.groupId`); der Betreiberweg
sucht über **alle** `groups/*` — gründlicher, und er erreicht Reste aus früheren Gruppen.

Beim **Löschantrag per E-Mail** und Inhaber einer Gruppe mit weiteren Mitgliedern: nicht
stillschweigend löschen — Ziffer 10 sagt „keine Gruppe ohne Inhaber“. Den Nutzer bitten, die
Gruppe in der App aufzulösen. Für das **verwaiste** Konto gilt der Ablauf unten.

Bei einem **verwaisten** Konto (24 Monate still, gewarnt, 30 Tage verstrichen) gilt seit dem
04.10.2026 (Entscheidung Paddy): **Die Gruppe wird aufgelöst**, nicht übertragen und nicht
aufgeschoben. Ablauf, **vor** den sieben Orten oben:

1. Die UIDs der übrigen Mitglieder aus `groups/{gid}/members` notieren — **vorher**, denn
   die Liste verschwindet mit der Gruppe. Die E-Mail-Adressen stehen **nur in Firebase Auth**
   (nicht in `users/{uid}`, nicht in der Gruppe): über die Auth-Konsole oder dieselbe
   Abfrage wie `tools/konten-inaktiv.py` (`accounts:batchGet`). Jedes Mitglied hat eine:
   Gruppen gibt es nur mit Cloud-Konto, und `handleCloudUser()` lässt nur Konten mit
   bestätigter Adresse (`emailVerified`) in die App. Fehlt trotzdem eine, ist das ein Befund —
   im Vermerk festhalten und nicht ohne Benachrichtigung auflösen.
   Dann informieren: Die Gruppe wird in 14 Tagen aufgelöst; wer die App bis dahin einmal
   öffnet, behält den aktuellen Stand als eigene Kopie.
2. Nach 14 Tagen löschen, was `CloudGroup.dissolve()` löscht: `groups/{gid}/members/*`,
   `…/plans/*`, `…/recipes/*`, dann `groups/{gid}` selbst — dazu die Einladungen
   (`invites/*` mit `gid` dieser Gruppe). Die Profile der Mitglieder **nicht** anfassen:
   Deren App bemerkt beim nächsten Laden `groupResult === "gone"`, behält ihren
   zwischengespeicherten Stand und schreibt ihn ohne `by`/`uids` ins eigene Konto
   (`startCloudSync()`, `hatFremdbezug()`, TROUBLESHOOTING §183) — genau wie beim Auflösen
   aus der App, wo auch nur der Inhaber seine Kopie direkt bekommt.
3. Erst dann das Konto des Inhabers über die Tabelle oben löschen.
4. Vermerk ohne Klardaten bei den Sicherungen (wie der Warnstand von `konten-inaktiv.py`):
   Datum der Mail, Datum der Auflösung, Zahl der Mitglieder, davon ohne erreichbare Adresse.

Warum nicht übertragen: Das bräuchte eine neue Regel in `firestore.rules`, einen neuen
Rechtstext und kollidiert mit „der Inhaber zahlt Pro“. Ob die Formulierung rechtlich trägt,
bleibt als Frage für das Anwaltsgespräch (`docs/DATENSCHUTZ-INTERN.md` Punkt 19, Frage 6).

Ein Admin-Skript dafür gibt es bewusst noch nicht (Entscheidung 01.10.2026: erst bei Bedarf);
bis dahin ist diese Tabelle die Prüfliste. Kommt eins, muss es dieselbe Liste abarbeiten wie
`kontoDatenLoeschen()` — und ein Prüfstand muss beide gegeneinander halten.

### Meldung eines rechtswidrigen Inhalts (DSA)

Seit dem 18.10.2026 nennt das Impressum einen Meldeweg: „Rechtswidrige Inhalte melden“, per
E-Mail. Der Text sagt zu: **„Wir prüfen jede Meldung und melden uns bei dir.“** Dieser Ablauf
ist der Unterbau dafür. Ob und wie weit der DSA hier überhaupt greift, ist offen
(`docs/DATENSCHUTZ-INTERN.md` Punkt 22) — der Ablauf gilt trotzdem, weil der Text es zusagt.

**Fristen (Entscheidung Paddy, 18.10.2026):** Eingang bestätigen binnen **3 Tagen**,
Entscheidung binnen **14 Tagen** mitteilen. Ausnahme: Deutet die Meldung auf eine Gefahr für
Leib oder Leben, **sofort** handeln und die Polizei informieren (Art. 18 DSA).

1. **Eingang bestätigen** — an die Absenderadresse, kurz: Meldung ist angekommen, Entscheidung
   folgt. Fehlt der Link oder die Begründung, danach fragen.
2. **Einordnen:** Wo liegt der Inhalt?
   - **Teilen-Link** (`…?s=<id>` bzw. `shared/{id}`): Nur hier ist ein Inhalt für Dritte
     abrufbar — für jeden Angemeldeten, der den Link hat. Der häufigste Fall.
   - **Gruppe** (`groups/{gid}/recipes/*`): nur für die höchstens vier Mitglieder sichtbar.
     Meldet ein Mitglied, liegt die Gruppen-ID nicht im Link — über die UID des Meldenden in
     `groups/*/members` suchen.
   - **Eigenes Konto** (`users/{uid}`): sieht niemand außer dem Nutzer selbst. Kein Fall für
     diesen Ablauf.
3. **Prüfen**, sorgfältig und ohne Ansehen der Person: Ist der Inhalt offensichtlich
   rechtswidrig (z. B. fremdes Foto mit Urheberrecht, Beleidigung, Bild einer Person ohne
   Einwilligung)? Im Zweifel nicht selbst entscheiden — zurückstellen und anwaltlich fragen.
4. **Entfernen**, wenn ja — vorher `python tools/firestore-backup.py`:
   - Teilen-Link: Dokument `shared/{id}` in der Firestore-Konsole löschen. Wer den Link
     danach öffnet, bekommt „Diesen Link gibt es nicht mehr.“
   - Gruppe: nur das betroffene Meal bzw. Foto in `groups/{gid}/recipes/{id}` entfernen, nicht
     die Gruppe. Im Feld `by` steht die UID dessen, der es angelegt hat.
5. **Mitteilen:** dem Meldenden die Entscheidung; bei Entfernung auch dem, der den Inhalt
   angelegt hat (E-Mail aus Firebase Auth über die UID) — mit kurzer Begründung, was entfernt
   wurde und warum (Art. 17 DSA). Weder dem einen den Namen des anderen nennen.
6. **Vermerk** ohne Klardaten in `docs/DATENSCHUTZ-INTERN.md` Abschnitt 4, wie bei Löschanträgen:
   Datum Eingang, Datum Bestätigung, Datum Entscheidung, Ort (Teilen-Link/Gruppe), entfernt
   ja/nein. Keine UID, keine E-Mail, keine Link-ID.

## 6. Zuständigkeiten

| Frage | Wer beantwortet sie |
|---|---|
| Läuft die App überhaupt? | `/smoke` |
| Funktioniert diese eine Funktion? | `/pruefstand` |
| Stimmt es am echten Konto? | `/abnahme` |
| Darf das live? | `/pushcheck` |
| Kommt das in die Stores? | `store-check` |
| Ist der Fremdcode noch gut? | `lieferkette` |
| Passt Rechtstext zum Code? | `anwalt` |
| Fehlt eine Datenschutz-Pflicht? | `datenschutz-technik` |
| Steht etwas Sensibles öffentlich? | `website-security` |
| Ist die Doku noch wahr? | `doku-waechter` |
| Geht das besser? | `kvp`, `ux-reviewer` |

**Was keiner von ihnen sehen kann:** Firebase-Konsole, Cloudflare-Secrets, Store-Konten.
Siehe `docs/SECURITY.md`, Abschnitt 7.
