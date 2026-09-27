# Was nur ein Mensch prüfen kann

Diese Datei sammelt die Abnahmen, die kein Skript übernimmt — und sagt bei jedem Punkt
dazu, **warum** nicht. Das ist kein Beiwerk: Solange nicht dasteht, warum ein Punkt hier
liegt, wandert er beim nächsten Aufräumen in ein Werkzeug, das ihn nur scheinbar prüft.

> `tools/abnahme-mobil.py` fährt 108 Stationen über drei Gerätebreiten und beide Themes.
> Es misst Größen, Kontraste und Trefferflächen — und das sehr genau. Was es **nicht**
> kann: eine Wischgeste, den echten Safari, einen zweiten Menschen und ein Netz, das
> mitten im Vorgang abbricht. Genau das steht hier.

Stand: 22.09.2026.

**Abgenommen am 27.09.2026 von Paddy:** Abschnitt 1 (außer 1.9) und Abschnitt 2
vollständig, ohne Befund. Offen bleibt nur 1.9.

---

## 1. Abnahme am echten iPhone

**Warum kein Skript:** Chrome mit Geräte-Emulation zeichnet die richtige Größe, aber er
ist nicht WebKit. Wischgesten, das Gummiband beim Überscrollen, die Adressleiste, die
beim Scrollen wächst und schrumpft, die Tastatur, die den Viewport zusammenschiebt, und
`100svh` — das alles verhält sich auf einem echten iPhone anders. Dazu kommt der
Autofokus der Kamera, den nur ein natives Gerät hat.

Vorbereitung: Die App im **Safari** öffnen (`https://www.paddysmealplan.de`), nicht in
Chrome für iOS und nicht im In-App-Browser von Instagram — der ist ein eigener Fall,
siehe Punkt 1.9.

### 1.1 Erster Eindruck, ohne Konto
- [x] Die App startet und zeigt sofort Inhalt (kein weißer Schirm, keine Endlos-Drehung).
- [x] Der **Footer mit Impressum und Datenschutz ist ohne Anmeldung sichtbar**.
- [x] Flugmodus an, App neu laden: Sie startet trotzdem und ist bedienbar.

### 1.2 Das Onboarding
- [x] Alle Eingabefelder lassen sich tippen, **ohne dass Safari hineinzoomt**
      (das passiert, sobald ein Feld kleiner als 16 px Schrift hat).
