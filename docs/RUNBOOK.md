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
ist nur die Vorlage (TROUBLESHOOTING 2).

**Zwei Geräte schaukeln sich hoch**
→ `updatedAt` **in der Cloud** beobachten, nicht die Anzeige. Steigt der Zeitstempel,
obwohl niemand etwas tut, schreiben sich die Geräte gegenseitig hoch
(TROUBLESHOOTING 34/44). Messweg: `/abnahme`.

**Etwas fehlt nach dem Sync**
→ Ein Sync-Feld braucht **zwei** Merge-Stellen. Ein isolierter Prüfstand sieht einen
fehlenden Aufrufer nicht — Beweis sind der Cloud-Lauf und der `git diff`.

**Die Linkvorschau zeigt nichts**
→ Der Cloudflare Worker fällt bei jedem Fehler still auf die GitHub-Pages-Antwort zurück.
Das ist Absicht: Er darf die App nie blockieren. Prüfen: Route aktiv? Secrets gesetzt?
Token abgelaufen?

---

## 5. Notfälle

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
