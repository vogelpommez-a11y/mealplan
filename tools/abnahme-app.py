# -*- coding: utf-8 -*-
u"""
Geraeteabnahme in der ECHTEN Android-App - dieselben Stationen wie tools/abnahme-mobil.py.

Warum es dieses Werkzeug gibt: abnahme-mobil.py emuliert ein Handy in Chrome. Die App im
Store ist aber eine Android-WebView in der Capacitor-Huelle - mit echtem Bildschirm, echter
Statusleiste, echtem Dunkelmodus des Systems und eigener Engine-Version. Was nur dort
anders ist, sieht keine Emulation (Entscheidung Paddy, 25.10.2026: "A2").

Wie: Der Debug-Build legt einen Socket webview_devtools_remote_<pid> an (siehe
tools/webview-js.py im App-Repo). Den leiten wir per adb auf einen lokalen Port und steuern
die App mit GENAU dem Code der Browser-Abnahme: Onboarding, vier Reiter, drei Fenster,
dieselbe Messung (MESSEN), derselbe Bericht. Nur Start, Laden und Theme sind ersetzt:

  * Theme   -> Dunkelmodus des Systems (cmd uimode night), KEINE Emulation. Ob die App ihn
               mitbekommt, wird vor dem Lauf geprueft - sonst misst Dunkel das helle Bild.
  * Laden   -> App-Daten loeschen (pm clear) und neu starten. Das ist zugleich die
               Cloud-Falle aus docs/TESTING.md: frische App, nur lokal, nie ein Konto.
  * Geraet  -> der Emulator, wie er ist. Eine Groesse; die Breiten deckt abnahme-mobil.py ab.

  python tools/abnahme-app.py                # baut die App, Hell + Dunkel
  python tools/abnahme-app.py --ohne-bauen   # installierte App pruefen (schneller)
  python tools/abnahme-app.py --theme dark
  python tools/abnahme-app.py --gegenprobe   # misst sich selbst, in der App

Laeuft nur vor Store-Abgaben (docs/TESTING.md 2g), nicht im Alltag.
Braucht: Android-SDK mit Emulator (AVD) und das App-Repo daneben (../Paddys Mealplan App).
"""
import argparse, importlib.util, json, os, subprocess, sys, time, urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_REPO = os.path.join(os.path.dirname(WURZEL), "Paddys Mealplan App")
PAKET = "de.paddysmealplan.app"
# Nicht 9343 (tools/webview-js.py im App-Repo) und nicht 9333 (Edge der Pruefstaende):
# eine liegengebliebene adb-Weiterleitung liess am 24.10.2026 zwei Pruefstaende rot werden.
PORT = 9344
SCHUESSE = os.path.join(os.environ.get("TEMP", "."), "mp-abnahme-app")

# Die Browser-Abnahme hat einen Bindestrich im Namen - laden statt importieren.
_spec = importlib.util.spec_from_file_location("abnahme_mobil", os.path.join(WURZEL, "tools", "abnahme-mobil.py"))
am = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(am)
am.SCHUESSE = SCHUESSE   # eigene Bilder, die Browser-Bilder bleiben Bezug fuer deren Vergleich


def sdk():
    for kandidat in (os.environ.get("ANDROID_HOME"),
                     os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk"),
                     os.path.expanduser("~/Library/Android/sdk")):
        if kandidat and os.path.isdir(kandidat):
            return kandidat
    raise SystemExit("Android-SDK nicht gefunden. Android Studio einmal einrichten.")


EXE = ".exe" if os.name == "nt" else ""
ADB = os.path.join(sdk(), "platform-tools", "adb" + EXE)