- [x] Die Tastatur verdeckt nie das Feld, in dem man gerade schreibt.
- [x] Der Weiter-Knopf bleibt erreichbar, wenn die Tastatur offen ist.
- [x] Am Ende erscheint **ein** Hinweis auf den Auto-Planer („Die ganze Woche auf einmal").
      Er lässt sich mit „Später" schließen und kommt danach nicht wieder.

### 1.3 Der Wochenplan — hier liegen die Gesten
- [x] Seitlich wischen wechselt den Tag, und der Streifen oben rastet sauber ein.
- [x] Beim Wischen scrollt die Seite **nicht** gleichzeitig senkrecht.
- [x] Ein Meal lässt sich mit dem Finger umsortieren (langes Drücken, dann ziehen).
- [x] Das Gummiband am oberen Rand reißt das Layout nicht auf.
- [x] Ein Meal antippen öffnet das Blatt; **Wischen nach unten schließt es wieder**.
- [x] Die untere Reiterleiste bleibt über der Home-Leiste des iPhone stehen
      (nichts klebt hinter dem Balken).

### 1.4 Ladezustand der Bilder *(neu am 22.09.2026)*
- [x] Im Meals-Reiter nach unten scrollen: Wo ein Foto noch fehlt, **schimmert** die
      Fläche kurz und wird dann vom Bild abgelöst.
- [x] Nichts schimmert dauerhaft weiter, nachdem das Bild da ist.
- [x] In den iOS-Einstellungen *Bedienungshilfen → Bewegung reduzieren* einschalten:
      Der Schimmer hört auf, die getönte Fläche bleibt.

### 1.5 Hinweise, die auf Touch ankommen *(neu am 22.09.2026)*
- [x] Einkaufsliste öffnen, eine Zutat mit „×2" antippen: Es erscheint eine kleine Blase
      („in 2 Meals der Woche"). Nochmal tippen schließt sie.
- [x] Irgendwo daneben tippen schließt sie ebenfalls.

### 1.6 Kamera und Barcode
- [x] Die Berechtigungsabfrage erscheint **einmal** und mit verständlichem Text.
- [x] Das Kamerabild steht richtig herum — auch, wenn man das Gerät quer hält.
- [x] Ein Barcode wird erkannt; wenn nicht, gibt es einen Weg zurück ohne Sackgasse.
- [x] Abbrechen gibt die Kamera wieder frei (die Leuchte am Gerät geht aus).

### 1.7 Anmelden
- [x] Anmeldung mit Google öffnet das Fenster und kehrt **in die App** zurück.
- [x] Anmeldung per E-Mail: Die Bestätigungsmail kommt an und der Link führt zurück.
- [x] Bei der Registrierung steht der Hinweis auf **mindestens 16 Jahre**.

### 1.8 Zur Startseite hinzufügen (PWA)
- [x] Über *Teilen → Zum Home-Bildschirm* installieren.
- [x] Das Symbol sieht richtig aus, der Name ist nicht abgeschnitten.
- [x] Aus dem Home-Bildschirm gestartet läuft die App **ohne Adressleiste**.
- [x] Auch dort: Flugmodus an, App startet trotzdem.

### 1.9 Der In-App-Browser *(bekannter offener Punkt)*
Einen Teilen-Link in Instagram oder WhatsApp an sich selbst schicken und **dort** öffnen.
- [ ] Die App lädt.
- [ ] Wenn die Anmeldung mit Google dort scheitert: Erscheint ein verständlicher Hinweis,
      oder eine Sackgasse? (Notiert als Befund vom 26.07.2026 — hier bitte den
      tatsächlichen Stand eintragen.)

**Stand 27.09.2026: 1.9 ist noch nicht getestet** und bleibt offen.

---

## 2. Abnahme zu zweit (Gruppe)

**Warum kein Skript:** Zwei echte Konten, die gleichzeitig schreiben, lassen sich headless
nicht glaubwürdig nachstellen. Die Prüfstände decken die Regeln und die Datenwege ab —
was sie nicht messen können, ist das Zusammenspiel in Echtzeit und das Gefühl dabei.

Vorbereitung: **Zwei Geräte, zwei echte Konten.** Person A ist Inhaber, Person B tritt
bei. Beide mit Netz, nebeneinander.

### 2.1 Gründen und beitreten
- [x] A gründet eine Gruppe und erzeugt einen Einladungslink.
- [x] B öffnet den Link und tritt bei.
- [x] A sieht B in der Mitgliederliste, **mit Namen und Bild**.
- [x] Bs eigene Meals sind in der Gruppe angekommen — **ohne Dubletten**.

### 2.2 Gleichzeitig planen — der eigentliche Punkt
- [x] Beide legen **im selben Moment** ein Meal auf denselben Tag.
      Danach stehen **beide** Meals da; keins hat das andere überschrieben.
- [x] A ändert ein Meal, B sieht die Änderung binnen weniger Sekunden.
- [x] B geht offline (Flugmodus), plant etwas, kommt zurück:
      Die Änderung erscheint bei A, und nichts ging verloren.

### 2.3 Rollen
- [x] A setzt B auf „Nur ansehen": Bei B verschwinden die Bearbeiten-Knöpfe.
- [x] B versucht trotzdem etwas zu ändern (z. B. über einen offenen Dialog):
      Es passiert nichts Stilles — entweder geht es nicht, oder es gibt eine Meldung.
- [x] A setzt B wieder auf „Mitplanen": B kann wieder planen.

### 2.4 Austritt — hier hängt der Datenschutz dran *(neu am 22.09.2026)*
- [x] B verlässt die Gruppe. **Bs Meals bleiben bei A im Plan.**
- [x] Bei A steht an diesen Meals **kein Name mehr** — auch kein „B".
- [x] B hat seine Meals mitgenommen und sieht sie in seinem eigenen Konto,
      wieder **ohne Dubletten**.
- [x] A entfernt danach ein weiteres Mitglied: gleiches Bild.

> Fachlich dahinter: Beim Austritt wird `by` in den Gruppen-Meals geleert. Sichtbar ist
> davon nur, dass kein Name mehr dasteht — das ist Absicht. Wer den Nachweis im Datenbestand
> sehen will, findet ihn in `tools/pruefstand-gruppe-anonymisieren.py`.

### 2.5 Auflösen
- [x] A löst die Gruppe auf. Beide landen wieder in ihrem eigenen Plan.
- [x] Bei beiden ist der Bestand vollständig und **nicht doppelt**.
- [x] A kann danach sein Konto löschen, ohne dass eine Gruppe ohne Inhaber zurückbleibt.

---

## 3. Wenn etwas auffällt

Nicht hier abhaken und weitergehen: Eintragen in `docs/TROUBLESHOOTING.md` mit Datum und
dem, was tatsächlich zu sehen war. Ein Haken, der gesetzt wurde, „weil es wohl passt",
ist schlechter als kein Haken — er behauptet eine Prüfung, die nicht stattgefunden hat.
