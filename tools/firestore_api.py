# -*- coding: utf-8 -*-
u"""Zugang zu Firestore fuer Sicherung und Rueckspielung - nur Standardbibliothek.

Warum es dieses Modul gibt
--------------------------
`tools/firestore-backup.py` und `tools/firestore-restore.py` brauchen dieselben drei Dinge:
einen Ausweis, einen Weg zur REST-Schnittstelle und die Kenntnis, wie Firestore Dokumente
benennt. Zweimal geschrieben waeren sie zweimal zu pflegen - und die Sicherung wuerde
irgendwann etwas anderes lesen, als die Rueckspielung schreibt.

Kein pip, kein google-cloud-firestore: Das Projekt hat bewusst keine Toolchain
(CLAUDE.md Abschnitt 9), und `urllib` aus der Standardbibliothek reicht fuer REST.

Der Ausweis
-----------
Das Token kommt aus `gcloud auth print-access-token` und lebt rund eine Stunde. Bewusst
KEIN Dienstkonto-Schluessel als Datei: Der laege dauerhaft auf der Platte und oeffnete jedem,
der ihn kopiert, saemtliche Nutzerdaten. Es gibt in diesem Projekt genau zwei echte
Geheimnisse (CLAUDE.md Abschnitt 12), und dabei soll es bleiben.

Das Rohformat bleibt roh
------------------------
Gesichert wird die `fields`-Struktur, wie die Schnittstelle sie liefert - nicht in
Python-Werte umgerechnet. Firestore unterscheidet `integerValue` von `doubleValue`,
kennt Zeitstempel, Bytes und Verweise; JSON kennt davon nichts. Eine Umrechnung waere
huebscher zu lesen und beim Zurueckschreiben falsch: Aus einer 1 wuerde eine 1.0, aus einem
Zeitstempel eine Zeichenkette. Ein Backup, das anders zurueckkommt, als es hineinging, ist
kein Backup.
"""
import io
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = "https://firestore.googleapis.com/v1"

# Feldnamen, die in einer updateMask nackt stehen duerfen. Alles andere braucht Backticks.
EINFACHER_NAME = re.compile(r"^[A-Za-z_][A-Za-z_0-9]*$")

# Ein Dokumentpfad, wie Firestore ihn vergibt: Segmente aus Buchstaben, Ziffern und
# -_.~ , getrennt durch Schraegstriche. Bewusst eng: Der Pfad kommt beim Rueckspielen aus
# einer Datei, und alles, was hier durchrutscht, landet in einer URL.
PFAD_MUSTER = re.compile(r"^[A-Za-z0-9_.~-]+(?:/[A-Za-z0-9_.~-]+)*$")


def pfad_ok(pfad):
    u"""Ist das ein unverdaechtiger Firestore-Dokumentpfad?

    Abgelehnt werden `?`, `#`, `:`, Leerzeichen, Steuerzeichen, Prozentkodierung, leere
    Segmente und jedes `.`/`..` als ganzes Segment. Ein Dokumentpfad hat ausserdem eine
    GERADE Zahl von Segmenten (Sammlung/Dokument/Sammlung/Dokument ...) - eine ungerade
    waere eine Sammlung und als Ziel eines Schreibvorgangs sinnlos.
    """
    if not isinstance(pfad, str) or not PFAD_MUSTER.match(pfad):
        return False
    teile = pfad.split("/")
    if any(t in (".", "..") for t in teile):
        return False
    # Firestore begrenzt einen Dokumentnamen auf 1500 Byte je Segment und den ganzen Pfad
    # auf rund 6 KiB. Was darueber liegt, kann kein echter Pfad sein - billig mitgenommen.
    if len(pfad) > 6144 or any(len(t) > 1500 for t in teile):
        return False
    return len(teile) % 2 == 0

HILFE_ANMELDUNG = u"""

Dafuer fehlt die Anmeldung. Einmalig einrichten:

    winget install Google.CloudSDK
    gcloud auth login
    gcloud config set project paddys-mealplan

Danach laeuft dieses Skript ohne weitere Eingabe - das Token holt es sich selbst.
"""


class ZugangFehler(Exception):
    u"""Alles, was den Zugang zu Firestore verhindert - mit einer Meldung fuer Menschen."""


