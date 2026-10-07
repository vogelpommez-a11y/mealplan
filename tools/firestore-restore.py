#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""Spielt eine Sicherung zurueck nach Firestore - standardmaessig nur als Trockenlauf.

Warum es dieses Skript gibt
---------------------------
Art. 32 DSGVO verlangt Wiederherstellbarkeit, nicht Kopien. Eine Sicherung, die niemand
zurueckspielen kann, erfuellt die Pflicht nicht - und im Ernstfall, unter Druck, ist eine
Handarbeit in der Firebase-Konsole der schlechteste Zeitpunkt zum Nachdenken.

Warum der Trockenlauf die VOREINSTELLUNG ist
--------------------------------------------
Ein Rueckspiel zur falschen Zeit macht mehr kaputt, als es rettet: Es ueberschreibt alles,
was seit der Sicherung entstanden ist. Deshalb zeigt das Skript zuerst nur, WAS es taete,
und schreibt erst mit `--schreiben` plus Rueckfrage.

Drei Zusagen, die das Skript einhaelt
-------------------------------------
* **Es loescht nie ein Dokument.** Was live steht, aber nicht in der Sicherung, wird
  gemeldet und bleibt stehen. Ein Konto, das nach der Sicherung angelegt wurde, darf ein
  Rueckspiel nicht kosten.
* **Ein Dokument wird exakt auf den Stand der Sicherung gesetzt**, auch in den Feldern:
  Was live ein Feld mehr hat, verliert es. Sonst entstuende eine Mischung aus zwei Staenden,
  die es nie gab - und die niemand mehr auseinandersortieren kann.
* **Es belebt kein geloeschtes Konto wieder** (Art. 17 DSGVO). Vor dem Schreiben fragt es
  Firebase Auth, welche betroffenen Konten noch bestehen. Daten eines Kontos, das es nicht
  mehr gibt, werden uebersprungen und gemeldet - auch bei `--nur users/<uid>`. Scheitert
  die Abfrage, wird NICHTS geschrieben: Im Zweifel verweigern, nicht raten. Bis zum
  30.09.2026 war das nur eine organisatorische Zusage (Befund `anwalt`).
  Ausnahme nur mit `--auch-geloeschte` - etwa wenn ein Konto versehentlich geloescht wurde
  und die Person ausdruecklich um Wiederherstellung bittet.

Der Normalfall ist NICHT die ganze Datenbank
--------------------------------------------
Der realistische Notfall ist ein einzelnes Konto, das seine Meals verloren hat. Dafuer ist
`--nur users/<uid>` da. Alles zurueckzuspielen ist die Ausnahme, nicht die Regel.

Aufruf:
    python tools/firestore-restore.py --stand 2026-09-17-1430
        Trockenlauf ueber ALLES - zeigt nur an, schreibt nichts.
    python tools/firestore-restore.py --stand 2026-09-17-1430 --nur users/abc123
        Trockenlauf fuer EIN Konto samt seinen Rezepten. Der Normalfall.
    python tools/firestore-restore.py --stand 2026-09-17-1430 --nur users/abc123 --schreiben
        Spielt wirklich zurueck - mit Rueckfrage.

Weitere Schalter:
    --ziel <Ordner>   anderer Ablageort (Standard: Mealplan-Backups neben dem Projekt)
    --ja              ueberspringt die Rueckfrage bei --schreiben. Gedacht fuer den Fall,
                      dass niemand an der Tastatur sitzt - im Notfall lieber bestaetigen.
    --auch-geloeschte schreibt auch Daten von Konten zurueck, die es nicht mehr gibt.
                      Nur auf ausdruecklichen Wunsch der betroffenen Person.

