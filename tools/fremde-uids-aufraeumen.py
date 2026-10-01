# -*- coding: utf-8 -*-
u"""Entfernt Kennungen ANDERER Personen aus Altdaten (Rechtspruefung 01.10.2026, 🔴 1).

Ziffer 10 sagt zu: Beim Austritt und bei der Kontoloeschung bleibt "das Gericht - ohne Hinweis
darauf, von wem es stammt". Bis 01.10.2026 galt das nur in groups/{gid}. Seitdem bereinigt die
App die Kopie beim Austritt selbst und raeumt alte Kopien beim naechsten Start auf
(ohneFremdbezug() in index.html, TROUBLESHOOTING §183). Wer die App nie wieder oeffnet, und alte
Teilen-Links, erreicht das nicht - dafuer ist dieses Skript.

Was es anfasst (und nur das):
  users/{uid}             nur wenn KEIN groupId gesetzt ist:
                          * plans: Eintraege {id, uids} -> mir zugewiesen: String-Form,
                            nur anderen: entfaellt; {id} ohne uids -> String-Form
                          * recipes (Altfeld vor dem Subcollection-Umbau): `by` raus
  users/{uid}/recipes/*   nur wenn KEIN groupId gesetzt ist: `by` raus
  shared/{id}             * recipes[].by raus (das obere Feld `by` ist der Anzeigename des
                            Absenders und bleibt - den hat er selbst geteilt)
                          * plan (Wochenplan-Links bis 02.08.2026): {id, uids} -> String-Form.
                            Hier wird nichts weggelassen: Der Link zeigt einen Plan zum
                            Uebernehmen, der Empfaenger plant ihn fuer sich.
Mitglieder einer aktiven Gruppe bleiben unberuehrt: Dort traegt `by`/`uids` eine Funktion.

Gearbeitet wird direkt auf den typisierten Firestore-Werten, ohne Umweg ueber Python-Objekte -
sonst wuerden aus integerValue unterwegs doubleValue und umgekehrt. Geschrieben wird nur mit
der Vorbedingung `currentDocument.updateTime`: Hat die App das Dokument seit dem Lesen
geaendert, lehnt Firestore ab, und der naechste Lauf entscheidet neu.

    python tools/fremde-uids-aufraeumen.py              # Trockenlauf, schreibt nichts
    python tools/fremde-uids-aufraeumen.py --schreiben  # schreibt (vorher sichern!)
    python tools/fremde-uids-aufraeumen.py --selbsttest # ohne Netz, mit Gegenprobe

Vor --schreiben: python tools/firestore-backup.py
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# --------------------------------------------------------------------- reine Logik
def _felder(v):
    return ((v or {}).get("mapValue") or {}).get("fields")


def _werte(v):
    return ((v or {}).get("arrayValue") or {}).get("values")


def rezept_ohne_by(v):
    u"""mapValue eines Meals -> (neuer Wert, geaendert?)."""
    f = _felder(v)
    if not f or "by" not in f:
        return v, False
    neu = copy.deepcopy(v)
    del neu["mapValue"]["fields"]["by"]
    return neu, True


def rezepte_ohne_by(v):
    u"""arrayValue von Meals -> (neuer Wert, Anzahl entfernter by)."""
    werte = _werte(v)
    if not werte:
        return v, 0
    neu, n = [], 0
    for w in werte:
        w2, g = rezept_ohne_by(w)
        neu.append(w2)
        n += 1 if g else 0
    if not n:
        return v, 0
    return {"arrayValue": {"values": neu}}, n


def eintrag(e, uid):
    u"""Ein Planeintrag -> neuer Eintrag oder None (faellt weg).

    uid=None heisst: niemand faellt weg, uids werden nur abgestreift (Teilen-Links).
    Dieselbe Regel wie ohneFremdbezug() in index.html.
    """
    f = _felder(e)
    if f is None:
        return e
    eid = f.get("id")
    if not eid or "stringValue" not in eid:
        return e        # unbekannte Form - nicht anfassen, die App normalisiert selbst
    uids = f.get("uids")
    if uids is None or uid is None:
        return {"stringValue": eid["stringValue"]}
    liste = [u.get("stringValue") for u in (_werte(uids) or [])]
    return {"stringValue": eid["stringValue"]} if uid in liste else None


def woche(v, uid):
    u"""mapValue einer Woche (Tag -> Mahlzeit -> Liste) -> (neuer Wert, Anzahl Aenderungen)."""
    tage = _felder(v)
    if not tage:
        return v, 0
    neu = copy.deepcopy(v)
    n = 0
    for tag, tv in tage.items():
        mz = _felder(tv)
        if not mz:
            continue
        for m, liste in mz.items():
            werte = _werte(liste)
            if not werte:
                continue
            raus = []
            for e in werte:
                e2 = eintrag(e, uid)
                if e2 is not e:
                    n += 1
                if e2 is not None:
                    raus.append(e2)
            if raus != werte:
                ziel = neu["mapValue"]["fields"][tag]["mapValue"]["fields"]
                ziel[m] = {"arrayValue": {"values": raus}} if raus else {"arrayValue": {}}
    return (neu, n) if n else (v, 0)


def plaene(v, uid):
    u"""Feld `plans` (Woche -> Woche) -> (neuer Wert, Anzahl Aenderungen)."""
    wochen = _felder(v)
    if not wochen:
        return v, 0
    neu = copy.deepcopy(v)
    n = 0
    for wk, wv in wochen.items():
        w2, k = woche(wv, uid)
        if k:
            neu["mapValue"]["fields"][wk] = w2
            n += k
    return (neu, n) if n else (v, 0)


def konto(felder, uid):
    u"""Felder von users/{uid} -> (Aenderungen {feld: wert}, Anzahl) - leer bei Gruppe."""
    gid = (felder.get("groupId") or {}).get("stringValue") or ""
    if gid:
        return {}, 0
    aend, n = {}, 0
    if "plans" in felder:
        p, k = plaene(felder["plans"], uid)
        if k:
            aend["plans"], n = p, n + k
    if "recipes" in felder:
        r, k = rezepte_ohne_by(felder["recipes"])
        if k:
            aend["recipes"], n = r, n + k
    return aend, n


def geteilt(felder):
    u"""Felder von shared/{id} -> (Aenderungen, Anzahl)."""
    aend, n = {}, 0
    if "recipes" in felder:
        r, k = rezepte_ohne_by(felder["recipes"])
        if k:
            aend["recipes"], n = r, n + k
    if "plan" in felder:
        w, k = woche(felder["plan"], None)
        if k:
            aend["plan"], n = w, n + k
    return aend, n


# --------------------------------------------------------------------- Selbsttest
def _s(x):
    return {"stringValue": x}


def _m(**f):
    return {"mapValue": {"fields": f}}


def _a(*w):
    return {"arrayValue": {"values": list(w)}}


def selbsttest(eintrag_fn=None):
    u"""Prueft die reine Logik ohne Netz. Liefert Liste der Fehlschlaege."""
    global eintrag
    echt = eintrag
    if eintrag_fn:
        eintrag = eintrag_fn
    try:
        f = []
        ich, b = "uid-ich", "uid-b"
        wk = _m(mon=_m(breakfast=_a(_s("m3"), _m(id=_s("m1"), uids=_a(_s(ich), _s(b))),
                                     _m(id=_s("m2"), uids=_a(_s(b))), _m(id=_s("m9")))))
        kontofelder = {"plans": _m(**{"2026-W40": wk}),
                       "recipes": _a(_m(id=_s("m1"), by=_s(b), kcal={"integerValue": "500"})),
                       "goal": _m(kcal={"integerValue": "1950"})}
        a, n = konto(copy.deepcopy(kontofelder), ich)
        liste = a["plans"]["mapValue"]["fields"]["2026-W40"]["mapValue"]["fields"]["mon"]["mapValue"]["fields"]["breakfast"]
        if json.dumps(liste) != json.dumps(_a(_s("m3"), _s("m1"), _s("m9"))):
            f.append("Konto: Slot falsch bereinigt: %s" % json.dumps(liste))
        if "by" in json.dumps(a.get("recipes")):
            f.append("Konto: by im Altfeld recipes nicht entfernt")
        if '"integerValue": "500"' not in json.dumps(a.get("recipes")):
            f.append("Konto: integerValue nicht erhalten")
        if "goal" in a:
            f.append("Konto: unbeteiligtes Feld goal wuerde geschrieben")
        g = dict(kontofelder, groupId=_s("g1"))
        if konto(g, ich)[1] != 0:
            f.append("Konto in Gruppe wurde angefasst")
        sauber = {"plans": a["plans"], "recipes": a["recipes"]}
        if konto(sauber, ich)[1] != 0:
            f.append("Zweiter Lauf auf bereinigtem Stand aendert noch etwas")
        sh = {"by": _s("Paddy"), "recipes": _a(_m(id=_s("m1"), by=_s(b))),
              "plan": wk}
        a2, _ = geteilt(copy.deepcopy(sh))
        if "by" in json.dumps(a2.get("recipes")):
            f.append("Teilen: recipes[].by nicht entfernt")
        if "by" in a2:
            f.append("Teilen: oberes Feld by (Absendername) wuerde angefasst")
        sl = a2["plan"]["mapValue"]["fields"]["mon"]["mapValue"]["fields"]["breakfast"]
        if json.dumps(sl) != json.dumps(_a(_s("m3"), _s("m1"), _s("m2"), _s("m9"))):
            f.append("Teilen: plan falsch bereinigt: %s" % json.dumps(sl))
        return f
    finally:
        eintrag = echt


def main_selbsttest():
    f = selbsttest()
    for x in f:
        print(u"  FEHL  " + x)
    print(u"Selbsttest: %s" % ("gruen" if not f else "%d Fehler" % len(f)))
    # Gegenprobe: eine Fassung, die nur abstreift statt wegzulassen, MUSS durchfallen.
    def kaputt(e, uid):
        fe = _felder(e)
        return {"stringValue": fe["id"]["stringValue"]} if fe and "id" in fe else e
    g = selbsttest(kaputt)
    print(u"Gegenprobe (fremde Eintraege nicht weglassen): %s"
          % ("faellt durch - gut" if g else "BESTEHT - der Selbsttest misst nichts"))
    return 0 if (not f and g) else 1


def ohne_pfade(text):
    u"""Ersetzt Firestore-Dokumentpfade (und damit UIDs) in Fehlertexten durch {pfad}."""
    import re
    return re.sub(r"projects/[^\s\"',]+", "{pfad}", text)


# --------------------------------------------------------------------- Lauf
def main(argv):
    if "--selbsttest" in argv:
        return main_selbsttest()
    import firestore_api as F
    schreiben = "--schreiben" in argv
    try:
        db = F.Zugang()
        konten = db.dokumente("users")
        links = db.dokumente("shared")
    except F.ZugangFehler as e:
        print(u"Kein Zugang: %s" % e)
        return 2

    auftraege = []   # (pfad, aenderungen, auch_leeren, update_time, art)
    in_gruppe = 0
    for d in konten:
        pfad = db.kurz(d["name"])
        uid = pfad.split("/")[-1]
        felder = d.get("fields", {})
        if (felder.get("groupId") or {}).get("stringValue"):
            in_gruppe += 1
            continue
        aend, n = konto(felder, uid)
        if n:
            auftraege.append((pfad, aend, [], d.get("updateTime"), "Konto (plans/recipes)"))
        for r in db.dokumente(pfad + "/recipes"):
            by = (r.get("fields", {}).get("by") or {})
            if by:
                art = ("Meal im Konto, fremdes by" if by.get("stringValue") != uid
                       else "Meal im Konto, eigenes by")
                auftraege.append((db.kurz(r["name"]), {}, ["by"], r.get("updateTime"), art))
    for d in links:
        aend, n = geteilt(d.get("fields", {}))
        if n:
            auftraege.append((db.kurz(d["name"]), aend, [], d.get("updateTime"), "Teilen-Link"))

    print(u"Konten: %d (davon in einer Gruppe, unberuehrt: %d) · Teilen-Links: %d"
          % (len(konten), in_gruppe, len(links)))
    arten = {}
    for a in auftraege:
        arten[a[4]] = arten.get(a[4], 0) + 1
    if not auftraege:
        print(u"\nNichts zu tun - keine fremden Kennungen in Altdaten.")
        return 0
    print(u"\nZu bereinigen:")
    for art, n in sorted(arten.items()):
        print(u"  %-24s %d Dokument(e)" % (art, n))
    for a in auftraege[:20]:
        print(u"    %s" % F.Zugang.muster(a[0]))
    if not schreiben:
        print(u"\nTrockenlauf - es wurde nichts geschrieben.")
        print(u"Vorher sichern:  python tools/firestore-backup.py")
        print(u"Dann:            python tools/fremde-uids-aufraeumen.py --schreiben")
        return 0

    ok, fehler = 0, []
    for pfad, aend, leeren, ut, _ in auftraege:
        try:
            db.schreibe(pfad, aend, auch_leeren=leeren, update_time=ut)
            ok += 1
        except Exception as e:
            # Firestore nennt im Fehlertext den vollen Dokumentpfad - mit UID. Maskieren,
            # wie die Pfade oben (Befund website-security 01.10.2026).
            fehler.append((F.Zugang.muster(pfad), ohne_pfade(str(e))[:160]))
    print(u"\nBereinigt: %d" % ok)
    if fehler:
        print(u"Nicht bereinigt (meist inzwischen geaendert - erneut laufen lassen): %d" % len(fehler))
        for p, m in fehler[:10]:
            print(u"  * %s: %s" % (p, m))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
