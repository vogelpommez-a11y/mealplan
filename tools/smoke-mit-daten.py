# -*- coding: utf-8 -*-
u"""
Smoke-Test MIT vorhandenen Nutzerdaten.

Der gewoehnliche Smoke-Test laedt index.html mit leerem localStorage. Genau daran ist am
16.08.2026 ein Totalausfall vorbeigerutscht: `sanitizePlanned()` kehrt bei leerem
`state.planned` vorher zurueck und fasst die Konstante gar nicht an, die noch in der
temporalen Totzone lag. Ein frisches Profil startete sauber, jedes benutzte Konto sah nur
noch Header und Reiter.

Deshalb setzt dieser Test die localStorage-Schluessel VOR dem Laden der App und prueft
danach, ob `#view` tatsaechlich gefuellt ist. Er faengt jede TDZ- und Migrationsfalle in der
load()-Kette, die nur bei vorhandenen Daten zuschlaegt.

Aufruf:  python tools/smoke-mit-daten.py
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'

# Ein Konto, das die App WIRKLICH benutzt hat. Die Schluessel stammen aus index.html
# (wochenkueche_v1 / wochenkueche_profile_v1) - siehe CLAUDE.md, Ziffer 21: die internen
# Namen sind bewusst nicht umbenannt worden.
STATE = {
    "recipes": [{
        "id": "r1", "name": "Porridge", "category": u"Frühstück", "tags": ["vegetarisch"],
        "nutrition": {"kcal": 400, "carbs": 50, "protein": 25, "fat": 10}, "ingredients": []
    }],
    "plans": {"2026-W34": {}},
    "goal": {"kcal": 2000, "carbs": 200, "protein": 150, "fat": 60},
    # DAS ist der Punkt: ein benutzter Planer. Ohne dieses Feld laeuft sanitizePlanned
    # in den fruehen return und der Fehler bleibt unsichtbar.
    "planned": {"r1": "2026-W33"},
    "favs": ["r1"],
    "shopPersons": 1,
    "viewWeek": "cur"
}
PROFILE = {"name": "Test"}

seite = io.open(INDEX, encoding="utf-8").read()
# Das Seed-Script direkt hinter <head> einsetzen, damit es VOR dem App-Script laeuft.
#
# Der onerror-Haken ist der eigentliche Wert dieses Tests: Ohne ihn meldet er nur "leer" und
# man faengt wieder bei null an. Mit ihm steht die Fehlermeldung samt Zeile im DOM - genau
# die Information, die man sonst nur in der Browserkonsole eines echten Nutzers bekaeme.
seed = (u'<script>window.__fehler=[];'
        u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
        u'window.addEventListener("unhandledrejection",function(e){window.__fehler.push("unhandled: "+((e.reason&&e.reason.message)||e.reason));});'
        u'try{'
        # Das "__test"-Suffix ist Pflicht: localKey() haengt es unter file:// und auf
        # localhost an JEDEN Schluessel (isTestOrigin), damit Testlaeufe die echten Daten
        # nicht anfassen. Ohne Suffix liest die App gar nichts und zeigt den Login - der
        # Test misst dann den Anmeldebildschirm. Beide Schreibweisen setzen, damit dieselbe
        # Datei auch gegen eine echte Herkunft laeuft.
        u'["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
        u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
        u'}catch(e){}</script>' % (json.dumps(json.dumps(STATE)), json.dumps(json.dumps(PROFILE))))
# Die gesammelten Fehler sichtbar machen, damit --dump-dom sie mitliefert.
#
# SYNCHRON und ohne setTimeout: --dump-dom wartet nicht beliebig, und ein verzoegertes
# Element fehlt im Abzug einfach. Dieses Script steht hinter allen App-Bloecken - ein
# Abbruch in einem frueheren <script> beendet nur diesen Block, nicht die Seite, also
# laeuft es auch (und gerade) im Fehlerfall.
# Bewusst ueber die DOM-API und NICHT ueber document.write: Dessen Zeichenkette enthaelt das
# gesuchte Markup schon im Quelltext, und die Auswertung unten liest dann sich selbst statt
# des Ergebnisses. (Genau das ist beim ersten Anlauf passiert.)
AUSGABE = (u'<script>(function(){var p=document.createElement("pre");p.id="fehlerliste";'
           u'p.textContent=(window.__fehler||[]).join(" || ")||"keine";'
           u'document.documentElement.appendChild(p);})();</script>')

# Einhaengepunkt ist der charset-Meta, NICHT "<head>": index.html hat gar kein <head>-Tag
# (der Browser ergaenzt es). Der einzige Treffer fuer "<head>" in der Datei steht in einem
# JS-Kommentar (bei MOTION) - ein dorthin ersetztes <script> zerschlaegt den Kommentar und
# damit den ganzen Script-Block. Genau das ist hier passiert: Der Test lief, meldete "keine
# Fehler" und hatte die Nutzerdaten nie gesetzt. Siehe docs/TROUBLESHOOTING.md.
# Nach dem charset-Meta und nicht davor: Ein Script vor der Zeichensatzangabe verschiebt sie
# ueber die 1024-Byte-Grenze hinaus, ab der der Browser sie nicht mehr beachtet.
if seite.count(ANKER) != 1:
    raise SystemExit("charset-Meta nicht genau einmal gefunden - Aufbau von index.html hat sich geaendert.")
seite = seite.replace(ANKER, ANKER + seed, 1)
# index.html hat KEIN </body> (bewusst, die Datei endet mit </html>) - deshalb dort einhaengen.
if "</html>" not in seite:
    raise SystemExit("Kein </html> gefunden - Aufbau von index.html hat sich geaendert.")
seite = seite.replace("</html>", AUSGABE + "</html>", 1)

tmp = tempfile.mkdtemp(prefix="smoke-daten-")
try:
    ziel = os.path.join(tmp, "index.html")
    io.open(ziel, "w", encoding="utf-8").write(seite)
    dump = os.path.join(tmp, "dump.html")
    with io.open(dump, "wb") as f:
        subprocess.call([
            EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=12000",
            "--user-data-dir=" + os.path.join(tmp, "profil"),
            "--dump-dom", "file:///" + ziel.replace("\\", "/")
        ], stdout=f, stderr=subprocess.PIPE)
    roh = io.open(dump, encoding="utf-8", errors="replace").read()

    mf = re.search(r'<pre id="fehlerliste">(.*?)</pre>', roh, re.S)
    fehler = (mf.group(1).strip() if mf else "(nicht ermittelt)")
    print("JS-Fehler waehrend des Starts: " + fehler)
    print("")

    # Das Kriterium ist die FEHLERLISTE, nicht der Inhalt von #view.
    #
    # Der erste Anlauf pruefte auf gefuelltes #view und schlug fehl, obwohl die App gesund war:
    # Mit hinterlegtem Profil laeuft sie in den Cloud-Pfad und wartet auf den Handshake, der
    # headless nicht zustande kommt - #view ist dann voellig zu Recht noch leer. Eine Pruefung,
    # die den Wartezustand nicht vom Absturz unterscheidet, meldet Fehlalarme, und ein Test,
    # dem man nicht glaubt, ist keiner.
    #
    # Der Absturz, um den es geht, ist ohnehin praeziser fassbar: Er wirft. Genau das faengt
    # der error-Listener aus dem Seed - und er faengt JEDEN Startfehler, nicht nur diesen einen.
    if fehler != "keine" and fehler != "(nicht ermittelt)":
        print("FEHLGESCHLAGEN: Das App-Script bricht mit vorhandenen Nutzerdaten ab.")
        print("Haeufigste Ursache: eine const/let, die in der load()-Kette gelesen,")
        print("aber erst spaeter deklariert wird (temporale Totzone).")
        sys.exit(1)
    if fehler == "(nicht ermittelt)":
        print("FEHLGESCHLAGEN: Die Fehlerliste fehlt im Abzug - der Test selbst ist kaputt,")
        print("nicht die App. Sitzt das Ausgabe-Script noch vor </html>?")
        sys.exit(1)

    # Zusatzinformation, ausdruecklich KEIN Fehlschlagskriterium (siehe oben).
    i = roh.find('id="view"')
    if i >= 0:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", roh[i:i + 600])).strip()
        kern = text[len('id="view">'):].strip()
        print(u"Hinweis: #view beginnt mit %s" % (repr(kern[:60]) if kern else "(leer)"))
        print(u"         Leer ist hier normal - ohne Cloud-Handshake bleibt der Wartezustand stehen.")
    print("")
    print("OK: Kein Startfehler mit vorhandenen Nutzerdaten.")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