Rueckgabewert: 0 in Ordnung, 1 Abbruch mit Meldung.
"""
import io
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import firestore_api as fs

WURZEL = fs.WURZEL
STANDARD_ZIEL = os.path.join(os.path.dirname(WURZEL), "Mealplan-Backups")


def lade_stand(ordner):
    u"""Liest einen Sicherungsordner und liefert {pfad: felder}.

    **Die Datei ist eine Eingabe, kein Befehl.** Sie liegt zwar lokal, kann aber von einem
    Stick kommen, aus einem synchronisierten Ordner oder von jemandem, der im Ernstfall
    "die Sicherung" weiterreicht. Jeder Schluessel wandert in eine Request-URL - ein Pfad
    wie `users/abc/x?currentDocument.exists=false&y=` haette die `updateMask` verschluckt
    und damit ein ganzes Dokument ersetzt statt einzelner Felder. Deshalb wird hier
    geprueft, und zwar bevor irgendetwas mit den Daten passiert.
    """
    if not os.path.isdir(ordner):
        raise fs.ZugangFehler(u"Diesen Stand gibt es nicht:\n    %s" % ordner)
    alles = {}
    dateien = [n for n in sorted(os.listdir(ordner))
               if n.endswith(".json") and n != "manifest.json"]
    if not dateien:
        raise fs.ZugangFehler(u"In diesem Ordner liegt keine einzige Sammlung:\n    %s" % ordner)
    for name in dateien:
        with io.open(os.path.join(ordner, name), encoding="utf-8") as f:
            inhalt = json.load(f)
        if not isinstance(inhalt, dict):
            raise fs.ZugangFehler(u"%s enthaelt kein Verzeichnis von Dokumenten." % name)
        for pfad, felder in inhalt.items():
            if not fs.pfad_ok(pfad):
                raise fs.ZugangFehler(
                    u"In %s steht ein Dokumentpfad, der so nicht von Firestore stammen kann:\n"
                    u"    %r\n"
                    u"Die Sicherung wird NICHT verwendet. Ein solcher Pfad kann beim Schreiben\n"
                    u"etwas anderes treffen, als er vorgibt - das ist kein Formfehler."
                    % (name, pfad[:200]))
            if not isinstance(felder, dict):
                raise fs.ZugangFehler(
                    u"In %s hat %s keine Feldliste." % (name, pfad))
            alles[pfad] = felder
    return alles


def gefiltert(alles, nur):
    u"""Beschraenkt auf einen Pfad und alles darunter.

    'users/abc' trifft das Dokument selbst UND 'users/abc/recipes/r1' - die Rezepte eines
    Kontos sind genau das, was man zurueckhaben will, wenn man das Konto nennt.
    """
    if not nur:
        return dict(alles)
    return {p: f for p, f in alles.items() if p == nur or p.startswith(nur + "/")}


def vergleiche(sicherung, live):
    u"""Stellt Sicherung und Live-Stand gegenueber.

    Liefert (plan, extras):
        plan   Liste (pfad, art, zu_leerende_felder) mit art aus neu/abweichend/gleich
        extras Pfade, die live stehen und nicht in der Sicherung - werden NIE angefasst
    """
    plan = []
    for pfad in sorted(sicherung):
        felder = sicherung[pfad]
        if pfad not in live:
            plan.append((pfad, "neu", []))
            continue
        jetzt = live[pfad]
        if jetzt == felder:
            plan.append((pfad, "gleich", []))
        else:
            zu_leeren = sorted(set(jetzt.keys()) - set(felder.keys()))
            plan.append((pfad, "abweichend", zu_leeren))
    extras = sorted(p for p in live if p not in sicherung)
    return plan, extras


def hole_live(zugang, sicherung, nur):
    u"""Den Live-Stand besorgen - gezielt bei --nur, sonst den ganzen Baum.

    Ohne Filter lohnt der Komplettabruf doppelt: Er ist billiger als tausend Einzelabrufe
    und er ist die einzige Art, die Extras ueberhaupt zu sehen.
    """
    if not nur:
        return zugang.alles()
    live = {}
    for pfad in sorted(sicherung):
        d = zugang.dokument(pfad)
        if d is not None:
            live[pfad] = d.get("fields", {})
    return live


def zu_tun(plan):
    u"""Nur die Dokumente, die wirklich einen Schreibvorgang kosten."""
    return [(p, a, z) for p, a, z in plan if a != "gleich"]


def konto_von(pfad, felder):
    u"""Wem gehoert dieses Dokument? Liefert die UID oder None (kein Personenbezug im Pfad).

    users/<uid>/...  entitlements/<uid>  loeschsperren/<uid>  groups/<gid>/members/<uid>
    und shared/<id> - dort steht der Eigentuemer nicht im Pfad, sondern im Feld `uid` -,
    invites/<code> ueber das Feld `by` (seit 01.10.2026: Eine Einladung eines geloeschten
    Kontos waere nach dem Rueckspiel wieder ein gueltiger Link).
    Gruppen-Meals und -Plaene gehoeren der Gruppe; die UIDs darin raeumt tote_entfernen().
    """
    t = pfad.split("/")
    if t[0] in ("users", "entitlements", "loeschsperren") and len(t) >= 2:
        return t[1]
    if t[0] == "groups" and len(t) >= 4 and t[2] == "members":
        return t[3]
    if t[0] == "shared":
        return ((felder or {}).get("uid") or {}).get("stringValue") or None
    if t[0] == "invites":
        return ((felder or {}).get("by") or {}).get("stringValue") or None
    return None


def _gruppeninhalt(pfad):
    t = pfad.split("/")
    return len(t) == 4 and t[0] == "groups" and t[2] in ("recipes", "plans")


def uids_im_inhalt(pfad, felder):
    u"""Alle UIDs in einem Gruppen-Meal oder -Plan: `by` und die `uids` der Planeintraege."""
    if not _gruppeninhalt(pfad):
        return set()
    raus = set()
    by = ((felder or {}).get("by") or {}).get("stringValue")
    if by:
        raus.add(by)
    for v in (felder or {}).values():
        for e in ((v or {}).get("arrayValue") or {}).get("values") or []:
            f = (e.get("mapValue") or {}).get("fields") or {}
            for u in ((f.get("uids") or {}).get("arrayValue") or {}).get("values") or []:
                if u.get("stringValue"):
                    raus.add(u["stringValue"])
    return raus


def tote_entfernen(pfad, felder, lebend):
    u"""Gruppen-Meal/-Plan ohne die UIDs geloeschter Konten - wie die App beim Austritt.

    Ohne das schriebe ein Gruppen-Rueckspiel die Kennung eines geloeschten Kontos zurueck in
    die Gruppe (Rechtspruefung 01.10.2026; Ziffer 10: "ohne Hinweis darauf, von wem es
    stammt"). Gesperrt wird das Dokument NICHT - es gehoert der Gruppe, nicht dem Konto.
    Dieselben Regeln wie anonymizeMyRecipes()/anonymizeMyPlanAssignments() in index.html:
      by: <tot>              -> by: ""
      {id, uids:[tot, x]}    -> {id, uids:[x]}
      {id, uids:[tot]}       -> faellt heraus (wie in der App seit 07.10.2026; vorher "id",
                                also "fuer alle" - die Woche des Geloeschten landete bei allen)
    Liefert (felder, geaendert?). Die Eingabe bleibt unveraendert.
    """
    if not _gruppeninhalt(pfad) or not felder:
        return felder, False
    neu = copy.deepcopy(felder)
    geaendert = False
    by = (neu.get("by") or {}).get("stringValue")
    if by and by not in lebend:
        neu["by"] = {"stringValue": ""}
        geaendert = True
    for name, v in neu.items():
        werte = ((v or {}).get("arrayValue") or {}).get("values")
        if not werte:
            continue
        behalten = []
        for e in werte:
            f = (e.get("mapValue") or {}).get("fields") or {}
            uids = ((f.get("uids") or {}).get("arrayValue") or {}).get("values")
            if uids is None:
                behalten.append(e)
                continue
            rest = [u for u in uids if u.get("stringValue") in lebend]
            if len(rest) == len(uids):
                behalten.append(e)
                continue
            geaendert = True
            if rest:
                f["uids"] = {"arrayValue": {"values": rest}}
                behalten.append(e)
        werte[:] = behalten
    return neu, geaendert


def tote_aus_gruppen(plan, sicherung, lebend):
    u"""Wendet tote_entfernen() auf alle zu schreibenden Gruppen-Dokumente an.

    Liefert (neue_sicherung, Zahl bereinigter Dokumente). Die Sicherung auf der Platte
    bleibt unberuehrt - geschrieben wird aus der bereinigten Kopie.
    """
    neu = dict(sicherung)
    n = 0
    for pfad, art, _ in plan:
        if art == "gleich":
            continue
        f, g = tote_entfernen(pfad, sicherung.get(pfad), lebend)
        if g:
            neu[pfad] = f
            n += 1
    return neu, n


def bestehende_konten(zugang, uids):
    u"""Fragt Firebase Auth, welche dieser UIDs noch ein Konto haben.

    Eigener Aufruf statt zugang.roh(): Die Auth-Schnittstelle will mit Nutzer-Zugangsdaten
    ein Kontingent-Projekt im Kopf (x-goog-user-project), und roh() meldet Fehler als
    Firestore-Fehler. Wirft ZugangFehler - der Aufrufer schreibt dann gar nichts.
    """
    import urllib.request, urllib.error
    uids = sorted(set(u for u in uids if u))
    lebend = set()
    for i in range(0, len(uids), 100):
        teil = uids[i:i + 100]
        url = ("https://identitytoolkit.googleapis.com/v1/projects/%s/accounts:lookup"
               % zugang.projekt)
        anfrage = urllib.request.Request(url, data=json.dumps({"localId": teil}).encode("utf-8"),
                                         method="POST")
        anfrage.add_header("Authorization", "Bearer " + zugang.token())
        anfrage.add_header("Content-Type", "application/json")
        anfrage.add_header("x-goog-user-project", zugang.projekt)
        try:
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                daten = json.loads(antwort.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            raise fs.ZugangFehler(
                u"Firebase Auth verweigert die Kontenpruefung (HTTP %d):\n%s\n"
                u"Ohne diese Pruefung wird nichts geschrieben - sonst koennte ein geloeschtes\n"
                u"Konto zurueckkommen." % (e.code, e.read().decode("utf-8", "replace")[:400]))
        except urllib.error.URLError as e:
            raise fs.ZugangFehler(u"Keine Verbindung zu Firebase Auth: %s" % e.reason)
        lebend.update(u.get("localId") for u in daten.get("users", []))
    return lebend


def sperre_geloeschte(plan, sicherung, lebend):
    u"""Nimmt aus dem Plan alles heraus, was einem nicht mehr bestehenden Konto gehoert.

    Liefert (plan_ohne, gesperrt). Unveraenderte Dokumente bleiben im Plan - sie kosten
    keinen Schreibvorgang und belegen nichts.
    """
    ohne, gesperrt = [], []
    for pfad, art, zu_leeren in plan:
        uid = konto_von(pfad, sicherung.get(pfad))
        if art != "gleich" and uid and uid not in lebend:
            gesperrt.append((pfad, uid))
        else:
            ohne.append((pfad, art, zu_leeren))
    return ohne, gesperrt


def spiele_zurueck(zugang, sicherung, plan, melder=None):
    u"""Schreibt den Plan und liefert die Zahl der geschriebenen Dokumente.

    Bricht eine Schreibung ab, bleibt der Rest unveraendert - der Aufruf ist wiederholbar,
    weil jedes Dokument fuer sich gesetzt wird und nicht auf den anderen aufbaut.
    """
    offen = zu_tun(plan)
    n = 0
    for pfad, _art, zu_leeren in offen:
        zugang.schreibe(pfad, sicherung[pfad], auch_leeren=zu_leeren)
        n += 1
        if melder and n % 25 == 0:
            melder(u"  %d/%d geschrieben ..." % (n, len(offen)))
    return n


def main():
    if "--stand" not in sys.argv:
        print(__doc__)
        print(u"ABBRUCH: --stand fehlt. Vorhandene Staende siehe %s" % STANDARD_ZIEL)
        return 1

    schreiben = "--schreiben" in sys.argv
    ohne_rueckfrage = "--ja" in sys.argv
    auch_geloeschte = "--auch-geloeschte" in sys.argv

    print(u"Firestore-Rueckspielung - Paddy's Mealplan")
    print(u"=" * 62)
    try:
        stand = fs.arg(sys.argv, "--stand")
        ziel = fs.arg(sys.argv, "--ziel", STANDARD_ZIEL)
        nur = fs.arg(sys.argv, "--nur")
        ordner = stand if os.path.isdir(stand) else os.path.join(ziel, stand)
        sicherung = gefiltert(lade_stand(ordner), nur)
        if not sicherung:
            print(u"ABBRUCH: In diesem Stand gibt es nichts unter '%s'." % nur)
            return 1
        zugang = fs.Zugang()
        print(u"Stand:   %s" % ordner)
        print(u"Projekt: %s" % zugang.projekt)
        print(u"Umfang:  %d Dokumente%s" % (len(sicherung), (u" unter " + nur) if nur else u" (ALLES)"))
        print(u"")
        live = hole_live(zugang, sicherung, nur)
        plan, extras = vergleiche(sicherung, live)
        gesperrt = []
        if not auch_geloeschte:
            betroffen = [konto_von(p, sicherung.get(p)) for p, a, _ in plan if a != "gleich"]
            for p, a, _ in plan:
                if a != "gleich":
                    betroffen.extend(uids_im_inhalt(p, sicherung.get(p)))
            if any(betroffen):
                lebend = bestehende_konten(zugang, betroffen)
                plan, gesperrt = sperre_geloeschte(plan, sicherung, lebend)
                sicherung, bereinigt = tote_aus_gruppen(plan, sicherung, lebend)
                if bereinigt:
                    print(u"BEREINIGT: %d Gruppen-Dokument(e) ohne die Kennung geloeschter Konten."
                          % bereinigt)
                    print(u"")
    except fs.ZugangFehler as e:
        print(u"")
        print(u"ABBRUCH: %s" % e)
        return 1

    if gesperrt:
        konten = sorted(set(u for _, u in gesperrt))
        print(u"GESPERRT: %d Dokumente gehoeren %d Konto/Konten, die es nicht mehr gibt."
              % (len(gesperrt), len(konten)))
        print(u"  Sie werden NICHT zurueckgespielt (Art. 17 DSGVO). Ausnahme: --auch-geloeschte")
        for pfad, _ in gesperrt[:10]:
            print(u"  GESPERRT     %s" % pfad)
        if len(gesperrt) > 10:
            print(u"  ... und %d weitere" % (len(gesperrt) - 10))
        print(u"")
    elif auch_geloeschte:
        print(u"--auch-geloeschte ist gesetzt: Konten werden NICHT auf Bestand geprueft.")
        print(u"")

    zaehler = {"neu": 0, "abweichend": 0, "gleich": 0}
    for pfad, art, _ in plan:
        zaehler[art] += 1

    print(u"Was ein Rueckspiel taete:")
    print(u"  %4d Dokumente kaemen ZURUECK (fehlen live)" % zaehler["neu"])
    print(u"  %4d Dokumente wuerden UEBERSCHRIEBEN (live anders als in der Sicherung)"
          % zaehler["abweichend"])
    print(u"  %4d Dokumente sind unveraendert - werden nicht angefasst" % zaehler["gleich"])
    if extras:
        print(u"  %4d Dokumente stehen live und NICHT in der Sicherung - bleiben unangetastet"
              % len(extras))

    zeigen = zu_tun(plan)
    if zeigen:
        print(u"")
        print(u"Im Einzelnen (die ersten 40):")
        for pfad, art, zu_leeren in zeigen[:40]:
            zusatz = u"  (Felder fallen weg: %s)" % ", ".join(zu_leeren) if zu_leeren else u""
            print(u"  %-12s %s%s" % (art.upper(), pfad, zusatz))
        if len(zeigen) > 40:
            print(u"  ... und %d weitere" % (len(zeigen) - 40))
    if extras and not nur:
        print(u"")
        print(u"Nur live vorhanden (die ersten 10) - diese bleiben, geloescht wird nie:")
        for pfad in extras[:10]:
            print(u"  BLEIBT       %s" % pfad)

    if not schreiben:
        print(u"")
        print(u"TROCKENLAUF - es wurde nichts geschrieben.")
        print(u"Wirklich zurueckspielen: denselben Aufruf mit --schreiben")
        return 0

    if not zeigen:
        print(u"")
        print(u"Nichts zu tun - der Live-Stand entspricht der Sicherung.")
        return 0

    print(u"")
    if ohne_rueckfrage:
        # --ja darf nicht stumm wirken: Wer die Rueckfrage vermisst, soll SEHEN, warum sie
        # ausbleibt - sonst haelt er das Ausbleiben fuer einen Fehler und startet neu.
        print(u"--ja ist gesetzt: %d Dokumente werden OHNE Rueckfrage ueberschrieben."
              % len(zeigen))
    else:
        print(u"%d Dokumente werden jetzt ueberschrieben. Das ist nicht rueckgaengig zu machen."
              % len(zeigen))
        try:
            antwort = input(u"Zum Bestaetigen 'ja' eingeben: ").strip().lower()
        except EOFError:
            antwort = ""
        if antwort != "ja":
            print(u"Abgebrochen - nichts geschrieben.")
            return 1

    try:
        n = spiele_zurueck(zugang, sicherung, plan, melder=print)
    except fs.ZugangFehler as e:
        print(u"")
        print(u"ABBRUCH nach %d von %d Dokumenten: %s"
              % (zugang.geschrieben, len(zeigen), e))
        print(u"Der Rest steht unveraendert - der Aufruf ist wiederholbar.")
        return 1

    print(u"")
    print(u"Zurueckgespielt: %d Dokumente." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
