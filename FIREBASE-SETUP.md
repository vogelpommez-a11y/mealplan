# Cloud-Anmeldung einrichten (Firebase)

Der Code ist fertig eingebaut. Solange unten in `index.html` noch die Platzhalter
(`DEIN_API_KEY` …) stehen, läuft die App automatisch im **alten lokalen Login** weiter –
es geht also nichts kaputt. Sobald du die echte Config einträgst, wird der Cloud-Login aktiv.

---

## 1. Firebase-Projekt anlegen (kostenlos)

1. Gehe zu <https://console.firebase.google.com/> und melde dich mit deinem Google-Konto an.
2. **Projekt hinzufügen** → Name z. B. `paddys-mealplan` → Google Analytics kannst du **aus**lassen → **Projekt erstellen**.

## 2. Web-App registrieren + Config holen

1. In der Projekt-Übersicht auf das **Web-Symbol `</>`** klicken.
2. App-Spitzname z. B. `mealplan-web` → **App registrieren** (Firebase Hosting NICHT ankreuzen).
3. Firebase zeigt dir jetzt das `firebaseConfig`-Objekt. Kopiere die Werte.

## 3. Werte in `index.html` eintragen

In `index.html` den Block `firebaseConfig` (im `<script type="module">`, ganz oben markiert
mit `▼▼▼`) ausfüllen:

```js
const firebaseConfig = {
  apiKey: "AIza…",                       // dein echter Wert
  authDomain: "paddys-mealplan.firebaseapp.com",
  projectId: "paddys-mealplan",
  appId: "1:1234…:web:abcd…"
};
```

> Diese Schlüssel dürfen öffentlich im Code stehen – das ist bei Firebase Web-Apps normal
> und kein Sicherheitsrisiko (der Schutz kommt über die Authorized Domains + Security Rules).

## 4. Anmelde-Methoden aktivieren

Firebase-Konsole → **Authentication** → **Get started** → Reiter **Sign-in method**:

- **E-Mail/Passwort**: aktivieren → speichern. (Die Bestätigungsmail verschickt Firebase automatisch.)
- **Google**: aktivieren → Support-E-Mail wählen → speichern.

## 5. Deine Domain freigeben (wichtig!)

Authentication → **Settings** → **Authorized domains** → **Add domain**:

- `vogelpommez-a11y.github.io`  (deine GitHub-Pages-Adresse)
- `localhost` ist schon drin (für lokale Tests)

Ohne diesen Schritt schlägt der Google-Login mit `auth/unauthorized-domain` fehl.

## 6. Cloud-Datenbank (Firestore) aktivieren – für die Synchronisierung

Damit Plan + Rezepte geräteübergreifend synchronisieren:

1. Firebase-Konsole → **Firestore Database** → **Datenbank erstellen**.
2. Standort z. B. `eur3 (europe-west)` wählen → **im Produktionsmodus starten** → Fertig.
3. Reiter **Regeln (Rules)** öffnen, den kompletten Inhalt von **`firestore.rules`** (liegt im
   Projektordner) einfügen → **Veröffentlichen**.

   Die Regeln stehen bewusst als Datei im Repo, damit nachvollziehbar ist, was gelten soll.
   Wirksam sind aber immer nur die Regeln, die in der Konsole **veröffentlicht** wurden –
   nach jeder Änderung an der Datei also erneut einfügen und veröffentlichen.

   Kurzfassung:

   > `users/{uid}`: jeder liest/schreibt nur sein **eigenes** Konto-Dokument.
   > `shared/{id}`: nur **`get`** (Dokument per ID), ausdrücklich **kein `list`**. Ändern verboten,
   > Löschen nur durch den Urheber.

   ⚠️ **Falls du eine ältere Fassung mit `allow read: if request.auth != null;` unter
   `shared/{id}` veröffentlicht hast: bitte dringend ersetzen.** In Firestore umfasst `read`
   sowohl `get` als auch `list` – damit konnte **jede angemeldete Person sämtliche geteilten
   Wochenpläne samt Namen auflisten**, ganz ohne Link. Das widersprach der Datenschutz&shy;erklärung.

