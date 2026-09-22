# -*- coding: utf-8 -*-
u"""Findet Konten, die seit 24 Monaten niemand mehr benutzt hat.

Ein Konto, das niemand mehr oeffnet, speichert trotzdem weiter: Ernaehrungsprofil,
Gewichtsverlauf, Wochenplaene. Art. 5 Abs. 1 lit. e DSGVO verlangt, dass personen-
bezogene Daten nicht laenger aufbewahrt werden als noetig - "solange das Konto besteht"
ist dafuer nur dann eine Frist, wenn ein verwaistes Konto irgendwann endet.

**Entscheidung vom 22.09.2026:** 24 Monate ohne Anmeldung, dann eine Vorwarnung per
E-Mail, 30 Tage spaeter die Loeschung.

WAS DIESES SKRIPT TUT - UND WAS NICHT
-------------------------------------
Es **meldet**. Es versendet nichts und es loescht nichts.

Der Grund ist nicht Bequemlichkeit, sondern der Tarif: Ein automatischer Versand
braeuchte eine Cloud Function und damit Blaze, und den gibt es in diesem Projekt
bewusst nicht (Gewerbe-Frage, Stand 19.09.2026). Ohne Blaze bleibt der Versand ein
Handgriff bei der Wartung - und das Loeschen erst recht. Ein Werkzeug, das
eigenmaechtig fremde Konten entfernt, soll es hier nicht geben.

Damit die Frist trotzdem nachweisbar laeuft, fuehrt das Skript den Warnstand: wer wann
gewarnt wurde: `{uid: {"gewarnt": datum}}` - **keine E-Mail-Adressen**, nur die
Kennung und ein Datum. Er liegt trotzdem bei den Sicherungen und NICHT im Repo: Eine
UID ist personenbezogen, und alles im Repo wird oeffentlich (CLAUDE.md 13).

    python tools/konten-inaktiv.py                 # Bericht
    python tools/konten-inaktiv.py --gewarnt UID   # Vorwarnung verschickt, Frist laeuft
    python tools/konten-inaktiv.py --klartext      # mit E-Mail-Adressen (zum Anschreiben)

Ohne `--klartext` stehen die Adressen verkuerzt da. Das ist Absicht: Der Normalfall ist
ein Blick auf die Zahlen, und dabei muss niemandes Adresse ueber den Schirm laufen.
"""
import datetime
import io
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import firestore_api as F  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Gleicher Ort wie die Sicherungen (firestore-backup.py) - bewusst ausserhalb des Repos.
WARNSTAND = os.path.join(os.path.dirname(WURZEL), "Mealplan-Backups", "inaktive-konten.json")

INAKTIV_TAGE = 730    # 24 Monate
GNADE_TAGE = 30       # zwischen Vorwarnung und Loeschung


def konten(z, pid):
    u"""Alle Auth-Konten, ueber alle Seiten.

    Der Header `x-goog-user-project` ist noetig, weil das Token aus `gcloud auth login`
    stammt (Nutzer-Anmeldung, keine Dienstkennung) - ohne ihn antwortet die API mit 403
    und dem Hinweis auf das fehlende Kontingentprojekt.
    """
    raus, token = [], None
    while True:
        url = ("https://identitytoolkit.googleapis.com/v1/projects/%s/accounts:batchGet"
               "?maxResults=500" % pid)
        if token:
            url += "&nextPageToken=" + token
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + z.token())
        req.add_header("x-goog-user-project", pid)
        antwort = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
        raus += antwort.get("users", [])
        token = antwort.get("nextPageToken")
        if not token:
            return raus


