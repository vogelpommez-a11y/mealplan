---
paths:
  - "firestore.rules"
  - "tools/firestore*"
  - "tools/regeln-*"
  - "worker/**"
---

# Firebase, Rules und Geheimnisse (ausgelagert aus CLAUDE.md §12)

Der Kern („Rules sind die einzige Sicherheitsgrenze“, Geheimnisse nie ausgeben) steht weiter in
`CLAUDE.md` §12. Hier die Einzelheiten. Vollständig: `docs/SECURITY.md`.

* Die App muss **auch ohne Firebase funktionieren** (Platzhalter-Config, blockiertes Netz,
  fehlgeschlagene Initialisierung → lokaler Login). `authMode = "local"` und `"cloud"` bleiben
  beide funktionsfähig.
* UI-Sperren sind **keine** Sicherheitsgrenze; DevTools umgehen sie in Sekunden. Jede neue
  Berechtigung **zuerst in den Regeln**, dann im Client.
* `allow read` ist **nicht** `allow get` — `read` umfasst `list`. Wo eine unerratbare ID
  schützt: `allow get`, `list` aus.
* `firestore.rules` im Repo ist nur **Vorlage**; verbindlich ist der Stand in der Konsole.
  Vergleich, nur lesend: `python tools/regeln-live.py` (braucht `gcloud auth login`). Ohne
  diesen Lauf bei jeder Aussage zum Live-Zustand sagen, dass er nicht geprüft ist.
* **Vor jedem Veröffentlichen** `python tools/regeln-pruefen.py` (es gibt keinen Emulator).
  **Veröffentlicht wird von Hand in der Konsole**, nie aus einem Skript.
* Die **Firebase-Web-Config in `index.html` ist kein Secret** — Web-Keys identifizieren das
  Projekt, sie autorisieren nichts. Nie als Leck behandeln.
* **Geheimnisse** gibt es genau zwei: `OPENAI_API_KEY` in `.env` und den GCP-Service-Account-
  Schlüssel des Cloudflare Workers (nur in den Cloudflare-Secrets). **Nie ausgeben**, **nie in
  einen Prüfstand oder ein Skript kopieren** (Skripte lesen aus der Umgebung). Stand ein
  Schlüssel einmal irgendwo, hilft nur **Rotation**.
