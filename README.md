# Paddy's Mealplan

**Plan it. Cook it. Lift it.**

Ein deutschsprachiger Wochen-Essensplaner für Menschen, die Fitness und Ernährung
zusammendenken. Die App schaut nach vorne — *was werde ich essen?* — statt zurück.
Sie ist ausdrücklich **kein Kalorien-Tracker**.

**→ [www.paddysmealplan.de](https://www.paddysmealplan.de)**

## Was hier liegt

Die App wird **ohne Build-Prozess** ausgeliefert: Was im Repo steht, ist unmittelbar
das, was im Browser läuft. Sie verteilt sich auf wenige klassische Dateien, die in
Dokumentreihenfolge geladen werden — keine Module, kein Bundler.

| Pfad | Inhalt |
|---|---|
| `index.html` | Markup, Firebase-Anbindung und der App-Kern |
| `css/` | Design-Tokens und Styles |
| `data/` | Rezeptkatalog, Zutaten, Bilder, Icons, Rechtstexte |
| `lib/` | gemeinsame Helfer, PDF-Erzeugung, Barcode |
| `firestore.rules` | Vorlage der Datenbank-Zugriffsregeln (wirksam ist der in der Firebase-Konsole veröffentlichte Stand) |
| `sw.js` | Service Worker für Offline-Betrieb |
| `worker/og.js` | Cloudflare Worker für die Linkvorschau geteilter Meals |
| `vendor/` | Firebase-SDK und ZXing, bewusst lokal statt vom CDN |
| `tools/` | Python-Hilfsskripte und Prüfstände |
| `docs/` | Produktdefinition, Architektur, Tests, bekannte Fallen |
| `.claude/` | Agenten, Hooks und Befehle für die Arbeit mit Claude Code |

## Mitmachen

Dies ist ein persönliches Projekt und nimmt derzeit **keine Beiträge von außen** an.
Der Code liegt öffentlich, damit nachvollziehbar ist, was die App tut — er ist nicht zur
Weiterverwendung freigegeben. Siehe [LICENSE](LICENSE).

## Eine Sicherheitslücke melden

Bitte **nicht** über ein öffentliches Issue. Der Weg steht in [SECURITY.md](SECURITY.md).

## Rechtliches

Impressum und Datenschutzerklärung stehen in der App selbst und sind ohne Anmeldung
erreichbar. Die mitgelieferten Fotos stehen unter CC0 bzw. Public Domain; die Herkunft
jedes Bildes ist im Impressum unter „Bildnachweise" belegt.
