#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Pruefstand fuer Sicherung und Rueckspielung der Firestore-Daten.

Warum es diesen Pruefstand gibt
-------------------------------
Ein Backup ist die einzige Funktion im Projekt, deren Fehler man erst bemerkt, wenn es zu
spaet ist: Sie meldet jahrelang "gesichert", und am Tag des Datenverlusts stellt sich
heraus, dass die Haelfte fehlte. Deshalb wird hier nicht die Schnittstelle geprueft, sondern
die Zusage - dass wirklich ALLES mitkommt, dass nichts ins Repo faellt und dass die
Rueckspielung nichts anfasst, was sie nicht anfassen soll.

Geprueft wird gegen einen NACHGEBAUTEN Transport, nicht gegen die Cloud. Das ist hier kein
Nachbau der Logik (den verbietet CLAUDE.md Abschnitt 11) - die echten Funktionen aus
`firestore_api`, `firestore-backup` und `firestore-restore` laufen unveraendert. Ersetzt ist
nur die eine Stelle, die ins Netz geht. Proben gehoeren nie an die Cloud echter Nutzer.

Aufruf:
    python tools/pruefstand-firestore-backup.py
    python tools/pruefstand-firestore-backup.py --gegenprobe
"""
import datetime
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import urllib.parse

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import firestore_api as fs


def _modul(dateiname, name):
    u"""Laedt ein Werkzeug mit Bindestrich im Namen - `import` kann das nicht."""
    pfad = os.path.join(HIER, dateiname)
    spec = importlib.util.spec_from_file_location(name, pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


bk = _modul("firestore-backup.py", "firestore_backup")
rs = _modul("firestore-restore.py", "firestore_restore")

ok = [0]
rot = [0]


def pruef(was, ist, soll):
    if ist == soll:
        ok[0] += 1
        print(u"OK   %s" % was)
        return True
    rot[0] += 1
    print(u"ROT  %s" % was)
    print(u"     ist:  %r" % (ist,))
    print(u"     soll: %r" % (soll,))
    return False


# ---------------------------------------------------------------------------
# Der nachgebaute Transport
# ---------------------------------------------------------------------------
class FakeZugang(fs.Zugang):
    u"""Beantwortet die REST-Aufrufe aus einem Dict, statt ins Netz zu gehen.

    Ueberschrieben ist NUR `roh()`. Alles darueber - Pfadbildung, Blaettern, Rekursion,
    updateMask - ist der echte Code und wird hier wirklich durchlaufen.
    """

    SEITE = 2   # absichtlich winzig, damit das Blaettern in JEDEM Lauf drankommt

    def __init__(self, daten, projekt="test-projekt"):
        fs.Zugang.__init__(self, projekt=projekt, token="test-token")
        self.daten = dict(daten)
        self.aufrufe = []

    def _pfad_aus(self, url):
        marke = "/documents"
        rest = url[url.find(marke) + len(marke):]
        rest = rest.split("?")[0].split(":")[0]
        return urllib.parse.unquote(rest.lstrip("/"))

    def roh(self, methode, url, rumpf=None):
        self.aufrufe.append((methode, url))
        pfad = self._pfad_aus(url)

        if url.split("?")[0].endswith(":listCollectionIds"):
            tiefe = len(pfad.split("/")) if pfad else 0
            raus = set()
            for p in self.daten:
                teile = p.split("/")
                if pfad and not (p.startswith(pfad + "/") and len(teile) > tiefe + 1):
                    continue
                if not pfad and len(teile) != 2:
                    continue
                raus.add(teile[tiefe])
            return {"collectionIds": sorted(raus)}

        if methode == "GET":
            teile = pfad.split("/")
            if len(teile) % 2 == 1:           # ungerade -> Sammlung
                treffer = sorted(p for p in self.daten
                                 if p.startswith(pfad + "/")
                                 and len(p.split("/")) == len(teile) + 1)
                frage = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                ab = int(frage.get("pageToken", ["0"])[0])
                stueck = treffer[ab:ab + self.SEITE]
                antwort = {"documents": [self._doc(p) for p in stueck]}
                if ab + self.SEITE < len(treffer):
                    antwort["nextPageToken"] = str(ab + self.SEITE)
                return antwort
            if pfad not in self.daten:        # gerade -> Dokument
                raise fs.ZugangFehler(u"Firestore antwortete mit HTTP 404")
            return self._doc(pfad)

        if methode == "PATCH":
            frage = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            maske = frage.get("updateMask.fieldPaths", [])
            felder = dict(self.daten.get(pfad, {}))
            for name in maske:
                felder.pop(name.strip("`"), None)
            felder.update((rumpf or {}).get("fields", {}))
            self.daten[pfad] = felder
            return {}

        raise AssertionError("unerwartete Methode %s" % methode)

    def _doc(self, pfad):
        return {"name": "projects/%s/databases/(default)/documents/%s" % (self.projekt, pfad),
                "fields": self.daten[pfad]}


def testdaten():
    u"""Ein kleiner, aber echter Ausschnitt der Struktur aus firestore.rules."""
    return {
        "users/u1": {"goal": {"stringValue": "abnehmen"},
                     "weight": {"doubleValue": 82.5},
                     "streak": {"integerValue": "7"}},
        "users/u1/recipes/r1": {"title": {"stringValue": "Porridge"}},
        "users/u1/recipes/r2": {"title": {"stringValue": "Chili"}},
        "users/u1/recipes/r3": {"title": {"stringValue": "Salat"}},
        "users/u2": {"goal": {"stringValue": "halten"}},
        "groups/g1": {"name": {"stringValue": "WG"},
                      "memberCount": {"integerValue": "2"}},
        "groups/g1/members/u1": {"role": {"stringValue": "owner"}},
        "groups/g1/members/u2": {"role": {"stringValue": "edit"}},
        "groups/g1/plans/2026-W38": {"mon_mi": {"arrayValue": {"values": [
            {"stringValue": "r1"}]}}},
        "entitlements/u1": {"pro": {"booleanValue": True}},
        "invites/abc": {"gid": {"stringValue": "g1"}},
    }


def main():
    gegenprobe = "--gegenprobe" in sys.argv
    print(u"Pruefstand: Firestore-Sicherung und -Rueckspielung")
    print(u"=" * 62)

    daten = testdaten()
    z = FakeZugang(daten)

    # ---- 1. Vollstaendigkeit: kommt wirklich alles mit? --------------------
    print(u"")
    print(u"-- Sichern: Vollstaendigkeit --")
    alles = z.alles()
    pruef(u"jedes Dokument ist in der Sicherung", sorted(alles), sorted(daten))
    pruef(u"auch die Unterkollektion users/u1/recipes",
          sorted(p for p in alles if p.startswith("users/u1/recipes/")),
          ["users/u1/recipes/r1", "users/u1/recipes/r2", "users/u1/recipes/r3"])
    pruef(u"auch die zweite Ebene unter groups/g1",
          sorted(p for p in alles if p.startswith("groups/g1/")),
          ["groups/g1/members/u1", "groups/g1/members/u2", "groups/g1/plans/2026-W38"])
    # Das Blaettern: recipes hat 3 Dokumente bei Seitengroesse 2.
    pruef(u"ueber die Seitengrenze hinweg wird weitergeblaettert",
          len([p for p in alles if p.startswith("users/u1/recipes/")]), 3)

    # ---- 2. Die Falle aus CLAUDE.md 18b: eine NEUE Sammlung ----------------
    print(u"")
    print(u"-- Sichern: eine neue Sammlung kommt von selbst mit --")
    spaeter = dict(daten)
    spaeter["marketing/kampagne1"] = {"titel": {"stringValue": "Herbst"}}
    spaeter["users/u1/notizen/n1"] = {"text": {"stringValue": "mehr Protein"}}
    z2 = FakeZugang(spaeter)
    alles2 = z2.alles()
    pruef(u"eine neue Wurzelsammlung wird mitgesichert",
          "marketing/kampagne1" in alles2, True)
    pruef(u"eine neue Unterkollektion wird mitgesichert",
          "users/u1/notizen/n1" in alles2, True)

    # ---- 3. Rohformat: verlustfrei ----------------------------------------
    print(u"")
    print(u"-- Sichern: das Rohformat bleibt roh --")
    pruef(u"eine Ganzzahl bleibt integerValue (wird nicht zu 7.0)",
          alles["users/u1"]["streak"], {"integerValue": "7"})
    pruef(u"eine Kommazahl bleibt doubleValue",
          alles["users/u1"]["weight"], {"doubleValue": 82.5})
    pruef(u"ein Array bleibt unveraendert",
          alles["groups/g1/plans/2026-W38"]["mon_mi"],
          {"arrayValue": {"values": [{"stringValue": "r1"}]}})

    # ---- 4. Das Ziel darf nie im Repo liegen ------------------------------
    print(u"")
    print(u"-- Sichern: fremde Daten fallen nie ins Repo --")
    for versuch in [fs.WURZEL, os.path.join(fs.WURZEL, "data"), os.path.join(fs.WURZEL, "x", "y")]:
        try:
            bk.ziel_pruefen(versuch)
            pruef(u"Ziel im Repo wird abgelehnt (%s)" % os.path.relpath(versuch, fs.WURZEL),
                  "durchgelassen", "abgelehnt")
        except fs.ZugangFehler:
            pruef(u"Ziel im Repo wird abgelehnt (%s)" % os.path.relpath(versuch, fs.WURZEL),
                  "abgelehnt", "abgelehnt")
    neben = os.path.join(os.path.dirname(fs.WURZEL), "Mealplan-Backups")
    try:
        bk.ziel_pruefen(neben)
        pruef(u"ein Ziel neben dem Repo ist erlaubt", "erlaubt", "erlaubt")
    except fs.ZugangFehler:
        pruef(u"ein Ziel neben dem Repo ist erlaubt", "abgelehnt", "erlaubt")
    # Der Ordnername des Repos ist ein PRAEFIX des Backup-Ordners - ein naiver
    # startswith() ohne Trennzeichen wuerde hier faelschlich ablehnen.
    try:
        bk.ziel_pruefen(fs.WURZEL + "-Backups")
        pruef(u"ein Nachbarordner mit gleichem Namensanfang ist erlaubt", "erlaubt", "erlaubt")
    except fs.ZugangFehler:
        pruef(u"ein Nachbarordner mit gleichem Namensanfang ist erlaubt", "abgelehnt", "erlaubt")

    # Windows: NTFS ist unempfindlich gegen Gross-/Kleinschreibung, ein Stringvergleich
    # nicht. Ohne normcase() haette derselbe Ordner in anderer Schreibweise die Pruefung
    # passiert - und die Daten aller Nutzer laegen im Repo.
    anders_geschrieben = os.path.join(fs.WURZEL.upper(), "backups")
    try:
        bk.ziel_pruefen(anders_geschrieben)
        pruef(u"Ziel im Repo in ANDERER Schreibweise wird abgelehnt",
              "durchgelassen", "abgelehnt")
    except fs.ZugangFehler:
        pruef(u"Ziel im Repo in ANDERER Schreibweise wird abgelehnt",
              "abgelehnt", "abgelehnt")
    # Ein Pfad, der ueber '..' wieder ins Repo zurueckfuehrt.
    zurueck = os.path.join(os.path.dirname(fs.WURZEL), "..", "Documents",
                           os.path.basename(fs.WURZEL), "backups")
    try:
        bk.ziel_pruefen(zurueck)
        pruef(u"ein Ziel, das ueber .. ins Repo zurueckfuehrt, wird abgelehnt",
              "durchgelassen", "abgelehnt")
    except fs.ZugangFehler:
        pruef(u"ein Ziel, das ueber .. ins Repo zurueckfuehrt, wird abgelehnt",
              "abgelehnt", "abgelehnt")

    # ---- 4b. Pfade aus der Sicherungsdatei sind eine EINGABE ----------------
    print(u"")
    print(u"-- Rueckspielen: der Pfad aus der Datei wird geprueft --")
    # Der gefaehrliche Fall: Ein Segment kapert den Query-String. Ein PATCH ohne
    # updateMask ersetzt in Firestore das GANZE Dokument statt einzelner Felder.
    boese = [
        u"users/abc/x?currentDocument.exists=false&y=",
        u"users/abc?updateMask.fieldPaths=goal",
        u"users/../../andere/abc",
        u"users/abc#fragment",
        u"users/ abc",
        u"users/abc:runQuery",
        u"users%2Fabc",
        u"users//abc",
        u"users/abc\nX",
    ]
    for p in boese:
        pruef(u"abgelehnt: %r" % p, fs.pfad_ok(p), False)
    for p in [u"users/abc", u"users/u1/recipes/r1", u"groups/g-1/plans/2026-W38",
              u"entitlements/u.1~2"]:
        pruef(u"erlaubt: %s" % p, fs.pfad_ok(p), True)
    # Eine ungerade Segmentzahl ist eine SAMMLUNG, kein Dokument - als Schreibziel sinnlos.
    pruef(u"eine Sammlung ist kein gueltiges Dokumentziel", fs.pfad_ok(u"users"), False)
    pruef(u"und auch nicht drei Segmente tief",
          fs.pfad_ok(u"users/u1/recipes"), False)

    # Und der Weg dahin: lade_stand() muss eine solche Datei ABLEHNEN, nicht nur melden.
    tmpb = tempfile.mkdtemp(prefix="pm-backup-boese-")
    try:
        with io.open(os.path.join(tmpb, "users.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps({u"users/abc/x?currentDocument.exists=false&y=": {}}))
        try:
            rs.lade_stand(tmpb)
            pruef(u"eine Sicherung mit praepariertem Pfad wird verworfen",
                  "verwendet", "verworfen")
        except fs.ZugangFehler:
            pruef(u"eine Sicherung mit praepariertem Pfad wird verworfen",
                  "verworfen", "verworfen")
    finally:
        shutil.rmtree(tmpb, ignore_errors=True)

    # Zweite Schicht: Auch wenn ein Pfad durchkaeme, darf er die URL nicht sprengen.
    zq = FakeZugang(daten)
    gebaut = zq._url(u"users/abc?x=1")
    pruef(u"ein Fragezeichen im Pfad wird in der URL kodiert",
          "?x=1" in gebaut.split("/documents/")[1], False)

    # ---- 5. Aufteilen auf Dateien ------------------------------------------
    print(u"")
    print(u"-- Sichern: Aufteilung auf Dateien --")
    teile = bk.aufteilen(alles)
    pruef(u"je Wurzelsammlung eine Datei",
          sorted(teile), ["entitlements", "groups", "invites", "users"])
    pruef(u"die Unterkollektion liegt in der Datei ihrer Wurzel",
          "users/u1/recipes/r1" in teile["users"], True)
    pruef(u"der Schluessel bleibt der VOLLE Pfad",
          sorted(teile["groups"]),
          ["groups/g1", "groups/g1/members/u1", "groups/g1/members/u2",
           "groups/g1/plans/2026-W38"])

    # ---- 6. Der ganze Lauf, auf die Platte ---------------------------------
    print(u"")
    print(u"-- Sichern: ein vollstaendiger Lauf --")
    tmp = tempfile.mkdtemp(prefix="pm-backup-test-")
    try:
        manifest = bk.sichere(z, tmp, jetzt=datetime.datetime(2026, 9, 17, 14, 30))
        pruef(u"das Manifest zaehlt alle Dokumente", manifest["dokumente"], len(daten))
        pruef(u"der Ordner heisst nach Datum und Uhrzeit",
              os.path.basename(manifest["ordner"]), "2026-09-17-1430")
        geschrieben = sorted(os.listdir(manifest["ordner"]))
        pruef(u"geschrieben wurden alle Sammlungen plus Manifest", geschrieben,
              ["entitlements.json", "groups.json", "invites.json", "manifest.json",
               "users.json"])
        zurueck = rs.lade_stand(manifest["ordner"])
        pruef(u"was geschrieben wurde, laesst sich unveraendert wieder lesen",
              zurueck, alles)

        # Zweimal in derselben Minute darf nichts ueberschreiben.
        m2 = bk.sichere(z, tmp, jetzt=datetime.datetime(2026, 9, 17, 14, 30))
        pruef(u"ein zweiter Lauf in derselben Minute bekommt einen eigenen Ordner",
              os.path.basename(m2["ordner"]), "2026-09-17-1430-2")

        # Eine leere Antwort ist ein Zugriffsbefund, kein Datenbefund.
        leer = FakeZugang({})
        try:
            bk.sichere(leer, tmp)
            pruef(u"eine LEERE Sicherung wird gar nicht erst angelegt",
                  "angelegt", "abgebrochen")
        except fs.ZugangFehler:
            pruef(u"eine LEERE Sicherung wird gar nicht erst angelegt",
                  "abgebrochen", "abgebrochen")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 7. Aufbewahrung ---------------------------------------------------
    print(u"")
    print(u"-- Sichern: alte Staende raeumen --")
    tmp2 = tempfile.mkdtemp(prefix="pm-backup-alter-")
    try:
        # 14 Staende, einer je Tag, der aelteste 200 Tage alt.
        jetzt = datetime.datetime(2026, 9, 17, 12, 0)
        for i in range(14):
            tag = jetzt - datetime.timedelta(days=200 - i * 15)
            os.makedirs(os.path.join(tmp2, tag.strftime("%Y-%m-%d-%H%M")))
        vorher = bk.staende(tmp2)
        weg = bk.alte_raeumen(tmp2, jetzt=jetzt)
        uebrig = bk.staende(tmp2)
        pruef(u"zu alte Staende werden geloescht", len(weg) > 0, True)
        pruef(u"geloescht wurde nur von vorn (die aeltesten)",
              weg, vorher[:len(weg)])

        # DIE Zusage aus docs/DATENSCHUTZ-INTERN.md 3a, gemessen statt geglaubt:
        # Nach dem Raeumen ist KEIN Stand mehr aelter als die Frist - ausser dem juengsten.
        zu_alt = [n for n in uebrig[:-1]
                  if (jetzt - bk._datum_aus(n)).days > bk.BEHALTEN_TAGE]
        pruef(u"danach ist kein Stand mehr aelter als 90 Tage (ausser dem juengsten)",
              zu_alt, [])
        pruef(u"die Voreinstellung behaelt genau EINEN Stand unabhaengig vom Alter",
              bk.MINDESTENS_STAENDE, 1)

        # Der juengste bleibt, auch wenn ALLES zu alt ist - sonst stuende man ohne Kopie da.
        tmp3 = tempfile.mkdtemp(prefix="pm-backup-alt2-")
        try:
            namen = []
            for i in range(3):
                tag = jetzt - datetime.timedelta(days=500 + i)
                namen.append(tag.strftime("%Y-%m-%d-%H%M"))
                os.makedirs(os.path.join(tmp3, namen[-1]))
            weg3 = bk.alte_raeumen(tmp3, jetzt=jetzt)
            uebrig3 = bk.staende(tmp3)
            pruef(u"sind ALLE zu alt, bleibt genau der juengste stehen", len(uebrig3), 1)
            pruef(u"und zwar wirklich der juengste", uebrig3, [max(namen)])
            pruef(u"die anderen sind weg", len(weg3), 2)
        finally:
            shutil.rmtree(tmp3, ignore_errors=True)
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # ---- 8. Rueckspielen: Filter ------------------------------------------
    print(u"")
    print(u"-- Rueckspielen: der Filter --")
    nur_u1 = rs.gefiltert(alles, "users/u1")
    pruef(u"--nur users/u1 nimmt das Konto UND seine Rezepte",
          sorted(nur_u1),
          ["users/u1", "users/u1/recipes/r1", "users/u1/recipes/r2", "users/u1/recipes/r3"])
    pruef(u"und laesst das fremde Konto in Ruhe", "users/u2" in nur_u1, False)
    pruef(u"ohne Filter bleibt alles", len(rs.gefiltert(alles, None)), len(alles))

    # ---- 9. Rueckspielen: der Vergleich ------------------------------------
    print(u"")
    print(u"-- Rueckspielen: was der Trockenlauf sieht --")
    live = dict(alles)
    del live["users/u1/recipes/r2"]                                   # verloren
    live["users/u1"] = {"goal": {"stringValue": "aufbauen"},          # geaendert
                        "weight": {"doubleValue": 82.5},
                        "streak": {"integerValue": "7"},
                        "neuesFeld": {"stringValue": "spaeter dazu"}}
    live["users/u3"] = {"goal": {"stringValue": "halten"}}            # nach der Sicherung neu
    plan, extras = rs.vergleiche(alles, live)
    arten = {p: a for p, a, _ in plan}
    pruef(u"ein verlorenes Dokument gilt als NEU",
          arten["users/u1/recipes/r2"], "neu")
    pruef(u"ein geaendertes Dokument gilt als ABWEICHEND",
          arten["users/u1"], "abweichend")
    pruef(u"ein unveraendertes Dokument gilt als GLEICH",
          arten["users/u2"], "gleich")
    pruef(u"ein Feld, das es nur live gibt, wird zum Leeren vorgemerkt",
          [z for p, a, z in plan if p == "users/u1"][0], ["neuesFeld"])
    pruef(u"ein nach der Sicherung entstandenes Konto ist ein Extra",
          extras, ["users/u3"])

    # ---- 10. Rueckspielen: der Trockenlauf schreibt NICHTS ------------------
    print(u"")
    print(u"-- Rueckspielen: der Trockenlauf fasst nichts an --")
    zt = FakeZugang(live)
    rs.vergleiche(alles, rs.hole_live(zt, alles, None))
    pruef(u"nach einem Trockenlauf ist kein Schreibvorgang passiert", zt.geschrieben, 0)
    pruef(u"und die Daten stehen unveraendert da", zt.daten, live)

    # ---- 11. Rueckspielen: das Schreiben -----------------------------------
    print(u"")
    print(u"-- Rueckspielen: das Schreiben --")
    zs = FakeZugang(live)
    n = rs.spiele_zurueck(zs, alles, plan)
    pruef(u"geschrieben wird nur, was neu oder abweichend ist", n, 2)
    pruef(u"das verlorene Rezept ist zurueck",
          zs.daten.get("users/u1/recipes/r2"), {"title": {"stringValue": "Chili"}})
    pruef(u"das geaenderte Dokument steht wieder auf dem Stand der Sicherung",
          zs.daten["users/u1"], alles["users/u1"])
    pruef(u"das Feld, das es nur live gab, ist weg",
          "neuesFeld" in zs.daten["users/u1"], False)
    pruef(u"das Extra wurde NICHT geloescht",
          zs.daten.get("users/u3"), {"goal": {"stringValue": "halten"}})
    pruef(u"unveraenderte Dokumente kosteten keinen Schreibvorgang", zs.geschrieben, 2)

    # ---- 11b. Aufrufparameter: eine Meldung statt eines Stacktrace ----------
    print(u"")
    print(u"-- Bedienung: kaputte Aufrufe enden mit einer Meldung --")
    pruef(u"ein fehlender Schalter liefert den Standardwert",
          fs.arg(["skript"], "--ziel", "standard"), "standard")
    pruef(u"ein gesetzter Schalter liefert seinen Wert",
          fs.arg(["skript", "--ziel", "D:/x"], "--ziel"), "D:/x")
    pruef(u"eine Zahl wird als Zahl geliefert",
          fs.arg(["skript", "--behalten", "30"], "--behalten", zahl=True), 30)
    for kaputt, was in [(["skript", "--ziel"], u"Wert fehlt am Ende"),
                        (["skript", "--ziel", "--behalten", "30"], u"naechster Schalter statt Wert")]:
        try:
            fs.arg(kaputt, "--ziel")
            pruef(u"abgefangen: %s" % was, "Absturz", "Meldung")
        except fs.ZugangFehler:
            pruef(u"abgefangen: %s" % was, "Meldung", "Meldung")
    try:
        fs.arg(["skript", "--behalten", "neunzig"], "--behalten", zahl=True)
        pruef(u"abgefangen: Zahl ist keine Zahl", "Absturz", "Meldung")
    except fs.ZugangFehler:
        pruef(u"abgefangen: Zahl ist keine Zahl", "Meldung", "Meldung")

    # ---- 12. updateMask -----------------------------------------------------
    print(u"")
    print(u"-- Rueckspielen: Feldnamen in der Maske --")
    pruef(u"ein schlichter Name steht nackt", fs._maskenname("goal"), "goal")
    pruef(u"ein Name mit Punkt bekommt Backticks",
          fs._maskenname("mon.mi"), "`mon.mi`")
    pruef(u"ein Name mit Backtick wird escaped",
          fs._maskenname("a`b"), "`a\\`b`")

    print(u"")
    print(u"ERGEBNIS %d gruen, %d rot" % (ok[0], rot[0]))

    if gegenprobe:
        print(u"")
        print(u"Gegenprobe: merkt dieser Pruefstand die Fehler, die er verhindern soll?")
        print(u"-" * 62)
        erwischt = 0

        # (a) Eine Fassung, die Unterkollektionen ueberspringt - der klassische
        #     Backup-Fehler: sieht vollstaendig aus, sichert die halbe App.
        class OhneUnter(FakeZugang):
            def alles(self, melder=None):
                raus = {}
                for s in self.sammlungen():
                    for d in self.dokumente(s):
                        raus[self.kurz(d["name"])] = d.get("fields", {})
                return raus

        blind = OhneUnter(daten).alles()
        if sorted(blind) != sorted(daten):
            print(u"  GRUEN  eine Fassung ohne Unterkollektionen faellt auf")
            print(u"         (%d statt %d Dokumente)" % (len(blind), len(daten)))
            erwischt += 1
        else:
            print(u"  ROT    eine Fassung ohne Unterkollektionen faellt NICHT auf")

        # (b) Eine Fassung mit fest verdrahteter Sammlungsliste - sie kennt die
        #     Sammlung von morgen nicht (CLAUDE.md 18b).
        class FesteListe(FakeZugang):
            def sammlungen(self, doku_pfad=""):
                echte = FakeZugang.sammlungen(self, doku_pfad)
                if not doku_pfad:
                    return [s for s in echte
                            if s in ("users", "groups", "entitlements", "invites")]
                return echte

        starr = FesteListe(spaeter).alles()
        if "marketing/kampagne1" not in starr:
            print(u"  GRUEN  eine feste Sammlungsliste faellt auf (marketing fehlt)")
            erwischt += 1
        else:
            print(u"  ROT    eine feste Sammlungsliste faellt NICHT auf")

        # (c) Eine Rueckspielung, die Extras mit wegraeumt.
        zx = FakeZugang(live)
        rs.spiele_zurueck(zx, alles, plan)
        for p in list(zx.daten):
            if p not in alles:
                del zx.daten[p]          # genau das, was NIE passieren darf
        if "users/u3" not in zx.daten:
            print(u"  GRUEN  eine Rueckspielung, die Extras loescht, faellt auf")
            erwischt += 1
        else:
            print(u"  ROT    eine Rueckspielung, die Extras loescht, faellt NICHT auf")

        # (d) Ein Ziel im Repo, das durchgelassen wird.
        naiv = os.path.join(fs.WURZEL, "backups")
        try:
            bk.ziel_pruefen(naiv)
            print(u"  ROT    ein Ziel im Repo wurde durchgelassen")
        except fs.ZugangFehler:
            print(u"  GRUEN  ein Ziel im Repo wird abgelehnt")
            erwischt += 1

        # (e) Die Fassung von vor dem 17.09.2026: abspath statt realpath+normcase.
        #     Genau so stand es hier, bis `website-security` es gefunden hat.
        def alte_zielpruefung(ziel):
            z = os.path.abspath(ziel)
            r = os.path.abspath(fs.WURZEL)
            return not (z == r or z.startswith(r + os.sep))

        gross = os.path.join(fs.WURZEL.upper(), "backups")
        alt_laesst_durch = alte_zielpruefung(gross)
        try:
            bk.ziel_pruefen(gross)
            neu_laesst_durch = True
        except fs.ZugangFehler:
            neu_laesst_durch = False
        if alt_laesst_durch and not neu_laesst_durch:
            print(u"  GRUEN  die alte Pfadpruefung (abspath) faellt ueber die Schreibweise,")
            print(u"         die neue (realpath+normcase) nicht")
            erwischt += 1
        elif not alt_laesst_durch:
            # Auf einem Dateisystem, das Gross-/Kleinschreibung unterscheidet, ist der
            # Fall gegenstandslos - dann ist der Pfad wirklich ein anderer.
            print(u"  n.z.   Gross-/Kleinschreibung ist hier bedeutungstragend,")
            print(u"         der Windows-Fall laesst sich so nicht nachstellen")
            erwischt += 1
        else:
            print(u"  ROT    auch die neue Pfadpruefung laesst die Schreibweise durch")

        # (g) Die Fassung von vor dem 17.09.2026: zehn juengste Staende bleiben unabhaengig
        #     vom Alter. Sie sieht harmlos aus und hebelt die 90-Tage-Zusage aus.
        tmpg = tempfile.mkdtemp(prefix="pm-backup-gegen-")
        try:
            jetztg = datetime.datetime(2026, 9, 17, 12, 0)
            for i in range(12):
                tag = jetztg - datetime.timedelta(days=400 - i * 30)
                os.makedirs(os.path.join(tmpg, tag.strftime("%Y-%m-%d-%H%M")))
            bk.alte_raeumen(tmpg, mindestens=10, jetzt=jetztg)      # die alte Regel
            alt_uebrig = bk.staende(tmpg)
            alt_zu_alt = [n for n in alt_uebrig[:-1]
                          if (jetztg - bk._datum_aus(n)).days > 90]
            if alt_zu_alt:
                print(u"  GRUEN  die alte Aufbewahrung (10 Staende) laesst %d Stand/Staende"
                      % len(alt_zu_alt))
                print(u"         ueber 90 Tage stehen - die neue Regel nicht")
                erwischt += 1
            else:
                print(u"  ROT    die alte Aufbewahrung faellt hier nicht auf")
        finally:
            shutil.rmtree(tmpg, ignore_errors=True)

        # (f) Eine Fassung, die Pfade aus der Datei ungeprueft uebernimmt.
        roher_pfad = u"users/abc/x?currentDocument.exists=false&y="
        if not fs.pfad_ok(roher_pfad):
            print(u"  GRUEN  ein praeparierter Dokumentpfad wird abgewiesen")
            erwischt += 1
        else:
            print(u"  ROT    ein praeparierter Dokumentpfad kaeme durch")

        print(u"")
        print(u"GEGENPROBE %d von 7 bekannten Fehlern bemerkt" % erwischt)
        if erwischt < 7:
            return 2

    return 1 if rot[0] else 0


if __name__ == "__main__":
    sys.exit(main())
