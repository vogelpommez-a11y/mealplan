---
name: smoke
description: Führt den Standard-Startbeweis für Paddy's Mealplan aus — erst Syntax-Check, dann Edge headless, dann die Prüfung, ob #view tatsächlich App-Inhalt enthält. Verwenden nach jeder Änderung an index.html und immer, wenn die Frage lautet "läuft die App überhaupt noch?".
---

# Smoke-Test

Beantwortet genau eine Frage: **Startet die App, und ist `#view` gefüllt?**

Ein HTTP-200 beweist hier nichts. Bei einem Syntaxfehler bleibt der statische Header
sichtbar und `#view` leer — die Seite sieht auf den ersten Blick heil aus.

## Schritt 1: Syntax-Check, immer zuerst

```powershell
python syntax-check.py
```

Rund eine Sekunde. Prüft jeden `<script>`-Block mit der V8-Engine von Edge, **ohne ihn
auszuführen**, und nennt Fehlermeldung und Zeile.

**Ist er rot, hör hier auf.** Der Smoke-Test würde neun Sekunden lang zeigen, dass ein
Fehler vorliegt, den diese eine Sekunde präzise benannt hat.

## Schritt 2: Ladeweg wählen — das ist keine Formalie

Seit dem 23.08.2026 liegt das Firebase-SDK unter `vendor/firebase/` und wird **relativ**
importiert. Über `file://` blockiert der Browser genau diesen Import. Die App fängt das
nach 6 Sekunden über ihren Timeout ab und startet im **lokalen Modus**.

| Frage | Ladeweg | Erwartete Überschrift in `#view` |
|---|---|---|
| Startet die App überhaupt? | `file://` | „Wie sollen wir dich nennen?" (lokaler Modus) |
| Anmeldung, Firestore, Sync? | `http://localhost:8000` | Cloud-Einstieg, „Willkommen bei Paddy's Mealplan" |

**Ein „Wie sollen wir dich nennen?" über `file://` ist kein Befund.** Wer das für einen
Fehler hält, jagt einen Phantomfehler — genau dafür steht diese Tabelle hier.

Für den HTTP-Weg zuerst:

```powershell
powershell -NoProfile -File test-server.ps1
```

## Schritt 3: Headless laden

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --virtual-time-budget=9000 `
  --user-data-dir="<scratchpad>\edge-profile" `
  --dump-dom "file:///C:/Users/Paddy/Documents/Paddys%20Mealplan/index.html" > dump.html
```

**Edge-Eigenheit, die schon Zeit gekostet hat:** In der Bash-Umgebung liefert die
Umleitung mit `>` unter Umständen nichts. Dann über PowerShell mit `Start-Process` und
`-RedirectStandardOutput` arbeiten. Auch gilt: `--window-size` ist **nicht** derselbe
Wert wie der CSS-Viewport — für Layoutmessungen nie darauf verlassen.

Den Scratchpad-Pfad dieser Sitzung verwenden, nicht `/tmp`.

## Schritt 4: Auswerten — auf Inhalt prüfen, nicht auf Länge

Aus `dump.html` gezielt lesen:

- Enthält `id="view"` tatsächlich Text? Ein leeres `<div id="view"></div>` ist der
  Fehlerfall, auch wenn die Datei 1 MB groß ist.
- Kommt eine der erwarteten Überschriften vor (siehe Tabelle oben)?
- Steht im DOM eine Fehlermeldung aus `window.noteError`?

Nie die ganze Datei in den Kontext laden — sie enthält Base64-Fotos. Gezielt greppen.

## Schritt 5: Ergebnis benennen

Sag klar, was gilt:

- **Grün**: Syntax sauber, `#view` gefüllt, erwartete Überschrift gefunden — und über
  welchen Ladeweg gemessen wurde.
- **Rot**: die Fehlermeldung mit Zeilennummer, nicht „geht nicht".

Der Smoke-Test beweist, dass die App **startet**. Er beweist nicht, dass ein Feature
funktioniert — dafür ist der Ausschneide-Prüfstand da (`/pruefstand`).
