# HERKUNFT.md

# Woher der Fremdcode stammt — und ob er noch unverändert ist

Angelegt am **27.08.2026**, nachdem der Agent `lieferkette` bei seiner Prüfung feststellen
musste: Die Unversehrtheit der Dateien war **nicht belegbar**. Es gab keine Prüfsummen, und
die ZXing-Version stand nirgends in `vendor/` selbst — nur als Kommentar in `index.html`.
Beides ließ sich nur durch einen Abruf beim Originalserver klären, und das auch nur für eine
der vier Dateien.

> **Wofür diese Datei taugt — und wofür nicht.** Die Prüfsummen unten belegen, dass eine
> Datei **seit dem Abzug** nicht mehr angefasst wurde. Sie belegen **nicht**, dass sie mit
> dem Original beim Hersteller identisch ist. Warum, steht im nächsten Abschnitt.

---

## 1. Firebase JS SDK

| | |
|---|---|
| Version | **10.12.5** |
| Bezogen von | `https://www.gstatic.com/firebasejs/10.12.5/<name>` |
| Bezogen über | `tools/firebase-vendor.py` — **nicht von Hand** |
| Lizenz | Apache 2.0, Volltext liegt als `vendor/firebase/10.12.5/LICENSE` bei |
| Zuletzt geprüft | 27.08.2026 durch `lieferkette`: kein Update-Anlass |

### Warum die Prüfsumme nicht der des Originals entspricht

`tools/firebase-vendor.py` nimmt **zwei bewusste Eingriffe** vor, sonst liefen die Dateien
hier nicht:

1. Der absolute gstatic-Import auf `firebase-app.js` wird auf den relativen Pfad
   `./firebase-app.js` umgeschrieben. Ohne das lüde die App beim Start doch wieder aus dem
   Netz — und verstieße gegen Apple 2.5.2 und den Offline-Start (`CLAUDE.md` Abschnitt 1).
2. Die `sourceMappingURL`-Zeile fällt weg, weil die `.map`-Dateien nicht mitgeliefert werden.

**Ein Abgleich gegen gstatic muss diese zwei Unterschiede also erwarten.** Wer die Herkunft
wirklich prüfen will, lässt `tools/firebase-vendor.py` erneut laufen und vergleicht das
Ergebnis mit den Werten unten — nicht die Rohdatei vom Server.

### Prüfsummen (SHA-256, Stand 27.08.2026)

| Datei | Bytes | SHA-256 |
|---|---|---|
| `firebase-app.js` | 104.992 | `9c93295170e5a12d049cd5fc4ae83b3bb3162df0b761f2cc953da73d0bc9569f` |
| `firebase-auth.js` | 150.917 | `d1cc7b53358f6515eaf306215a70271e443ad6929983630cb39e51176bcc23e0` |
| `firebase-firestore.js` | 437.974 | `1fde763a488e294d33673bee8b7435b8bc73ebdfb687fe656720b929446e1cbf` |
| `LICENSE` | 11.358 | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `README.md` | 1.063 | `0d44d7ac7f3aec79c20a062b69a06797beeb0804541a89b1c631d7dbe61b7e1d` |

---

## 2. ZXing

| | |
|---|---|
| Version | **0.21.3** (`@zxing/library`, npm) |
| Lizenz | Apache 2.0 — Hinweis in der `LICENSE` im Projektwurzelverzeichnis, Abschnitt „AUSNAHMEN" |
| Geladen | **verzögert**, erst beim ersten Scan bzw. QR-Code (`loadZXing()`), nicht beim Start |
| Zuletzt geprüft | 27.08.2026 durch `lieferkette`: keine CVEs gefunden |

**Die Datei nennt ihre Version nicht selbst.** Sie ist minifiziert, dabei ist auch der
Lizenzkopf verlorengegangen. Die Versionsangabe stand bis heute nur als Kommentar in
`index.html` (bei `loadZXing()`) — an einer Stelle, an der niemand sie sucht, der `vendor/`
prüft. Deshalb steht sie jetzt hier.

| Datei | Bytes | SHA-256 |
|---|---|---|
| `zxing.min.js` | 336.008 | `d7cc8f69dd70bdcf3ac00c9ae572bf2acb9f4132ba379c72df842e4db918652d` |

---

## 3. Prüfsummen nachrechnen

```powershell
# PowerShell
Get-FileHash vendor\zxing.min.js -Algorithm SHA256

# Bash
sha256sum vendor/zxing.min.js
```

Weicht ein Wert ab, ist das **kein automatischer Alarm** — es kann ein bewusstes Update
gewesen sein, bei dem nur diese Datei nicht nachgetragen wurde. Die Frage lautet dann:
*Wer hat wann und warum?* Findet sich darauf keine Antwort in der Git-Historie, ist es
ein Befund.

## 4. Was beim nächsten Update zu tun ist

`CLAUDE.md` Abschnitt 16 gilt unverändert: **Update nur mit Anlass** — eine Sicherheitslücke
oder ein konkreter Fehler. Eine höhere Versionsnummer allein ist keiner, weil es keine
Testsuite gibt, die ein Update auffängt.

Kommt ein Update, gehört zum selben Arbeitsschritt:

1. `python tools/firebase-vendor.py` laufen lassen (nie von Hand kopieren).
2. Die Tabellen hier **neu ausrechnen** — Version, Bytes, SHA-256.
3. Den Anlass hier vermerken: welche Lücke, welcher Fehler, welches Datum.
4. `lieferkette` laufen lassen und `docs/STORE.md` gegenlesen (Apple 2.5.2).

> **Noch offen:** `tools/firebase-vendor.py` schreibt diese Datei nicht selbst fort — die
> Tabellen werden heute von Hand gepflegt. Genau daran ist die alte Fassung gescheitert:
> Was von Hand gepflegt wird, altert still. Das Nachrüsten ist für eine eigene Sitzung
> vorgemerkt.
