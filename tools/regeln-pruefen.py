# -*- coding: utf-8 -*-
u"""Prueft die Syntax von `firestore.rules` - OHNE sie zu veroeffentlichen.

Das Gegenstueck zu `tools/regeln-live.py`: Der vergleicht Repo und Live, dieses
Skript beantwortet die Frage davor - *waere die Vorlage ueberhaupt gueltig?*

Warum das noetig ist: Es gibt fuer dieses Projekt **keinen Firestore-Emulator** und
damit keine Moeglichkeit, eine Regel vor dem Scharfschalten auszuprobieren. Ein
Tippfehler in einer `allow`-Zeile faellt sonst erst auf, wenn die Regeln live sind -
und dann sofort bei echten Nutzern. Bei einer verschaerfenden Regel wie `shareFrisch()`
hiesse das: alle Teilen-Links auf einen Schlag tot.

`projects.rulesets.create` legt ein Regelwerk an und validiert es dabei. **Ein Ruleset
ohne Release ist wirkungslos** - es gilt erst, wenn es per `releases.patch` scharf
geschaltet wird, und genau das tut dieses Skript NICHT. Das angelegte Regelwerk wird
danach wieder entfernt.

    python tools/regeln-pruefen.py

Braucht `gcloud auth login`. Rueckgabewert 0 = gueltig, 1 = Syntaxfehler oder kein Zugang.

**Das Veroeffentlichen bleibt Handarbeit in der Firebase-Konsole.** Das ist Absicht und
steht so in `CLAUDE.md` 12: Die Regeln sind die einzige Sicherheitsgrenze, und ein Skript,
das sie im Vorbeigehen scharf schalten kann, ist selbst ein Risiko.
"""
import io, json, os, sys, urllib.request, urllib.error
sys.path.insert(0, os.path.abspath("tools"))
sys.stdout.reconfigure(encoding="utf-8")
import firestore_api as F

z = F.Zugang()
pid = F.projekt_id()
quelle = io.open("firestore.rules", encoding="utf-8").read()

rumpf = {"source": {"files": [{"name": "firestore.rules", "content": quelle}]}}
url = "https://firebaserules.googleapis.com/v1/projects/%s/rulesets" % pid
req = urllib.request.Request(url, data=json.dumps(rumpf).encode("utf-8"), method="POST")
req.add_header("Authorization", "Bearer " + z.token())
req.add_header("Content-Type", "application/json")
req.add_header("x-goog-user-project", pid)
try:
    antwort = json.loads(urllib.request.urlopen(req, timeout=40).read().decode("utf-8"))
    name = antwort.get("name", "")
    print("SYNTAX OK - Regelwerk angelegt (NICHT veroeffentlicht):")
    print("  ", name)
    # Gleich wieder wegraeumen: ein unbenutztes Ruleset braucht niemand.
    d = urllib.request.Request("https://firebaserules.googleapis.com/v1/" + name, method="DELETE")
    d.add_header("Authorization", "Bearer " + z.token())
    d.add_header("x-goog-user-project", pid)
    try:
        urllib.request.urlopen(d, timeout=30)
        print("   wieder entfernt.")
    except Exception as e:
        print("   konnte nicht entfernt werden (harmlos, es ist nicht scharf):", e)
    print("\nDie Regeln sind syntaktisch gueltig. Sie sind damit NICHT live.")
except urllib.error.HTTPError as e:
    roh = e.read().decode("utf-8", "replace")
    print("SYNTAXFEHLER oder kein Zugang (HTTP %s):" % e.code)
    print(roh[:1800])
    sys.exit(1)
