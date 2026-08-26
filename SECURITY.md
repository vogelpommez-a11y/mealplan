# Eine Sicherheitslücke melden

Danke, dass du dir die Mühe machst. Meldungen sind ausdrücklich willkommen.

## So bitte

**Nicht** über ein öffentliches GitHub-Issue und nicht über einen Pull Request — beides
wäre für alle sichtbar, bevor die Lücke geschlossen ist.

Stattdessen:

1. **Über GitHub**, wenn du dort ein Konto hast: Reiter *Security* → *Report a
   vulnerability* (Private Vulnerability Reporting). Das ist der schnellste Weg.
2. **Per E-Mail** an die im [Impressum](https://www.paddysmealplan.de) genannte Adresse.
   Betreff bitte mit `[Security]` beginnen.

Hilfreich in der Meldung: was passiert, wie man es nachstellt, und was jemand damit
anrichten könnte. Ein Screenshot oder eine kurze Abfolge von Schritten reicht völlig —
ein fertiger Exploit ist nicht nötig und nicht erwünscht.

## Was du erwarten kannst

Dies ist ein Ein-Personen-Projekt, kein Unternehmen mit Bereitschaftsdienst. Trotzdem:

| | |
|---|---|
| Erste Rückmeldung | innerhalb von **7 Tagen** |
| Einschätzung, ob und wie schwer | innerhalb von **14 Tagen** |
| Behebung schwerer Lücken | so schnell wie möglich, in der Regel Tage, nicht Wochen |

Ich melde mich zurück, auch wenn ich zu dem Schluss komme, dass es keine Lücke ist —
und sage dann, warum. Wenn du möchtest, wirst du nach der Behebung namentlich genannt.

Ein Bug-Bounty-Programm gibt es nicht, es fließt also kein Geld.

## Was in Ordnung ist

- Die eigene Instanz untersuchen: eigenes Konto, eigene Daten, eigene geteilte Links.
- Die Firestore-Regeln gegen ein **eigenes** Testkonto prüfen.
- Den ausgelieferten Code lesen. Er liegt offen, genau dafür.

## Was nicht

- Auf **fremde Konten** oder fremde Daten zugreifen. Auch nicht „nur zum Beweis".
- Lasttests, Denial-of-Service, automatisiertes Massen-Anlegen von Konten.
- Social Engineering gegen mich oder gegen Nutzende.
- Eine gefundene Lücke veröffentlichen, bevor sie geschlossen ist.

## Was ausdrücklich **keine** Lücke ist

**Der Firebase-Web-Schlüssel in `index.html`** (`apiKey: "AIzaSy…"`). Firebase-Web-Keys
sind öffentlich by design — sie identifizieren das Projekt, sie autorisieren nichts. Der
Schutz kommt aus Authorized Domains und den Firestore Security Rules. Meldungen dazu sind
gut gemeint, aber schon oft eingegangen.

Gleiches gilt für:

- **`firestore.rules` im Repo.** Die Regeln liegen offen, weil eine Regel, die nur
  geheim funktioniert, keine Regel ist. Zeig mir lieber, wo sie **nicht** greift.
- **Name und Anschrift im Impressum.** Nach § 5 DDG vorgeschrieben.
- Fehlende Header, die GitHub Pages gar nicht setzen kann — als Hinweis trotzdem
  willkommen, aber bitte als solcher gekennzeichnet.

## Umfang

In Reichweite: `www.paddysmealplan.de`, dieses Repository und die dort ausgelieferte App.

Nicht in Reichweite: die Infrastruktur von Google/Firebase, GitHub und Cloudflare selbst.
Lücken dort meldest du besser direkt bei diesen Anbietern — die haben dafür eigene
Programme und zahlen sogar dafür.
