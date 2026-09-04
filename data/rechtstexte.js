/* rechtstexte.js - Paddy's Mealplan
 *
 * Impressum und Datenschutzerklaerung als Markup - unveraendert aus index.html.
 *
 * Das sind RECHTSTEXTE, kein gewoehnlicher UI-Text: Sie enthalten konkrete
 * technische Zusagen. Eine Aenderung am Verhalten der App kann sie inhaltlich
 * falsch machen - jede Aenderung hier braucht den Agenten `anwalt`.
 *
 * Das Impressum ist zweigeteilt, weil dort der Bildnachweis eingesetzt wird, den
 * creditsHtml() im Kern aus PHOTO_CREDITS erzeugt. Der Text selbst ist dadurch
 * reine Zeichenkette geblieben - kein Template mit Logik.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  const IMPRESSUM_HTML_1 = `
      <h4>Angaben gemäß § 5 DDG</h4>
      <p>Patrick Fleischmann<br>Bauvereinstraße 2<br>97526 Sennfeld</p>
      <h4>Kontakt</h4>
      <p>E-Mail: fleischmann-patrick@gmx.de</p>
      <h4>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h4>
      <p>Patrick Fleischmann (Anschrift wie oben)</p>
      <h4>Haftung für Inhalte</h4>
      <p>Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt.</p>
      <h4>Haftung für Links</h4>
      <p>Unser Angebot enthält ggf. Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Für diese fremden Inhalte kann keine Gewähr übernommen werden. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber verantwortlich.</p>
      <h4>Urheberrecht</h4>
      <p>Die durch den Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. Beiträge Dritter sind als solche gekennzeichnet.</p>
      <h4>Bildnachweise</h4>
      <p>Die mitgelieferten Gerichtsfotos stehen unter <strong>CC0 1.0</strong> bzw. <strong>Public Domain Mark 1.0</strong>
         und dürfen ohne Namensnennung kommerziell genutzt werden. Die Nennung erfolgt freiwillig als Herkunftsnachweis.
         Die Bilder wurden mittig zugeschnitten, sonst nicht verändert. Von Nutzenden selbst hochgeladene Fotos
         sind hier nicht erfasst – dafür ist die jeweilige Person verantwortlich.</p>
      `;

  const IMPRESSUM_HTML_2 = `
      <p>Die Gerichtsfotos im <strong>Rezeptbuch</strong> sind <strong>KI-generiert</strong> (OpenAI, Modell <code>gpt-image-2</code>).
         Die kommerzielle Nutzung ist nach den <a href="https://openai.com/policies/terms-of-use" target="_blank" rel="noopener noreferrer">OpenAI-Nutzungsbedingungen</a> erlaubt.
         Sie zeigen keine realen Personen, Orte oder Ereignisse; zu jedem Bild ist festgehalten, mit welcher Beschreibung und wann es entstanden ist.</p>
      <h4>Nährwertdaten</h4>
      <p>Die Nährwerte der Rezepte im <strong>Rezeptbuch</strong> – und damit auch der Meals, die zu Beginn passend zu deiner Auswahl in deine Sammlung gelegt werden – sind aus den Zutatenmengen anhand allgemeiner Nährwerttabellen <strong>berechnet</strong>. Es sind <strong>Richtwerte</strong>: Sorte, Reifegrad, Zubereitung und Garverluste verändern die tatsächlichen Werte. Sie sind nicht laborgeprüft und ersetzen keine ernährungsmedizinische Beratung.</p>
      <p>Die Produktdaten beim Barcode-Scan stammen von <strong>Open Food Facts</strong>
         (<a href="https://world.openfoodfacts.org" target="_blank" rel="noopener noreferrer">world.openfoodfacts.org</a>),
         einer offenen, gemeinschaftlich gepflegten Datenbank. Die Datenbank als Ganzes steht unter
         der <a href="https://opendatacommons.org/licenses/odbl/1.0/" target="_blank" rel="noopener noreferrer">Open Database License (ODbL) 1.0</a>,
         die einzelnen Dateninhalte – genau das, was diese App per Barcode abruft – zusätzlich unter der
         <a href="https://opendatacommons.org/licenses/dbcl/1.0/" target="_blank" rel="noopener noreferrer">Database Contents License (DbCL) 1.0</a>.
         Einzelne Angaben können unvollständig oder fehlerhaft sein – bitte vor dem Speichern kurz prüfen.</p>`;

  const DATENSCHUTZ_HTML = `
      <h4>1. Verantwortlicher</h4>
      <p>Patrick Fleischmann, Bauvereinstraße 2, 97526 Sennfeld<br>E-Mail: fleischmann-patrick@gmx.de</p>
      <h4>2. Hosting der Website (GitHub Pages)</h4>
      <p>Diese Website wird bei GitHub Pages gehostet, einem Dienst der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Beim Aufruf der Seite verarbeitet GitHub technisch notwendige Zugriffsdaten (z. B. deine IP-Adresse), um die Seite auszuliefern und deren Sicherheit zu gewährleisten. Rechtsgrundlage ist unser berechtigtes Interesse an einer sicheren und effizienten Bereitstellung (Art. 6 Abs. 1 lit. f DSGVO). Dabei kann eine Übermittlung in die USA erfolgen. Weitere Infos: <a href="https://docs.github.com/de/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener">GitHub Privacy Statement</a>.</p>
      <h4>3. Welche Daten wir verarbeiten</h4>
      <p><strong>Zwei Betriebsarten – und nur eine davon verarbeitet Daten bei uns.</strong> Du kannst die App <strong>ohne Konto</strong> nutzen: Dann bleiben deine Plan- und Profildaten ausschließlich auf deinem Gerät (Browser-Speicher), sie werden <strong>weder an uns noch an Firebase übertragen</strong>, und wir haben keinen Zugriff darauf. Ohne Konto entsteht dabei auch keine Verbindung zu Google: Die Software für die Cloud-Funktionen wird seit August 2026 zusammen mit der Seite ausgeliefert und nicht mehr von Google-Servern nachgeladen (Ziffer 5). Wir fragen dabei nur einen frei wählbaren <strong>Namen</strong> ab; eine E-Mail-Adresse ist optional und verlässt das Gerät ebenfalls nicht. Der folgende Abschnitt beschreibt die zweite Betriebsart: die Nutzung <strong>mit Konto</strong> (Cloud-Synchronisierung), für die du dich aktiv entscheidest. Löschst du die Websitedaten deines Browsers, sind lokal gespeicherte Angaben unwiederbringlich weg – im Betrieb ohne Konto haben wir keine Kopie davon.</p>
      <p>Bei der Registrierung: <strong>Name und E-Mail-Adresse</strong>. Bei Nutzung der App: die von dir angelegten <strong>Wochenpläne, Meals/Rezepte und ggf. Fotos</strong> sowie ein optionales <strong>Profilbild</strong> (als Kreis-Avatar zugeschnitten, in deinem Nutzerkonto gespeichert, nicht Teil von Teilen-Links) sowie – im Rahmen der Einführungsfragen zu Beginn, die zur Nutzung der App erforderlich sind – <strong>Geschlecht, Alter, Größe, Gewicht, Alltagsbewegung und Ziel</strong> sowie optional deine <strong>Trainingstage</strong> (Wochentag, Intensität und Dauer) und deinen <strong>Körperfettanteil</strong> (als grobe Stufe; Details zu beidem siehe Ziffer 3a) sowie – ebenfalls optional – deine <strong>Auswahl, welche Meals dir vorgeschlagen werden sollen</strong> (vegetarisch, vegan oder ohne Einschränkung; dazu wahlweise glutenfrei und/oder laktosefrei). Erstellst du Teilen-Links, merkt sich dein Konto zusätzlich deren <strong>Kennungen</strong> (keine Klardaten, siehe Ziffer 8), damit sie beim Löschen deines Kontos zugeordnet und mitentfernt werden können. Nutzt du „Gemeinsam planen", speichert dein Konto außerdem die <strong>Kennung deiner Gruppe</strong> sowie die Kennungen der von dir erstellten <strong>Einladungslinks</strong> – aus demselben Grund (siehe Ziffer 8a); an einem in einer Gruppe angelegten Meal wird zusätzlich deine <strong>Nutzerkennung</strong> vermerkt, damit sichtbar ist, wer es angelegt hat. Weist du ein geplantes Gericht nur einem Teil der Gruppe zu (statt „für alle"), wird für dieses Gericht zusätzlich vermerkt, welche Mitglieder es per <strong>Nutzerkennung</strong> essen – sichtbar für die ganze Gruppe als kleines Farb-Badge auf der Meal-Karte. Stellst du in der Einkaufsliste eine <strong>Personenanzahl</strong> ein, wird auch diese gespeichert. Markierst du Meals als <strong>Favorit</strong>, wird diese Auswahl ebenfalls in deinem Konto gespeichert – nur für dich, auch in einer Gruppe. Nutzt du den <strong>automatischen Wochenplaner</strong>, merkt sich dein Konto zu den eingeplanten Meals die <strong>Kalenderwoche</strong>, in der sie zuletzt vorgeschlagen wurden – damit du nicht jede Woche dieselben Gerichte bekommst. Diese Angabe gilt nur für dich, auch in einer Gruppe, und wird nach einigen Wochen automatisch wieder entfernt. Damit dein <strong>Wochenarchiv</strong> im Reiter „Fortschritt“ Auswertungen über die zwei im Plan gehaltenen Wochen hinaus ermöglicht – etwa deine Serie, die Zahl der Tage im Ziel oder den Jahresüberblick –, bewahrt dein Konto zu jeder vergangenen Kalenderwoche vier <strong>Kennzahlen</strong> auf: die Anzahl geplanter Tage, die Zahl der Tage innerhalb deines Zielkorridors, das damals gültige Tagesziel und die Angabe, <em>welche</em> Wochentage beplant waren. Der Wochenplan selbst wird dabei gelöscht – gespeichert bleiben nur diese Zahlen, keine Gerichte und keine Fotos. Aufbewahrt werden das <strong>laufende und die beiden vorangegangenen Kalenderjahre</strong>, Älteres entfällt automatisch. Übernimmst du ein Rezept aus dem mitgelieferten <strong>Rezeptbuch</strong>, entsteht eine Kopie in deiner Sammlung; an ihr wird zusätzlich die <strong>Kennung des Ursprungsrezepts</strong> vermerkt, damit sich eine später korrigierte Fassung zuordnen lässt. Damit du nicht mit einer leeren Sammlung beginnst, legen wir am Ende der Einführungsfragen <strong>fünf solcher Kopien</strong> für dich an – ausgewählt passend zu deiner Angabe, welche Meals dir vorgeschlagen werden sollen. Sie gehören dann dir und lassen sich wie jedes andere Meal bearbeiten oder löschen. Plant der <strong>automatische Wochenplaner</strong> ein Rezept aus dem Rezeptbuch ein, entsteht dabei <strong>keine</strong> Kopie: Dein Plan verweist dann unmittelbar auf das mitgelieferte Gericht, und deine Sammlung bleibt unverändert. Kopien, die frühere Fassungen der App beim Planen angelegt haben und die du nie verändert hast, räumt die App einmalig auf (siehe Ziffer 10). Stimmst du der Speicherung deines <strong>Gewichtsverlaufs</strong> ausdrücklich zu, speichern wir je Eintrag Kalenderwoche und Gewicht sowie ein optionales <strong>Jahres-Zielgewicht</strong> (Details und Widerruf siehe Ziffer 3b). Ist für dein Konto die kostenpflichtige <strong>Pro-Stufe</strong> freigeschaltet, speichern wir dazu ein eigenes Dokument mit dem <strong>Pro-Status</strong>, der <strong>Herkunft der Freischaltung</strong> (manuell, Apple oder Google) und gegebenenfalls einem <strong>Ablaufdatum</strong>. Dieses Dokument kann die App nur lesen, nicht ändern – gesetzt wird es ausschließlich von uns bzw. künftig vom Bezahlvorgang des jeweiligen App-Stores. Es wird mit deinem Konto gelöscht (Ziffer 10). Eine Bezahlfunktion gibt es derzeit nicht. Diese Daten speichern wir, damit du dich anmelden und deine Planung geräteübergreifend nutzen kannst.</p>
      <h4>3a. Ziel-Berechnung (Einführungsfragen)</h4>
      <p>Zur Nutzung der App gibst du bei den Einführungsfragen zu Beginn <strong>Geschlecht, Alter, Größe und Gewicht</strong> sowie deine Alltagsbewegung und dein Ziel an – ohne diese Angaben lässt sich kein Kalorien- und Makroziel berechnen und die App steht dir nicht zur Verfügung. Optional legst du zusätzlich deine <strong>Trainingstage</strong> fest – also an welchen Wochentagen du trainierst, mit welcher Intensität und wie lange; diese Angabe kannst du auch weglassen. Ebenfalls optional wählst du eine grobe Stufe für deinen <strong>Körperfettanteil</strong> – gibst du sie an, berechnet die App deinen Grundumsatz nach der Katch-McArdle-Formel über die fettfreie Masse statt nach Mifflin-St-Jeor; wählst du „Weiß ich nicht", bleibt es bei Mifflin-St-Jeor. Daraus berechnet die App direkt in deinem Browser deinen Tagesbedarf, deine Makronährstoffe und deinen BMI; an Trainingstagen zusätzlich den geschätzten Mehrbedarf durch die jeweilige Einheit. Übernimmst du das Ergebnis als dein Ziel, werden diese Angaben wie deine übrigen Plandaten lokal und – bei Cloud-Nutzung – in deinem Nutzerkonto (Cloud Firestore, siehe Ziffer 5) gespeichert, um sie geräteübergreifend verfügbar zu halten. Du kannst dein Ziel jederzeit über den Knopf „Ziel neu berechnen" im Wochenplan neu berechnen; die vorherigen Werte sind dann durch die neuen ersetzt. Rechtsgrundlage ist wie unter Ziffer 4 die Erfüllung des Nutzungsvertrags (Art. 6 Abs. 1 lit. b DSGVO). Diese Angaben werden <strong>nicht</strong> in Teilen-Links aufgenommen (siehe Ziffer 8).</p>
      <h4>3b. Gewichtsverlauf („Ziele &lt;Jahr&gt;")</h4>
      <p>Dein Gewichtsverlauf ist ein <strong>Gesundheitsdatum</strong> (Art. 9 DSGVO) und wird deshalb nur mit deiner ausdrücklichen, jederzeit widerrufbaren <strong>Einwilligung</strong> gespeichert (Art. 9 Abs. 2 lit. a DSGVO). Ohne diese Einwilligung zeigt dir die App unter „Ziele &lt;Jahr&gt;" lediglich einen Knopf zum Aktivieren – auch ein bei den Einführungsfragen oder beim Neuberechnen deines Ziels angegebenes Gewicht wird dann <strong>nicht</strong> automatisch als Verlauf gespeichert, sondern nur einmalig für die Berechnung deines Kalorien- und Makroziels verwendet (Ziffer 3a). Stimmst du zu, besteht ein Eintrag aus <strong>Kalenderwoche und Gewicht</strong> – taggenaue Angaben werden nicht erhoben; zusätzlich kannst du ein <strong>Zielgewicht je Kalenderjahr</strong> festlegen. Ein Eintrag entsteht dann, wenn du im Bereich „Ziele" eine Wiegung einträgst – auch nachträglich für zurückliegende Wochen –, und automatisch, wenn du bei den Einführungsfragen oder beim Neuberechnen deines Ziels dein Gewicht angibst und dieses vom zuletzt erfassten Wert abweicht. Die jeweils jüngste Wiegung aktualisiert zusätzlich das bei der Ziel-Berechnung hinterlegte Gewicht, damit dein Kalorien- und Makroziel zu deinem aktuellen Gewicht passt. Speicherung: lokal auf deinem Gerät und – bei Cloud-Nutzung – in deinem Nutzerkonto. Deine Einwilligung kannst du jederzeit über das Menü der Karte widerrufen; bereits gespeicherte Einträge bleiben dabei bestehen, es kommen nur keine neuen automatischen Einträge mehr hinzu. Einzelne Einträge kannst du jederzeit im Wiegen-Dialog löschen, den gesamten Verlauf mit deinem Konto (Ziffer 10). Diese Angaben werden <strong>nicht</strong> in Teilen-Links aufgenommen (siehe Ziffer 8).</p>
      <h4>3c. Auswahl deiner Meal-Vorschläge</h4>
      <p>In den Einführungsfragen kannst du festlegen, <strong>welche Meals dir vorgeschlagen werden sollen</strong>: ohne Einschränkung, vegetarisch oder vegan, dazu wahlweise glutenfrei und/oder laktosefrei. Das ist eine <strong>Auswahl für Vorschläge</strong> – wir erheben damit weder eine Unverträglichkeit noch eine Erkrankung oder Weltanschauung und leiten daraus nichts ab. Die Angabe ist freiwillig; ohne sie bekommst du alle Meals vorgeschlagen. Gespeichert wird sie nur, wenn du etwas anderes als „Alles" wählst – zusammen mit deinem Ziel, also lokal auf deinem Gerät und bei Cloud-Nutzung in deinem Nutzerkonto. Ändern kannst du sie jederzeit über „Ziele neu berechnen". In einer Gruppe (Ziffer 8a) wird sie <strong>nicht</strong> geteilt – kein Mitglied sieht deine Auswahl. Sie fließt auch <strong>nicht</strong> in Teilen-Links ein (Ziffer 8).</p>
      <h4>4. Zweck &amp; Rechtsgrundlage</h4>
      <p>Wir verarbeiten die Daten zur Bereitstellung deines Nutzerkontos und der Planer-Funktionen (Art. 6 Abs. 1 lit. b DSGVO – Nutzungsvertrag). Die Bestätigungs-E-Mail dient der Sicherstellung, dass die Adresse dir gehört.</p>
      <h4>5. Cloud-Dienste (Google Firebase)</h4>
      <p>Für Anmeldung und Speicherung nutzen wir <strong>Google Firebase</strong> (Firebase Authentication und Cloud Firestore) der Google Ireland Ltd., Gordon House, Barrow Street, Dublin 4, Irland. Die dafür nötige Software wird seit August 2026 zusammen mit der Seite ausgeliefert und nicht mehr von Google-Servern nachgeladen. <strong>Ohne Konto</strong> entsteht beim Aufruf dieser Seite deshalb keine Verbindung zu Google. Bist du dagegen <strong>mit einem Konto angemeldet</strong>, prüft die App bei jedem Aufruf deine Anmeldung bei Google – dabei wird deine IP-Adresse an Google übermittelt, ebenso beim Registrieren und beim Anmelden. Der Datenbank-Standort ist auf <strong>Europa</strong> eingestellt. Google verarbeitet die Daten in unserem Auftrag (Auftragsverarbeitung); eine Übermittlung in die USA kann nicht ausgeschlossen werden und stützt sich auf die EU-Standardvertragsklauseln bzw. das EU-US Data Privacy Framework. Datenschutz von Google: <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">policies.google.com/privacy</a>.</p>
      <h4>6. Anmeldung mit Google</h4>
      <p>Wenn du dich mit „Mit Google anmelden" einloggst, erhält Google die für die Anmeldung nötigen Informationen. Es gelten zusätzlich die Datenschutzbestimmungen von Google.</p>
      <h4>7. Speicherung im Browser</h4>
      <p>Zur Anmeldung und für den Offline-Betrieb speichert die App technisch notwendige Daten lokal in deinem Browser (localStorage/IndexedDB) – bei einem Cloud-Konto zählt dazu auch ein Zwischenspeicher deines Wochenplans, deiner Meals sowie, falls zutreffend, der Daten eurer gemeinsamen Gruppe (Namen, Profilbilder, gemeinsame Meals) bzw. eines von dir geöffneten Teilen-Links, damit alles ohne Internetverbindung verfügbar bleibt. Dafür ist keine Einwilligung erforderlich; ein Tracking findet nicht statt (Google Analytics ist deaktiviert).</p>
      <h4>7a. Barcode-Scan (Produktsuche)</h4>
      <p>Beim Anlegen von Zutaten sowie beim direkten Einplanen eines Fertigprodukts aus dem
         Wochenplan kannst du einen Barcode scannen. Dafür fragt die App den Zugriff
         auf die <strong>Kamera</strong> deines Geräts an und zeigt das Kamerabild live an, bis ein
         Barcode erkannt oder der Scanner geschlossen wird; alternativ kannst du ein Einzelfoto
         aufnehmen. Das <strong>Kamerabild wird weder gespeichert noch übertragen</strong> und die
         Kamera wird beim Schließen des Scanners sofort wieder freigegeben. Die Erkennung des
         Barcodes läuft <strong>vollständig lokal in deinem Browser</strong> – Bild bzw. Foto
         verlassen dein Gerät nicht. Unterstützt dein Browser die dafür nötige Technik nicht selbst (z. B.
         auf iPhones), nutzt die App die Open-Source-Bibliothek <strong>ZXing</strong>, die
         <strong>mit der App ausgeliefert</strong> wird (kein Nachladen von einem fremden Server, keine
         Übermittlung deiner IP-Adresse an Dritte dafür). Anschließend übermittelt die App die
         erkannte <strong>Barcode-Nummer</strong> (nicht das Foto) an <strong>Open Food
         Facts</strong> (Open Food Facts Association, Frankreich), um Name und Nährwerte des
         Produkts abzurufen; dabei wird ebenfalls deine IP-Adresse an diesen Dienst übermittelt
         (Art. 6 Abs. 1 lit. f DSGVO). Die Barcode-Nummer wird außerdem im angelegten Meal
         gespeichert (wie deine übrigen Plandaten, siehe Ziffer 3), damit die App ein erneut
         gescanntes Produkt wiedererkennt, statt es doppelt anzulegen. Ein so angelegtes Produkt
         räumt die App nach einiger Zeit von selbst wieder weg, sobald du es nicht mehr eingeplant
         hast (Ziffer 10). Nutzt du den
         Barcode-Scan nicht, findet keiner dieser Abrufe statt.</p>
      <h4>8. Teilen-Funktion</h4>
      <p>Wenn du einen Teilen-Link für ein einzelnes Meal erstellst, wird eine Kopie dieses Meals (inkl. eines
         eigenen Fotos, falls vorhanden, dein angezeigter Name und der Zeitpunkt) in der Cloud gespeichert. Sie ist
         ausschließlich über den Link abrufbar und nur für angemeldete Nutzer. Die Kennung im Link wird mit
         80&nbsp;Bit Zufall erzeugt und ist praktisch nicht erratbar; ein Auflisten oder Durchsuchen der geteilten
         Inhalte ist technisch unterbunden. Der Link ist damit der einzige Zugang – <strong>teile ihn nur mit
         Personen, die den Inhalt sehen dürfen</strong>, denn wer ihn hat, kann ihn öffnen. Ein Teilen-Link ist eine
         <strong>Momentaufnahme</strong>: Wer ihn öffnet, erhält eine Kopie und kann dein Meal nicht verändern. Das
         gemeinsame Planen eines Wochenplans in einer Gruppe funktioniert anders – siehe Ziffer 8a.</p>
      <h4>8a. Gemeinsam planen (Gruppen)</h4>
      <p>Mit „Gemeinsam planen" könnt ihr – etwa als Paar oder WG – <strong>denselben</strong> Wochenplan nutzen.
         Anders als beim Teilen-Link (Ziffer 8) ist das keine Kopie: Änderungen sind für alle Mitglieder sofort
         sichtbar. Für alle Mitglieder der Gruppe sichtbar sind dein <strong>angezeigter Name</strong>, dein
         optionales <strong>Profilbild</strong> (als kleines Abbild), deine <strong>Meals samt Fotos</strong>, der
         gemeinsame <strong>Wochenplan</strong>, ein optionaler <strong>Gruppenname</strong> und die Angabe,
         <strong>wer welches Meal angelegt hat</strong> (gespeichert wird dafür nur deine Nutzerkennung, nicht dein
         Name). Weist du ein geplantes Gericht nur einem Teil der Gruppe zu, statt es wie im Regelfall für alle
         gelten zu lassen, ist auch diese <strong>Zuweisung</strong> (per Nutzerkennung) für die ganze Gruppe
         sichtbar.</p>
      <p><strong>Nicht</strong> geteilt werden dein Kalorien- und Makroziel, deine Angaben aus den Einführungsfragen
         (Ziffer 3a), dein Gewichtsverlauf (Ziffer 3b), dein <strong>Wochenarchiv</strong> samt der Angabe,
         welche Tage du beplant hast (Ziffer 3), und deine <strong>E-Mail-Adresse</strong>. Jedes Mitglied
         sieht denselben Plan gegen sein jeweils eigenes Ziel.</p>
      <p>Eingeladen wird über einen <strong>Einladungslink</strong>. Für ihn gilt dasselbe wie für den Teilen-Link:
         80&nbsp;Bit Zufall, nicht erratbar, ein Auflisten ist technisch unterbunden. Ein Unterschied ist aber
         wesentlich – wer den Einladungslink öffnet und sich anmeldet, wird <strong>Mitglied</strong> und erhält
         zunächst das Recht zum <strong>Mitplanen</strong>; die Inhaberin oder der Inhaber der Gruppe kann das
         jederzeit auf <strong>Nur ansehen</strong> ändern, Mitglieder entfernen und den Einladungslink
         zurückziehen. Der Beitritt erfolgt nie automatisch – die App fragt dich vorher. Bis zum ersten Beitritt
         planst du unverändert für dich; erst danach ist der Plan wirklich gemeinsam.</p>
      <h4>9. Verschlüsselung</h4>
      <p>Die Übertragung der Daten erfolgt verschlüsselt über HTTPS (SSL/TLS).</p>
      <h4>10. Speicherdauer &amp; Löschung</h4>
      <p>Wir speichern deine Daten, solange dein Konto besteht – mit zwei Ausnahmen, die von selbst ablaufen. Erstens dein <strong>Wochenarchiv</strong>: Die Kennzahlen vergangener Kalenderwochen (Ziffer 3) bewahren wir nur für das laufende und die beiden vorangegangenen <strong>Kalenderjahre</strong> auf; Älteres entfernt die App automatisch, auch wenn dein Konto bestehen bleibt. Zweitens: Einträge, die du
         schnell in den Plan gelegt hast – per Barcode-Scan oder durch Antippen eines zählbaren
         Lebensmittels (z. B. ein Apfel) –, räumt die App nach etwa drei Wochen von selbst
         weg – aber nur, wenn sie in keiner deiner Wochen mehr eingeplant sind. Einmalig räumt die App außerdem
         Kopien aus dem mitgelieferten <strong>Rezeptbuch</strong> weg, die frühere Fassungen beim Planen angelegt
         haben: Sie werden nicht mehr gebraucht, weil dein Plan inzwischen direkt auf das mitgelieferte Gericht
         verweisen kann (Ziffer 3). Betroffen sind ausschließlich Kopien, die du <strong>nie verändert</strong> und
         nicht als Favorit markiert hast – alles, woran du gearbeitet hast, bleibt. Deine Wochenpläne bleiben dabei
         vollständig erhalten; sie zeigen anschließend auf das Rezept im Rezeptbuch. Über „Konto löschen" im Profilmenü kannst du dein
         Konto und deine Daten <strong>jederzeit selbst und sofort</strong> unwiderruflich löschen; alternativ kannst
         du die Löschung auch per E-Mail an uns verlangen. Das schließt deinen <strong>Pro-Status</strong> (siehe Ziffer 3) ein, der zusammen mit dem Konto entfernt wird,
         sowie alle Teilen-Links für einzelne Meals, die deinem
         Konto zugeordnet und diesem Gerät bzw. deinem synchronisierten Konto zum Löschzeitpunkt bekannt sind – sie
         werden automatisch mitentfernt; stellt sich beim Löschversuch heraus, dass ein Link ohnehin nicht mehr
         deinem Konto zugeordnet ist, wird er übersprungen. Schlägt das Entfernen aus einem anderen Grund fehl,
         bricht die Löschung ab, statt einen Rest zurückzulassen, und du kannst sie erneut anstoßen. Bis zur Löschung bleiben geteilte Inhalte
         abrufbar – auch dann, wenn du den Link nicht mehr weitergibst. Nutzt du die App ohne Cloud-Konto (lokales
         Profil), kannst du ebenso über „Alle Daten löschen" im Profilmenü sämtliche auf diesem Gerät gespeicherten
         Daten sofort entfernen.</p>
      <p>Bist du <strong>Mitglied einer Gruppe</strong> (Ziffer 8a), werden beim Löschen deines Kontos zusätzlich
         dein Mitglieder-Eintrag (Name und Bild) sowie die von dir erstellten Einladungslinks mitentfernt. Bist du
         <strong>Inhaber</strong> einer Gruppe, musst du sie vorher auflösen – die App weist dich darauf hin, damit
         keine Gruppe ohne Inhaber zurückbleibt.</p>
      <p>Verlässt du eine Gruppe oder löst sie auf, wird dein Mitglieder-Eintrag entfernt und du siehst den
         gemeinsamen Plan nicht mehr. Die von dir erstellten Einladungslinks werden dabei ebenfalls gelöscht –
         du musst dafür nicht bis zur Kontolöschung warten. Die Meals und Wochenpläne, die in der Gruppe entstanden
         sind, <strong>bleiben bei der Gruppe</strong> – du behältst davon eine eigene Kopie. Das gilt auch für Meals, die ursprünglich von dir stammen: Sobald du
         sie in eine Gruppe eingebracht hast, kannst du sie den übrigen Mitgliedern nicht mehr einseitig entziehen.
         Der Personenbezug entfällt dabei, weil zu einem Meal nur deine Nutzerkennung gespeichert ist, die mit
         deinem Mitglieder-Eintrag verschwindet.</p>
      <h4>11. Deine Rechte</h4>
      <p>Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch – wende dich dafür an die in Ziffer 1 genannte Adresse; Löschen und Widerruf gehen zusätzlich direkt in der App (Ziffern 3b und 10). Soweit eine Verarbeitung auf deiner Einwilligung beruht, kannst du diese jederzeit mit Wirkung für die Zukunft widerrufen. Zudem hast du ein Beschwerderecht bei einer Datenschutz-Aufsichtsbehörde – für uns zuständig ist das Bayerische Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach.</p>
      <h4>12. Automatisierte Entscheidungsfindung</h4>
      <p>Eine automatisierte Entscheidungsfindung oder ein Profiling mit rechtlicher Wirkung oder ähnlich erheblicher
         Beeinträchtigung im Sinne des Art. 22 DSGVO findet nicht statt. Funktionen, die dir etwas <em>vorschlagen</em> –
         etwa der automatische Wochenplaner, der aus deinen eigenen Meals einen Vorschlag gegen dein Kalorienziel
         zusammenstellt – fallen nicht darunter: Das Ergebnis ist ein Vorschlag in deinem Plan, den du jederzeit ändern,
         rückgängig machen oder löschen kannst.</p>`;
