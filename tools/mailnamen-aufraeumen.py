# -*- coding: utf-8 -*-
u"""Entfernt den E-Mail-Rueckfall-Namen aus Altdaten (Rechtspruefung 17.10.2026, 🟡 1).

Bis zum 17.10.2026 schrieb die App bei Konten OHNE displayName den Teil der E-Mail-Adresse vor
dem @ als Namen in die Cloud (handleCloudUser() -> profile.name). Ziffer 8a sagt aber: "Nicht
geteilt ... deine E-Mail-Adresse". Seitdem nimmt die App dafuer gruppenName() bzw. ein leeres
`by` (Merker profile.nameAusMail). Neue Daten sind sauber, alte heilen nur zum Teil von selbst:

  groups/{gid}/members/{uid}  `name`  -> heilt beim naechsten Oeffnen in der Gruppe
                                         (syncMyMember) - wer nicht mehr oeffnet, nie
  shared/{id}                 `by`    -> heilt nie: Teilen-Links sind unveraenderlich
                                         (firestore.rules) und bis 12 Monate lesbar

Dieses Skript raeumt beides EINMAL auf. Ob ein Name der E-Mail-Rueckfall ist, entscheidet nicht
eine Vermutung, sondern Firebase Auth: Er ist es genau dann, wenn er gleich dem Teil vor dem @
der hinterlegten Adresse ist und das Konto keinen gleichlautenden displayName traegt (dann
haette der Nutzer ihn selbst so gewaehlt). Ersatz wie in der App: im Mitgliedereintrag
"Mitglied", im Teilen-Link leer (der Empfaenger zeigt "Jemand").

Geschrieben wird nur mit der Vorbedingung `currentDocument.updateTime` (wie
tools/fremde-uids-aufraeumen.py). Ausgaben nennen nie Namen, Adressen oder IDs.

    python tools/mailnamen-aufraeumen.py              # Trockenlauf, schreibt nichts
    python tools/mailnamen-aufraeumen.py --schreiben  # schreibt (vorher sichern!)
    python tools/mailnamen-aufraeumen.py --selbsttest # ohne Netz, mit Gegenprobe

Vor --schreiben: python tools/firestore-backup.py
"""
import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ERSATZ_MITGLIED = u"Mitglied"   # = gruppenName() in index.html
ERSATZ_LINK = u""               # = shareMealPayload(): leer, der Empfaenger zeigt "Jemand"


# --------------------------------------------------------------------- reine Logik
def mailnamen(konten):
    u"""Auth-Konten -> {uid: E-Mail-Rueckfall}, nur fuer Konten, bei denen er greifen konnte."""
    raus = {}
    for u in konten:
        mail = u.get("email") or ""
        vorm = mail.split("@")[0] if "@" in mail else ""
        if not vorm:
            continue
        # Hat der Nutzer genau diesen Namen selbst als displayName, ist es seine Wahl.
        if (u.get("displayName") or "") == vorm:
            continue
        raus[u.get("localId", "")] = vorm
    return raus


def _s(felder, name):
    return ((felder or {}).get(name) or {}).get("stringValue")


def mitglied_ist_mailname(felder, uid, karte):
    u"""groups/{gid}/members/{uid}: traegt `name` den E-Mail-Rueckfall dieses Kontos?"""
    vorm = karte.get(uid)
    return bool(vorm) and _s(felder, "name") == vorm


def link_ist_mailname(felder, karte):
    u"""shared/{id}: traegt `by` den E-Mail-Rueckfall des Absenders (`uid`)?"""
    vorm = karte.get(_s(felder, "uid") or "")
    return bool(vorm) and _s(felder, "by") == vorm


# --------------------------------------------------------------------- Selbsttest
def selbsttest(pruef_mitglied=None, pruef_link=None):
    pm = pruef_mitglied or mitglied_ist_mailname
    pl = pruef_link or link_ist_mailname
    karte = mailnamen([
        {"localId": "a", "email": "anna.k@example.org"},                       # Rueckfall moeglich
        {"localId": "b", "email": "bert@example.org", "displayName": "Bert"},  # heute echter Name
        {"localId": "c", "email": "carla@example.org", "displayName": "carla"},  # selbst gewaehlt
        {"localId": "d"},                                                     # ohne Adresse
    ])
    s = lambda t: {"stringValue": t}
    faelle = [
        # b hat HEUTE einen Namen - frueher, vor dem Setzen, griff der Rueckfall trotzdem.
        ("Karte kennt alle Konten mit moeglichem Rueckfall", sorted(karte) == ["a", "b"]),
        ("alter Rueckfall eines Kontos, das heute einen Namen hat, wird erkannt",
         pm({"name": s("bert")}, "b", karte)),
        ("Mitglied mit Rueckfall-Namen wird erkannt", pm({"name": s("anna.k")}, "a", karte)),
        ("Mitglied mit eigenem Namen bleibt", not pm({"name": s("Anna")}, "a", karte)),
        ("Mitglied 'Mitglied' bleibt (schon sauber)", not pm({"name": s("Mitglied")}, "a", karte)),
        ("gleichlautender Name eines ANDEREN Kontos zaehlt nicht",
         not pm({"name": s("anna.k")}, "b", karte)),
        ("selbst gewaehlter displayName = Teil vor dem @ bleibt",
         not pm({"name": s("carla")}, "c", karte)),
        ("Teilen-Link mit Rueckfall-Absender wird erkannt",
         pl({"uid": s("a"), "by": s("anna.k")}, karte)),
        ("Teilen-Link mit leerem by bleibt", not pl({"uid": s("a"), "by": s("")}, karte)),
        ("Teilen-Link mit echtem Namen bleibt", not pl({"uid": s("b"), "by": s("Bert")}, karte)),
        ("Teilen-Link ohne uid bleibt", not pl({"by": s("anna.k")}, karte)),
    ]
    return faelle


