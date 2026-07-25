---
description: Führt alle vier Push-Checks (anwalt, secure, ux-reviewer, KVP) auf Haiku aus und wechselt danach zurück zu Sonnet
---

Wechsle zum Haiku-Modell für die folgenden Prüfungen.

Führe danach nacheinander die vier Push-Checks aus den definierten Regeln aus:
1. anwalt – rechtliche Prüfung
2. secure – Sicherheitsprüfung
3. ux-reviewer – Übersichtlichkeits-/UX-Prüfung (nur bei geänderten UI-Dateien: Komponenten, Screens, HTML/CSS)
4. KVP – kontinuierlicher Verbesserungsprozess

Prüfe dabei die aktuell geänderten Dateien im Vergleich zum letzten Push (`git diff --name-only @{u}..` bzw. falls kein Upstream gesetzt ist, die letzten Commits).

Gib die Ergebnisse aller vier Checks gebündelt und klar getrennt aus. Markiere kritische Funde mit 🔴, unkritische Hinweise mit 🟡. Falls ein Check nichts findet, schreibe "Keine kritischen Punkte gefunden."

Fasse am Ende zusammen, ob mindestens ein 🔴-Fund vorliegt.

Wechsle danach wieder zurück zum Sonnet-Modell, bevor du auf die nächste Nachricht wartest.