def projekt_id():
    u"""Die Projekt-ID aus index.html lesen, nicht hier hartkodieren.

    Sie steht in der Firebase-Konfiguration und ist kein Geheimnis (CLAUDE.md Abschnitt 12).
    Zweimal gepflegt waere sie einmal falsch - und eine Sicherung gegen das falsche Projekt
    meldet froehlich Erfolg, waehrend sie nichts findet.
    """
    pfad = os.path.join(WURZEL, "index.html")
    with io.open(pfad, encoding="utf-8") as f:
        for zeile in f:
            treffer = re.search(r'projectId:\s*"([^"]+)"', zeile)
            if treffer:
                return treffer.group(1)
    raise ZugangFehler(u"In index.html steht keine projectId - stimmt der Projektordner?")


class Zugang(object):
    u"""Spricht mit der Firestore-REST-Schnittstelle.

    Der Transport steckt allein in `roh()`. Der Pruefstand setzt eine Unterklasse ein und
    prueft damit die ganze Mechanik, ohne die echte Datenbank auch nur anzufassen - Proben
    gehoeren nie an die Cloud echter Nutzer (siehe docs/TESTING.md, Cloud-Falle).
    """

    def __init__(self, projekt=None, token=None):
        self.projekt = projekt or projekt_id()
        self._token = token
        self.gelesen = 0
        self.geschrieben = 0

    # -- Ausweis ---------------------------------------------------------------
    def token(self):
        if self._token:
            return self._token
        gcloud = shutil.which("gcloud")
        if not gcloud:
            raise ZugangFehler(u"gcloud ist nicht installiert." + HILFE_ANMELDUNG)
        try:
            roh = subprocess.check_output([gcloud, "auth", "print-access-token"],
                                          stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            melde = e.output.decode("utf-8", "replace").strip()
            raise ZugangFehler(u"gcloud konnte kein Token ausstellen:\n%s%s"
                               % (melde, HILFE_ANMELDUNG))
        self._token = roh.decode("utf-8", "replace").strip()
        if not self._token:
            raise ZugangFehler(u"gcloud lieferte ein leeres Token." + HILFE_ANMELDUNG)
        return self._token

    # -- Transport -------------------------------------------------------------
    def roh(self, methode, url, rumpf=None):
        u"""Ein Aufruf an die Schnittstelle. Die EINZIGE Stelle, die wirklich ins Netz geht."""
        daten = json.dumps(rumpf).encode("utf-8") if rumpf is not None else None
        anfrage = urllib.request.Request(url, data=daten, method=methode)
        anfrage.add_header("Authorization", "Bearer " + self.token())
        anfrage.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                text = antwort.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace")
            if e.code in (401, 403):
                raise ZugangFehler(
                    u"Firestore verweigert den Zugriff (HTTP %d).\n%s\n"
                    u"Das Konto braucht die Rolle 'Cloud Datastore-Nutzer' oder 'Inhaber'.%s"
                    % (e.code, text[:400], HILFE_ANMELDUNG))
            raise ZugangFehler(u"Firestore antwortete mit HTTP %d:\n%s" % (e.code, text[:800]))
        except urllib.error.URLError as e:
            raise ZugangFehler(u"Keine Verbindung zu Firestore: %s" % e.reason)
        return json.loads(text) if text.strip() else {}

    # -- Pfade -----------------------------------------------------------------
    def _url(self, pfad=""):
        u"""Baut die URL - jedes Pfadsegment einzeln kodiert.

        Der Pfad kann aus einer Sicherungsdatei stammen, also aus einer Datei, die jemand
        angefasst haben kann. Roh verkettet wuerde ein Segment wie
        `x?currentDocument.exists=false&y=` den Query-String kapern und das nachgestellte
        `updateMask` verschlucken - und ein PATCH OHNE updateMask ersetzt in Firestore das
        ganze Dokument statt einzelner Felder. `pfad_ok()` faengt das schon beim Laden ab;
        die Kodierung hier ist die zweite Schicht, direkt an der Leitung.
        """
        basis = "%s/projects/%s/databases/(default)/documents" % (BASIS, self.projekt)
        if not pfad:
            return basis
        teile = [urllib.parse.quote(t, safe="") for t in pfad.split("/")]
        return basis + "/" + "/".join(teile)

    def kurz(self, voller_name):
        u"""'projects/P/databases/(default)/documents/users/abc' -> 'users/abc'."""
        marke = "/documents/"
        i = voller_name.find(marke)
        return voller_name[i + len(marke):] if i >= 0 else voller_name

    # -- Lesen -----------------------------------------------------------------
    def sammlungen(self, doku_pfad=""):
        u"""Welche Sammlungen liegen unter der Wurzel bzw. unter einem Dokument?

        BEWUSST erfragt statt hier aufgelistet: Eine Liste im Code kennt nur die Sammlungen
        von heute. Kaeme in einem halben Jahr eine neue dazu, sicherte das Skript sie nicht -
        und meldete trotzdem Erfolg. Genau diese Art von Luecke beschreibt CLAUDE.md 18b.
        """
        antwort = self.roh("POST", self._url(doku_pfad) + ":listCollectionIds",
                           {"pageSize": 300})
        return sorted(antwort.get("collectionIds", []))

    def dokumente(self, sammlung):
        u"""Alle Dokumente einer Sammlung, ueber alle Seiten hinweg."""
        raus = []
        seite = None
        while True:
            url = self._url(sammlung) + "?pageSize=300"
            if seite:
                url += "&pageToken=" + urllib.parse.quote(seite)
            antwort = self.roh("GET", url)
            for d in antwort.get("documents", []):
                self.gelesen += 1
                raus.append(d)
            seite = antwort.get("nextPageToken")
            if not seite:
                return raus

    def dokument(self, pfad):
        u"""Ein einzelnes Dokument, oder None wenn es nicht existiert."""
        try:
            return self.roh("GET", self._url(pfad))
        except ZugangFehler as e:
            if "HTTP 404" in str(e):
                return None
            raise

    def alles(self, melder=None):
        u"""Laeuft den ganzen Baum ab und liefert {pfad: felder}.

        Unterkollektionen werden mitgenommen: In diesem Projekt haengen an `users/{uid}` die
        Rezepte und an `groups/{gid}` Mitglieder, Plaene und Rezepte. Wer nur die Wurzel
        sichert, sichert die halbe App.
        """
        raus = {}

        def ab(sammlung):
            if melder:
                melder(sammlung)
            for d in self.dokumente(sammlung):
                pfad = self.kurz(d.get("name", ""))
                raus[pfad] = d.get("fields", {})
                for unter in self.sammlungen(pfad):
                    ab(pfad + "/" + unter)

        for s in self.sammlungen():
            ab(s)
        return raus

    # -- Schreiben -------------------------------------------------------------
    def schreibe(self, pfad, felder, auch_leeren=None):
        u"""Setzt ein Dokument auf genau diese Felder.

        `auch_leeren` nennt zusaetzliche Feldnamen, die in der Maske stehen, aber nicht im
        Rumpf - die raeumt Firestore dadurch weg. So entsteht wirklich der Stand des Backups
        und nicht eine Mischung aus alt und neu.
        """
        namen = sorted(set(list(felder.keys()) + list(auch_leeren or [])))
        maske = "&".join("updateMask.fieldPaths=" + urllib.parse.quote(_maskenname(n))
                         for n in namen)
        url = self._url(pfad) + ("?" + maske if maske else "")
        self.roh("PATCH", url, {"fields": felder})
        self.geschrieben += 1


def arg(argv, name, standard=None, zahl=False):
    u"""Liest `--name WERT` aus argv - mit einer Meldung statt eines Absturzes.

    `sys.argv[i + 1]` ohne Pruefung wirft einen IndexError, und `int()` auf Unsinn einen
    ValueError. Beides endet in einem Python-Stacktrace. Diese Werkzeuge laufen im Notfall,
    wenn Daten weg sind und jemand unter Druck steht - da ist ein Stacktrace die schlechteste
    aller Antworten. (Befund des Agenten `kvp`, 17.09.2026.)
    """
    if name not in argv:
        return standard
    i = argv.index(name)
    if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
        raise ZugangFehler(u"Zu %s fehlt der Wert." % name)
    wert = argv[i + 1]
    if not zahl:
        return wert
    try:
        return int(wert)
    except ValueError:
        raise ZugangFehler(u"%s erwartet eine Zahl, bekommen hat es: %r" % (name, wert))


def _maskenname(name):
    u"""Feldnamen in einer updateMask: alles ausser schlichten Bezeichnern braucht Backticks."""
    if EINFACHER_NAME.match(name):
        return name
    escaped = name.replace("\\", "\\\\").replace("`", "\\`")
    return "`" + escaped + "`"
