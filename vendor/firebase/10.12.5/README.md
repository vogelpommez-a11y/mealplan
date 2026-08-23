# Firebase JavaScript SDK 10.12.5

Unveraendert von `https://www.gstatic.com/firebasejs/10.12.5/` uebernommen, bis auf zwei
Eingriffe, die `tools/firebase-vendor.py` vornimmt und dort begruendet sind:

* In `firebase-auth.js` und `firebase-firestore.js` zeigt der Import von `firebase-app.js`
  jetzt auf `./firebase-app.js` statt auf die absolute gstatic-URL.
* Die `sourceMappingURL`-Zeile ist entfernt (die `.map`-Dateien liegen nicht bei).

Neu holen oder Version wechseln:

```powershell
python tools/firebase-vendor.py 10.12.5
```

## Lizenz

Copyright Google LLC, lizenziert unter der **Apache License 2.0**. Der Lizenztext liegt
daneben als `LICENSE`.

Der Lizenzkopf steht im Quelltext nur in `firebase-app.js` - `firebase-auth.js` und
`firebase-firestore.js` sind minifiziert und haben ihn nicht mehr. Deshalb steht der
Hinweis hier: Apache 2.0 Abschnitt 4 verlangt bei Weitergabe eine Kopie der Lizenz und die
Beibehaltung der Urhebervermerke, und zwei von drei Dateien tragen ihn selbst nicht.

Herkunft: <https://github.com/firebase/firebase-js-sdk>