So funktioniert die Sync dann automatisch:
- Nach dem Login werden deine Cloud-Daten geladen und mit den lokalen zusammengeführt (Rezepte gehen nie verloren).
- Jede Änderung wird ~1 Sek. später in die Cloud geschrieben.
- Änderungen auf einem anderen, gleichzeitig eingeloggten Gerät erscheinen **live** (Meldung „Von anderem Gerät aktualisiert").

## 7. Datenschutz-Einstellungen prüfen

Firebase-Konsole → **Projekteinstellungen** (Zahnrad oben links) → Bereich **Datenschutz**.
Direktlink: `https://console.firebase.google.com/project/paddys-mealplan/settings/general`

### 7a. Freigabe der „Firebase-Dienstdaten" abschalten

Dort steht eine Option sinngemäß:

> „Google darf meine Firebase-Dienstdaten verwenden, um … die **Nicht-Firebase-Dienste**
> von Google zu verbessern."

**Häkchen entfernen.** Grund: Die Datenschutzerklärung der App sagt zu, dass Google die Daten
*in unserem Auftrag* verarbeitet (Auftragsverarbeitung). Diese Option erlaubt ausdrücklich eine
Nutzung für **Googles eigene Zwecke** und steht dieser Zusage entgegen.

> Zur Einordnung: Betroffen sind nur **Dienstdaten** – Metadaten darüber, wie *du* das Projekt
> nutzt. Die Daten der App-Nutzer (Wochenplan, Meals, Gewicht) sind **Kundendaten** und
> ausdrücklich ausgenommen. Das Abschalten kostet keine Funktion.

Nach dem Klick die Seite **neu laden** und nachsehen, ob das Häkchen leer geblieben ist – das
ist der einzige verlässliche Beleg dafür, dass gespeichert wurde.

### 7b. Datenschutzbeauftragter

Auf derselben Seite lässt sich ein **Datenschutzbeauftragter (DSB)** eintragen. Für den
Betrieb als Privatperson ist das **nicht erforderlich** – das Feld bleibt leer.

Art. 37 DSGVO verlangt einen DSB nur, wenn man eine Behörde ist, die Kerntätigkeit in
umfangreicher systematischer Überwachung besteht, oder **umfangreich** besondere
Datenkategorien (Art. 9) verarbeitet werden. Erwägungsgrund 91 der DSGVO nimmt einzelne
Personen von „umfangreich" ausdrücklich aus.

⚠️ **Neu bewerten**, sobald die App kommerzialisiert wird oder die Nutzerzahl deutlich
wächst. Das gilt besonders, weil ungeklärt ist, ob der Gewichtsverlauf ein Gesundheitsdatum
nach Art. 9 DSGVO ist.

### 7c. Auftragsverarbeitungs-Addendum (DPA)

§5 der Datenschutzerklärung stützt sich darauf, dass Google Auftragsverarbeiter ist. Einen
eigenen Menüpunkt zum Annehmen eines DPA gibt es in der Konsole **nicht** (mehr) – Google hat
den *Cloud Data Processing Addendum* offenbar fest in die Nutzungsbedingungen integriert,
sodass er automatisch gilt.

Bestätigt ist das hier nicht. Wer es belastbar braucht, liest im Original nach:
<https://cloud.google.com/terms/data-processing-addendum>

> Dieser Abschnitt ist eine Einrichtungshilfe, **keine Rechtsberatung**. Google baut diese
> Menüs regelmäßig um – Bezeichnungen und Pfade können abweichen.

## 8. Testen & veröffentlichen

1. Lokal öffnen und mit E-Mail registrieren → du bekommst die Bestätigungsmail → Link klicken → einloggen.
2. Passt alles: committen und pushen (`git push origin main`), GitHub Pages baut neu.

---

## Optional: „Mit Apple anmelden" später aktivieren

Der Apple-Button ist im Code schon vorhanden, aber ausgeschaltet. Voraussetzung ist ein
**Apple-Developer-Account (99 €/Jahr)**.

1. Apple-Provider in Firebase (Authentication → Sign-in method → **Apple**) einrichten
   (Service ID, Key etc. laut Firebase-Anleitung).
2. In `index.html` die Zeile `const APPLE_ENABLED = false;` auf `true` setzen.

---

## Gut zu wissen

- **Im Claude-Artifact** funktioniert der Cloud-Login **nicht** (die CSP blockiert externe
  Requests) – dort erscheint automatisch der lokale Login. Der Cloud-Login läuft nur auf der
  echten Website (GitHub Pages) und lokal.
- Rezepte/Wochenplan liegen lokal (localStorage) **und** – sobald du Firestore wie in Schritt 6
  einrichtest – in der Cloud, sodass sie auf jedem Gerät erscheinen. Ohne eingerichtetes Firestore
  läuft die App trotzdem normal (nur eben ohne geräteübergreifende Sync).
