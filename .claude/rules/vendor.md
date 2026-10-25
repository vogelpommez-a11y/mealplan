---
paths:
  - "vendor/**"
  - "tools/firebase-vendor.py"
---

# Fremdcode unter `vendor/` (ausgelagert aus CLAUDE.md §16)

Firebase-SDK und ZXing liegen **lokal**, nicht auf einem CDN (kein Nachladen zur Laufzeit). Wird
nicht zurückgedreht, auch nicht „weil ein CDN einfacher zu aktualisieren ist“.

* Aktualisieren nur über `tools/firebase-vendor.py`; danach Version, Quelle und SHA-256 in
  **`vendor/HERKUNFT.md`** nachtragen.
* Update **nur mit Anlass** (Sicherheitslücke, konkreter Fehler) — nie wegen einer höheren
  Versionsnummer.
* Niemand merkt von selbst, wenn eine Bibliothek altert: dafür Agent `lieferkette`.
* Apache-2.0-Lizenzhinweise bleiben mitgeliefert (`LICENSE`).
