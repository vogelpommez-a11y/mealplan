# -*- coding: utf-8 -*-
u"""Oeffnet die Vergleichsseite in einem EIGENEN Browserprofil - ohne Cloud-Konto.

    python tools/vorfuehren.py dropdown
    python tools/vorfuehren.py                 # Liste der Bausteine
    python tools/vorfuehren.py --app           # nur die App, ohne Vergleich

Warum ein eigenes Profil
------------------------
Im Alltagsbrowser ist ein Cloud-Konto angemeldet. Die Vergleichsseite bricht dort ab, und
das ist richtig so: Sie schreibt einen erfundenen Zustand nach `wochenkueche_v1__test`, und
der `__test`-Suffix trennt nur den LOKALEN Speicher - nicht die Cloud. Die App wuerde den
erfundenen Zustand mit dem echten Konto vereinigen und pushen (passiert am 04.09.2026:
14 erfundene Archivwochen und zwei erfundene Wiegungen in einem echten Konto).

Die Notbremse abzuschalten waere die falsche Antwort. Stattdessen ein eigenes Profil, in
dem nie jemand angemeldet ist - dasselbe Prinzip wie bei `tools/abnahme-mobil.py`, nur
sichtbar statt headless.

Das Profil bleibt zwischen den Laeufen bestehen (Fenstergroesse, Zoom). Wer es zuruecksetzen
will: `--frisch`.

CLAUDE.md Abschnitt 21b: Jede sichtbare Aenderung wird erst vorgefuehrt, dann committet.
"""
import argparse, io, os, re, subprocess, sys, time, urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-vorfuehrung")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASIS = "http://localhost:8000"


def server_laeuft():
    try:
        urllib.request.urlopen(BASIS + "/index.html", timeout=2).read(1)
        return True
    except Exception:
        return False


def server_starten():
    print(u"Der lokale Server laeuft nicht - starte test-server.ps1 ...")
    subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Minimized",
                      "-File", os.path.join(WURZEL, "test-server.ps1")],
                     cwd=WURZEL)
    for _ in range(30):
        time.sleep(0.5)
        if server_laeuft():
            return True
    return False


def bausteine():
    u"""Liest die Kennungen aus der Registry - ohne sie nachzubauen."""
    pfad = os.path.join(WURZEL, "tools", "vergleich-bausteine.js")
    if not os.path.exists(pfad):
        return []
    text = io.open(pfad, encoding="utf-8").read()
    return re.findall(r'^\s*id:\s*"([a-z0-9-]+)"', text, re.M)


def hat_schnappschuss(kennung):
    return os.path.isdir(os.path.join(WURZEL, "tools", "vorher", kennung))


def oeffnen(url, frisch=False):
    if not os.path.exists(CHROME):
        print(u"Chrome nicht gefunden unter %s" % CHROME)
        print(u"Dann von Hand oeffnen: %s" % url)
        return 2
    if frisch and os.path.isdir(PROFIL):
        import shutil
        shutil.rmtree(PROFIL, ignore_errors=True)
    subprocess.Popen([CHROME, "--user-data-dir=" + PROFIL, "--no-first-run",
                      "--no-default-browser-check", "--new-window", url])
    print(u"Geoeffnet in eigenem Profil (kein Konto angemeldet):")
    print(u"  %s" % url)
    return 0


def main():
    p = argparse.ArgumentParser(description=u"Vergleichsseite im eigenen Profil zeigen")
    p.add_argument("baustein", nargs="?", help=u"Kennung, z. B. dropdown")
    p.add_argument("--app", action="store_true", help=u"nur die App oeffnen")
    p.add_argument("--frisch", action="store_true", help=u"Profil vorher zuruecksetzen")
    a = p.parse_args()

    if not server_laeuft() and not server_starten():
        print(u"Server kam nicht hoch. Von Hand:  powershell -NoProfile -File test-server.ps1")
        return 2

    if a.app:
        return oeffnen(BASIS + "/index.html", a.frisch)

    alle = bausteine()
    if not a.baustein:
        print(u"Bausteine in tools/vergleich-bausteine.js:\n")
        for b in alle:
            print(u"  %-18s %s" % (b, u"" if hat_schnappschuss(b) else u"(kein Schnappschuss)"))
        print(u"\n  python tools/vorfuehren.py <kennung>")
        return 0

    if a.baustein not in alle:
        print(u"'%s' steht nicht in der Registry. Bekannt: %s" % (a.baustein, ", ".join(alle)))
        return 2
    if not hat_schnappschuss(a.baustein):
        print(u"Fuer '%s' gibt es keinen Vorher-Stand. Zuerst:" % a.baustein)
        print(u"  python tools/schnappschuss.py %s <git-stand-vor-der-aenderung>" % a.baustein)
        return 2

    return oeffnen(BASIS + "/tools/probe-vergleich.html?baustein=" + a.baustein, a.frisch)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