def adb(*args, pruefen=True):
    r = subprocess.run([ADB] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if pruefen and r.returncode:
        raise RuntimeError("adb %s: %s" % (" ".join(args), (r.stderr or r.stdout).strip()))
    return r.stdout


def emulator_sicherstellen():
    if "\tdevice" in adb("devices"):
        return
    emu = os.path.join(sdk(), "emulator", "emulator" + EXE)
    avds = subprocess.run([emu, "-list-avds"], capture_output=True, text=True).stdout.split()
    if not avds:
        raise SystemExit("Kein Test-Handy (AVD) angelegt - in Android Studio unter Device Manager.")
    print("Starte Emulator", avds[0])
    subprocess.Popen([emu, "-avd", avds[0], "-no-snapshot-save", "-no-boot-anim"],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    adb("wait-for-device")
    for _ in range(180):
        if adb("shell", "getprop", "sys.boot_completed", pruefen=False).strip() == "1":
            return
        time.sleep(1)
    raise SystemExit("Emulator nicht hochgefahren (3 min).")


def app_bauen():
    u"""Baut und installiert den aktuellen Stand der Web-App - sonst prueft man die App von gestern."""
    skript = os.path.join(APP_REPO, "tools", "app-bauen.py")
    if not os.path.isfile(skript):
        raise SystemExit("App-Repo nicht gefunden: %s" % APP_REPO)
    print("Baue die App (web-kopieren, cap sync, gradle) ...")
    r = subprocess.run([sys.executable, skript, "--ohne-start"], cwd=APP_REPO)
    if r.returncode:
        raise SystemExit("Bauen fehlgeschlagen (Exit %d)." % r.returncode)
    apk = os.path.join(APP_REPO, "android", "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    adb("install", "-r", apk)


class AppSitzung(am.Sitzung):
    u"""Sitzung der Browser-Abnahme, aber gegen die WebView der App statt gegen Chrome."""

    def __init__(self):
        am.Sitzung.__init__(self)
        self.theme = None

    def _seiten(self):
        with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT, timeout=5) as r:
            return [t for t in json.loads(r.read().decode("utf-8")) if t.get("type") == "page"]

    def start(self, frisch=True):
        emulator_sicherstellen()
        if PAKET not in adb("shell", "pm", "list", "packages", PAKET):
            raise SystemExit("Die App ist nicht installiert - ohne --ohne-bauen starten.")
        # lauf() spricht schon vor laden() mit der Seite - also gleich einmal starten.
        adb("shell", "monkey", "-p", PAKET, "-c", "android.intent.category.LAUNCHER", "1")
        self.verbinden()

    def verbinden(self):
        u"""Socket der laufenden App suchen, weiterleiten, verbinden. Nach jedem Neustart
        neu: die pid und damit der Socketname wechseln."""
        import websocket
        pid = ""
        for _ in range(40):
            pid = adb("shell", "pidof", PAKET, pruefen=False).strip()
            if pid and ("webview_devtools_remote_%s" % pid) in adb("shell", "cat", "/proc/net/unix"):
                break
            time.sleep(0.5)
        else:
            raise SystemExit(u"ABBRUCH - keine debugbare WebView der App (pid %r).\n"
                             u"  Nur Debug-Builds oeffnen sie - ohne --ohne-bauen neu bauen." % pid)
        adb("forward", "tcp:%d" % PORT, "localabstract:webview_devtools_remote_%s" % pid)
        for _ in range(40):
            try:
                seiten = self._seiten()
                if seiten:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        else:
            raise SystemExit("ABBRUCH - die WebView meldet keine Seite.")
        self.ws = websocket.create_connection(seiten[0]["webSocketDebuggerUrl"], timeout=90,
                                              suppress_origin=True)
        self.senden("Page.enable")

    def stoppen(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        adb("forward", "--remove", "tcp:%d" % PORT, pruefen=False)
        if self.theme:   # das Handy so hinterlassen, wie man es kennt
            adb("shell", "cmd", "uimode", "night", "auto", pruefen=False)

    def geraet(self, breite, hoehe, theme):
        u"""Breite und Hoehe gibt der Emulator vor - nur das Theme wird gesetzt, systemweit."""
        self.theme = theme
        adb("shell", "cmd", "uimode", "night", "yes" if theme == "dark" else "no")

    def laden(self):
        u"""Frische App: Daten weg, neu starten, Startbildschirm abwarten."""
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        self.ws = None
        adb("shell", "am", "force-stop", PAKET)
        adb("shell", "pm", "clear", PAKET)
        adb("shell", "monkey", "-p", PAKET, "-c", "android.intent.category.LAUNCHER", "1")
        self.verbinden()
        for _ in range(80):
            time.sleep(0.25)
            try:
                if self.js("document.readyState") == "complete":
                    break
            except Exception:
                continue
        for _ in range(64):
            try:
                if not self.js("!!document.getElementById('splash')"):
                    break
            except Exception:
                pass
            time.sleep(0.25)
        self.bild_abwarten()
        self.messgrundlage_pruefen()
        self.theme_pruefen()

    def theme_pruefen(self):
        u"""Bekommt die WebView den Dunkelmodus des Systems mit? Wenn nicht, misst der
        Dunkel-Lauf das helle Bild und meldet trotzdem gruen - das darf nicht still passieren."""
        if not self.theme:
            return
        dunkel = self.js("matchMedia('(prefers-color-scheme: dark)').matches")
        if dunkel != (self.theme == "dark"):
            raise SystemExit(u"ABBRUCH - System steht auf %s, die App sieht prefers-color-scheme: %s.\n"
                             u"  Dann misst dieser Lauf das falsche Theme." % (
                                 self.theme, "dark" if dunkel else "light"))


def main():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--ohne-bauen", action="store_true", help="installierte App pruefen")
    p.add_argument("--theme", choices=["light", "dark"], help="ohne Angabe beide")
    p.add_argument("--gegenprobe", action="store_true", help="misst sich selbst, in der App")
    a = p.parse_args()

    emulator_sicherstellen()
    if not a.ohne_bauen:
        app_bauen()
    s = AppSitzung()
    s.start()
    try:
        if a.gegenprobe:
            return am.gegenprobe(s)
        groesse = adb("shell", "wm", "size").strip().split()[-1]
        print("Echte App im Emulator, Bildschirm %s" % groesse)
        alle = []
        for theme in ([a.theme] if a.theme else ["dark", "light"]):
            erg = am.lauf(s, 0, 0, theme, "android")
            alle += erg
            print("--- android-%s: %d Stationen, %d Befunde" % (
                theme, len(erg), sum(am.zaehle(m) for m in erg)))

        print("\n" + "=" * 74)
        anzahl = am.bericht(alle)
        print("\nBilder: %s" % SCHUESSE)
        if am.UNBEKANNTE_FELDER:
            print("\nROT - das Onboarding verlangt Felder, die abnahme-mobil.py nicht kennt:")
            for feld in sorted(am.UNBEKANNTE_FELDER):
                print("  * %s" % feld)
            return 1
        if anzahl:
            print("\nROT - %d Ursache(n) in %d Stationen." % (anzahl, len(alle)))
            return 1
        print("\nGRUEN - %d Stationen ohne Befund." % len(alle))
        return 0
    finally:
        s.stoppen()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
