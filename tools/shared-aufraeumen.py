# -*- coding: utf-8 -*-
u"""Entfernt abgelaufene Teilen-Links aus `shared/`.

Ein Teilen-Link lebt 12 Monate (Entscheidung 22.09.2026, Art.-30-Verzeichnis V5).
Die Frist selbst steckt in den Firestore-Regeln (`shareFrisch`): Nach 12 Monaten
laesst sich der Snapshot nicht mehr lesen, auch nicht mit den Entwicklerwerkzeugen.

**Die Regel macht den Link unlesbar - sie loescht ihn nicht.** Unlesbar ist keine
Loeschung: Die Daten liegen weiter in Firestore, und Ziffer 10 der Datenschutz-
erklaerung sagt zu, dass sie weggeraeumt werden. Genau das tut dieses Skript.

Es laeuft ueber die Admin-Schnittstelle (`gcloud auth print-access-token`) und
umgeht die Regeln damit bewusst - `list` auf `shared/` ist fuer Angemeldete
gesperrt, und das soll so bleiben.

    python tools/shared-aufraeumen.py              # Trockenlauf, loescht nichts
    python tools/shared-aufraeumen.py --wirklich   # loescht

Ohne `--wirklich` wird nichts angefasst. Das ist Absicht: Ein Werkzeug, das beim
ersten Tippfehler Daten entfernt, wird irgendwann im falschen Moment getippt.
"""
import io
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import firestore_api as F  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Dieselbe Zahl wie SHARE_TTL_MS in index.html und shareFrisch() in firestore.rules.
# Laufen die drei je auseinander, sagt die Oberflaeche etwas anderes als die Regel und
# dieses Skript raeumt nach einer dritten Frist. tools/pruefstand-share-frist.py haelt
# sie gegeneinander.
TTL_MS = 31536000000  # 365 Tage


def when_von(dok):
    u"""Liest `when` aus einem Firestore-Rohdokument - oder None.

    Ein Snapshot ohne `when` stammt aus der Zeit vor der Frist. Er wird NICHT geloescht:
    Ohne Datum laesst sich nicht sagen, ob er abgelaufen ist, und Raten waere hier ein
    Datenverlust. Die Regeln lassen solche Dokumente aus demselben Grund weiter lesen.
    """
    feld = (dok.get("fields") or {}).get("when") or {}
    roh = feld.get("integerValue")
    if roh is None:
        return None
    try:
        return int(roh)
    except (TypeError, ValueError):
        return None


def main(argv):
    wirklich = "--wirklich" in argv
    jetzt = int(time.time() * 1000)
    grenze = jetzt - TTL_MS

    try:
        db = F.Zugang()
        dokumente = db.dokumente("shared")
    except F.ZugangFehler as e:
        print(u"Kein Zugang: %s" % e)
        return 2

    abgelaufen, ohne_datum, frisch = [], 0, 0
    for d in dokumente:
        w = when_von(d)
        if w is None:
            ohne_datum += 1
        elif w < grenze:
            abgelaufen.append(d)
        else:
            frisch += 1

    print(u"Teilen-Links in shared/:  %d" % len(dokumente))
    print(u"  frisch (< 12 Monate):   %d" % frisch)
    print(u"  ohne Datum (Altbestand): %d  - bleiben liegen, siehe when_von()" % ohne_datum)
    print(u"  abgelaufen:             %d" % len(abgelaufen))

    if not abgelaufen:
        print(u"\nNichts zu tun.")
        return 0

    if not wirklich:
        print(u"\nTrockenlauf - es wurde nichts geloescht.")
        print(u"Zum Loeschen:  python tools/shared-aufraeumen.py --wirklich")
        return 0

    weg, fehler = 0, []
    for d in abgelaufen:
        pfad = db.kurz(d["name"])
        try:
            db.loesche(pfad, d.get("updateTime"))
            weg += 1
        except Exception as e:
            fehler.append((pfad, str(e)))

    print(u"\nGeloescht: %d" % weg)
    if fehler:
        print(u"Nicht geloescht: %d" % len(fehler))
        for pfad, meldung in fehler[:10]:
            print(u"  * %s: %s" % (pfad, meldung))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