def letzter_kontakt(u):
    u"""Millisekunden des letzten Lebenszeichens.

    `lastLoginAt` fehlt bei einem Konto, das nie benutzt wurde - dann zaehlt die
    Anlage. Ohne diesen Rueckfall waere ausgerechnet das leere Konto von der Frist
    ausgenommen.
    """
    for feld in ("lastRefreshAt", "lastLoginAt", "createdAt"):
        wert = u.get(feld)
        if not wert:
            continue
        try:
            if isinstance(wert, str) and "T" in wert:   # lastRefreshAt ist ISO
                t = datetime.datetime.strptime(wert[:19], "%Y-%m-%dT%H:%M:%S")
                return int(t.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
            return int(wert)
        except (TypeError, ValueError):
            continue
    return None


def einstufen(nutzer, stand, jetzt_ms, heute):
    u"""In welchem Zustand ist dieses Konto?

    Eigene Funktion, damit sie pruefbar ist: Steckt die Einstufung in main(), laesst sie
    sich nur mit echten Konten pruefen - und die sind alle aktiv. Ein Werkzeug, das
    "nichts zu tun" meldet, weil es gar nichts erkennt, saehe genauso aus wie eines,
    das richtig liegt (tools/pruefstand-konten-inaktiv.py).

    Liefert (zustand, tage_still, tage_seit_warnung). Zustand ist einer von:
    "aktiv", "warnen", "wartend", "loeschen" - oder "unbekannt", wenn das Konto
    keinen einzigen Zeitstempel traegt.
    """
    ms = letzter_kontakt(nutzer)
    if ms is None:
        return (u"unbekannt", None, None)
    tage = (jetzt_ms - ms) // 86400000
    if tage < INAKTIV_TAGE:
        return (u"aktiv", tage, None)
    vermerk = stand.get(nutzer.get("localId", ""))
    if not vermerk:
        return (u"warnen", tage, None)
    try:
        gewarnt = datetime.datetime.strptime(
            vermerk["gewarnt"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    except (KeyError, TypeError, ValueError):
        # Ein kaputter Vermerk darf nicht zur Loeschung fuehren - dann lieber neu warnen.
        return (u"warnen", tage, None)
    seit = (heute - gewarnt).days
    return ((u"loeschen" if seit >= GNADE_TAGE else u"wartend"), tage, seit)


def kurz_mail(adresse, klartext):
    if klartext or not adresse or "@" not in adresse:
        return adresse or u"(keine E-Mail)"
    name, _, rest = adresse.partition("@")
    return u"%s***@%s" % (name[:2], rest)


def warnstand_lesen():
    try:
        return json.loads(io.open(WARNSTAND, encoding="utf-8").read())
    except Exception:
        return {}


def warnstand_schreiben(daten):
    ordner = os.path.dirname(WARNSTAND)
    if not os.path.isdir(ordner):
        os.makedirs(ordner)
    io.open(WARNSTAND, "w", encoding="utf-8").write(
        json.dumps(daten, indent=2, ensure_ascii=False))


def main(argv):
    klartext = "--klartext" in argv
    gewarnt_neu = []
    if "--gewarnt" in argv:
        i = argv.index("--gewarnt")
        gewarnt_neu = [a for a in argv[i + 1:] if not a.startswith("--")]

    heute = datetime.datetime.now(datetime.timezone.utc)
    jetzt_ms = int(heute.timestamp() * 1000)
    stand = warnstand_lesen()

    if gewarnt_neu:
        for uid in gewarnt_neu:
            stand[uid] = {"gewarnt": heute.strftime("%Y-%m-%d")}
        warnstand_schreiben(stand)
        print(u"Vormerkung gesetzt fuer %d Konto/Konten. Die 30 Tage laufen ab heute."
              % len(gewarnt_neu))
        print(u"Ablage: %s" % WARNSTAND)
        return 0

    try:
        z = F.Zugang()
        pid = F.projekt_id()
        alle = konten(z, pid)
    except Exception as e:
        print(u"Kein Zugang zur Auth-API: %s" % e)
        print(u"  Nach  gcloud auth login  erneut versuchen.")
        return 2

    warnen, loeschen, wartend, aktiv = [], [], [], 0
    for u in alle:
        zustand, tage, seit = einstufen(u, stand, jetzt_ms, heute)
        if zustand == u"aktiv":
            aktiv += 1
            continue
        if zustand == u"unbekannt":
            continue
        eintrag = (u.get("localId", ""), kurz_mail(u.get("email"), klartext), tage)
        if zustand == u"warnen":
            warnen.append(eintrag)
        elif zustand == u"wartend":
            wartend.append(eintrag + (seit,))
        else:
            loeschen.append(eintrag + (seit,))

    print(u"Konten gesamt: %d" % len(alle))
    print(u"  aktiv (in den letzten 24 Monaten angemeldet): %d" % aktiv)
    print(u"  seit ueber 24 Monaten still:                  %d"
          % (len(warnen) + len(wartend) + len(loeschen)))

    if warnen:
        print(u"\nZU WARNEN (%d) - Vorwarnung verschicken, dann --gewarnt setzen:" % len(warnen))
        for uid, mail, tage in warnen:
            print(u"  * %s  %s  (%d Tage still)" % (uid, mail, tage))
        print(u"\n  Danach:  python tools/konten-inaktiv.py --gewarnt %s"
              % u" ".join(u for u, _, _ in warnen[:3]))
        if not klartext:
            print(u"  Adressen im Klartext:  python tools/konten-inaktiv.py --klartext")

    if wartend:
        print(u"\nFRIST LAEUFT (%d) - gewarnt, aber die 30 Tage sind noch nicht um:" % len(wartend))
        for uid, mail, tage, seit in wartend:
            print(u"  * %s  %s  (gewarnt vor %d Tagen)" % (uid, mail, seit))

    if loeschen:
        print(u"\nZU LOESCHEN (%d) - gewarnt und 30 Tage verstrichen:" % len(loeschen))
        for uid, mail, tage, seit in loeschen:
            print(u"  * %s  %s  (%d Tage still, gewarnt vor %d Tagen)" % (uid, mail, tage, seit))
        print(u"\n  Dieses Skript loescht NICHT. Weg: Firebase-Konsole -> Authentication,")
        print(u"  dazu die Daten unter users/{uid} samt Unterkollektion (docs/RUNBOOK.md).")
        print(u"  Vorher sichern:  python tools/firestore-backup.py")

    if not (warnen or wartend or loeschen):
        print(u"\nNichts zu tun - kein Konto ist ueber die Frist hinaus still.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
