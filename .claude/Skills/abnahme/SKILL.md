---
name: abnahme
description: Fährt eine Abnahme am echten Cloud-Konto über tools/cdp.py — sichtbarer Chrome per DevTools-Protokoll, der Nutzer meldet sich selbst an, danach liest und klickt das Skript. Verwenden für alles, was ein echtes Firebase-Konto braucht: Anmeldung, Firestore-Schreibvorgänge, Zwei-Geräte-Verhalten.
---

# Abnahme am echten Cloud-Konto

Schließt die Lücke zwischen „headless geht nicht" (kein Login) und „im Prüfstand geht
nicht" (keine Cloud). Alles, was früher als „nur am Gerät prüfbar" beim Nutzer liegen
blieb, ist hiermit prüfbar.

## Die Arbeitsteilung — das ist der Punkt

**Der Mensch meldet sich einmal von Hand an.** Passwörter laufen nie durch das Skript und
stehen in keinem Protokoll. Danach liest und klickt das Skript.

Frag den Nutzer aktiv, wenn die Anmeldung dran ist. Warte darauf. Mach nicht weiter, bevor
er bestätigt hat.

## Werkzeug

```powershell
python tools/cdp.py start          # Chrome mit Fernbedienung, eigenes Profil im TEMP
python tools/cdp.py eval "<js>"    # JavaScript in der App-Seite auswerten
python tools/cdp.py stop
```

Vier Dinge, die den Aufbau überhaupt brauchbar machen — alle nicht selbsterklärend:

- **`--remote-allow-origins=*` beim Start und `origin=` beim Verbinden.** Ohne beides
  lehnt Chrome die Verbindung zum Debug-Port ab: `403 Rejected an incoming WebSocket
  connection`.
- **`awaitPromise: true` und `returnByValue: true`** bei `Runtime.evaluate` — sonst kommt
  bei `await CloudSync.load(uid)` nur eine Objekt-ID zurück statt des Dokuments.
- **Eigenes Profilverzeichnis.** Ein bereits laufender Alltags-Chrome verhindert das
  Debug-Port-Flag sonst stillschweigend; der Alltagsbrowser bleibt unangetastet.
- **`window.CloudSync` ist global.** `CloudSync.load(uid)` ersetzt den Gang in die
  Firebase-Konsole vollständig und liest genau das, was die App sieht. Die `uid` steht in
  `localStorage` unter `wochenkueche_lastprofile_v1__test`.

## Der Ablauf — echte Daten sind im Spiel

`localhost` trennt nur den **lokalen** Speicher (`__test`-Suffix über `localKey()`),
**nicht die Cloud**. Ein Test am echten Konto schreibt in echte Firestore-Daten.

1. **Zuerst sichern.** Das betroffene Feld über `CloudSync.load()` lesen und wegschreiben.
2. Test fahren.
3. **Zurückschreiben und gegenprüfen**, dass die Schlüsselmenge deckungsgleich ist — nicht
   nur ein einzelner Wert.
4. Beide Fenster neu laden, damit keines mit dem alten Zustand weiterpusht.
5. **Chrome beenden.** Ein offener Debug-Port ist eine offene Fernbedienung und darf nicht
   länger laufen als die Abnahme.

Schritt 5 nie vergessen, auch wenn die Abnahme scheitert.

## Messfallen

**`Object.keys(goal)` statt `JSON.stringify(goal)`**, wenn auf ein *fehlendes* Feld
geprüft wird. `JSON.stringify` lässt `undefined` weg — ein fehlendes Feld sieht dann aus
wie ein Skriptfehler statt wie das Ergebnis. Das hat einen Lauf gekostet.

**Der Zwei-Fenster-Test misst `updatedAt` in der Cloud, nicht die Anzeige.** Steigt der
Zeitstempel weiter, obwohl niemand etwas tut, schreiben sich die Geräte gegenseitig hoch
(TROUBLESHOOTING 34/44). Das ist billiger und aussagekräftiger als jede DOM-Beobachtung.

**`fromCache` ist kein Beweis** — siehe TROUBLESHOOTING 45.

## Mobile fernsteuern

`python tools/cdp.py messen` misst am echten Gerätefenster. Wischgesten sind in diesem
Projekt allerdings **nicht** automatisiert prüfbar — drei Anläufe, dokumentiert in
`docs/TESTING.md`. Dort ist die Abnahme am Gerät der einzige Beweis; sag das, statt
Sicherheit vorzutäuschen.

## Danach

Das Ergebnis in `docs/TESTING.md` festhalten: was geprüft wurde, mit welchem Ausgangs-
und Endstand. Eine Abnahme, die nicht aufgeschrieben ist, muss beim nächsten Zweifel
komplett wiederholt werden.
