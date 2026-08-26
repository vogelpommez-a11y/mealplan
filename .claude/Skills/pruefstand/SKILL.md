---
name: pruefstand
description: Baut einen Ausschneide-Prüfstand für Paddy's Mealplan — schneidet echten Code aus index.html, stubbt fehlende Helfer, fährt ihn headless und prüft mit Gegenprobe gegen den alten Stand. Verwenden, wenn eine Funktion hinter Login, Modal oder komplexem Zustand geprüft werden soll.
---

# Ausschneide-Prüfstand

Die wichtigste Testmethode des Projekts. Es gibt kein Test-Framework — dafür diese eine
Regel: **Getestet wird der echte Produktionscode, ausgeschnitten, nicht nachgebaut.**

## Die eine Grundregel

Nicht abtippen. Nicht manuell kopieren. Keine vereinfachte Nachbildung schreiben.

Ein nachgebauter Test prüft den Nachbau, nicht die App. Er wird grün, während der echte
Code kaputt ist — das ist schlimmer als kein Test.

## Ablauf

### 1. Marker im Original finden

Mit `Grep` die Funktion suchen und zwei eindeutige Grenzen bestimmen — Funktionsanfang und
das schließende `}` auf derselben Einrückungsebene. `index.html` **nie** am Stück lesen.

### 2. Per Python ausschneiden

Ein Build-Skript unter `tools/pruefstand-<thema>.py`, das den Bereich aus `index.html`
herausschneidet und in eine HTML-Datei im Scratchpad schreibt.

**Zusicherungen einbauen.** Regex und Klammernzählung erwischen still den falschen
Bereich. Deshalb festhalten, was drinstehen muss:

```python
assert "CloudGroup.removeMember" not in code
```

Auf **Aufrufe** prüfen, nicht auf bloße Wortvorkommen — `assert "removeMember" not in code`
schlägt schon bei einem Kommentar an, der das Wort erklärt.

### 3. Fehlende Helfer stubben

Nur was der ausgeschnittene Code tatsächlich braucht. Jeder Stub protokolliert seinen
Namen — dazu gleich mehr.

### 4. Headless fahren, Ergebnis nach jedem Schritt ausgeben

```html
<pre id="out"></pre>
```

Nach jedem Prüfschritt aktualisieren. Nur so ist erkennbar, **wo** ein Test hängen bleibt,
statt dass er wortlos nichts liefert.

### 5. Die Gegenprobe — ohne sie zählt kein Ergebnis

Ein Prüfstand, der nur den neuen Code grün zeigt, beweist nichts. Er könnte am Verhalten
vorbeimessen. Deshalb bei jeder Fehlerbehebung denselben Prüfstand gegen den alten Stand:

```powershell
git show HEAD:index.html > "<scratchpad>\index_alt.html"
```

Das Build-Skript nur auf die andere Quelldatei zeigen lassen.
**Der alte Stand muss durchfallen.** Tut er es nicht, prüft der Test nicht das, was er
zu prüfen vorgibt — dann ist der Prüfstand der Befund, nicht der Code.

Variante für eine einzelne Zeile: eine Ganzdatei-Kopie bauen, in der **genau diese Zeile
fehlt**, und zeigen, dass der Test darauf rot wird.

## Fallen, die schon Läufe gekostet haben

**`--virtual-time-budget` wartet nicht auf IndexedDB.** Die virtuelle Uhr läuft ab und
`--dump-dom` feuert, während die IDB-Rückrufe noch in Echtzeit unterwegs sind. Kein
Fehler, kein Log, leeres `<pre>` — sieht aus wie ein Absturz, ist nur Timing.
Lösung: Die Seite meldet aktiv zurück statt auf den Dump zu warten.

```javascript
navigator.sendBeacon("/result", out.join("\n"));
```

Dazu ein kleiner Python-Server, der `POST /result` in eine Datei schreibt. Edge dann
**ohne** `--virtual-time-budget` und **ohne** `--dump-dom` starten und danach beenden.
Für IndexedDB scheidet `file:///` ohnehin aus — über HTTP laden.

**Ein Abbruch mittendrin ist meist ein vergessener Stub.** Nicht raten: den Trace der
Stub-Namen mit ausgeben, der letzte Eintrag zeigt, welche Zeile als Nächstes drankam.
Zusätzlich `window.onerror` und `unhandledrejection` in die Seite hängen — sonst
verschluckt ein `catch` im Produktionscode den Fehler, und der Prüfstand liefert wortlos
nichts.

**`focus()` verfälscht Scroll-Messungen.** Wer Scroll-Positionen misst, darf nicht
nebenbei fokussieren.

**Ein Hänger ist nicht automatisch ein kaputter Prüfstand.** Er kann der Befund sein.

**Ein isolierter Prüfstand sieht keinen fehlenden Aufrufer.** Er prüft die Funktion, nicht
ob sie irgendwo gerufen wird. Bei Sync-Feldern gilt: zwei Merge-Stellen, und der Beweis
sind der Cloud-Lauf (`/abnahme`) und der `git diff` — nicht dieser Prüfstand.

## Erzeugnisse

Die erzeugten `tools/pruefstand-*.html` sind gitignored — sie entstehen bei jedem Lauf neu.
Das **Skript**, das sie baut, gehört ins Repo.

Handgeschriebene Prüfseiten heißen bewusst anders (`tools/mobilprobe-*.html`), damit sie
nicht unter dieses Muster geraten und beim nächsten frischen Checkout verschwinden.

## Danach

Neuen Prüfstand in `docs/TESTING.md` beschreiben: wofür er da ist, und was die Gegenprobe
gezeigt hat.