def main_selbsttest():
    faelle = selbsttest()
    for name, ok in faelle:
        print(u"  %s  %s" % ("OK    " if ok else "FEHLER", name))
    # Gegenprobe: Eine Pruefung, die ALLES fuer Rueckfall haelt (oder nichts), muss auffallen.
    gegen_alles = [ok for _, ok in selbsttest(lambda f, u, k: True, lambda f, k: True)]
    gegen_nichts = [ok for _, ok in selbsttest(lambda f, u, k: False, lambda f, k: False)]
    gp = not all(gegen_alles) and not all(gegen_nichts)
    print(u"  %s  GEGENPROBE: zu grosszuegige und zu enge Pruefung fallen beide durch"
          % ("OK    " if gp else "FEHLER"))
    gruen = all(ok for _, ok in faelle) and gp
    print(u"ALLE PRUEFUNGEN GRUEN" if gruen else u"FEHLGESCHLAGEN")
    return 0 if gruen else 1


# --------------------------------------------------------------------- Lauf
def _auth_konten(z, pid):
    u"""Auth-Konten ueber dieselbe Abfrage wie tools/konten-inaktiv.py - nicht doppelt gebaut."""
    pfad = os.path.join(os.path.dirname(os.path.abspath(__file__)), "konten-inaktiv.py")
    spec = importlib.util.spec_from_file_location("konten_inaktiv", pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.konten(z, pid)


def main(argv):
    if "--selbsttest" in argv:
        return main_selbsttest()
    import firestore_api as F
    schreiben = "--schreiben" in argv
    try:
        db = F.Zugang()
        karte = mailnamen(_auth_konten(db, F.projekt_id()))
        gruppen = db.dokumente("groups")
        links = db.dokumente("shared")
    except Exception as e:
        print(u"Kein Zugang: %s" % e)
        print(u"  Nach  gcloud auth login  erneut versuchen.")
        return 2

    auftraege = []   # (pfad, felder, update_time, art)
    mitglieder = 0
    for g in gruppen:
        for m in db.dokumente(db.kurz(g["name"]) + "/members"):
            mitglieder += 1
            pfad = db.kurz(m["name"])
            if mitglied_ist_mailname(m.get("fields", {}), pfad.split("/")[-1], karte):
                auftraege.append((pfad, {"name": {"stringValue": ERSATZ_MITGLIED}},
                                  m.get("updateTime"), "Mitgliedereintrag"))
    for d in links:
        if link_ist_mailname(d.get("fields", {}), karte):
            auftraege.append((db.kurz(d["name"]), {"by": {"stringValue": ERSATZ_LINK}},
                              d.get("updateTime"), "Teilen-Link"))

    print(u"Konten mit moeglichem E-Mail-Rueckfall: %d · Gruppen: %d · Mitgliedereintraege: %d"
          u" · Teilen-Links: %d" % (len(karte), len(gruppen), mitglieder, len(links)))
    if not auftraege:
        print(u"\nNichts zu tun - kein E-Mail-Rueckfall-Name in den Altdaten.")
        return 0
    arten = {}
    for a in auftraege:
        arten[a[3]] = arten.get(a[3], 0) + 1
    print(u"\nZu bereinigen:")
    for art, n in sorted(arten.items()):
        print(u"  %-20s %d Dokument(e)" % (art, n))
    if not schreiben:
        print(u"\nTrockenlauf - es wurde nichts geschrieben.")
        print(u"Vorher sichern:  python tools/firestore-backup.py")
        print(u"Dann:            python tools/mailnamen-aufraeumen.py --schreiben")
        return 0

    ok, fehler = 0, []
    for pfad, felder, ut, _ in auftraege:
        try:
            db.schreibe(pfad, felder, update_time=ut)
            ok += 1
        except Exception as e:
            fehler.append((F.Zugang.muster(pfad), type(e).__name__))
    print(u"\nBereinigt: %d" % ok)
    if fehler:
        print(u"Nicht bereinigt (meist inzwischen geaendert - erneut laufen lassen): %d" % len(fehler))
        for p, m in fehler[:10]:
            print(u"  * %s: %s" % (p, m))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
