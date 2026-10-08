// -*- coding: utf-8 -*-
// Registry der UI-Bausteine fuer tools/probe-vergleich.html.
//
// Klassisches Skript, kein Modul - wie data/ikonen.js. Ueber file:// laeuft sonst nichts.
//
// Je Baustein:
//   id        Ordnername unter tools/vorher/ UND ?baustein=<id> in der URL
//   titel     Ueberschrift in der Probe
//   was       ein Satz: worauf soll man schauen?
//   stellen   die Fundstellen von heute - steht als Mahnung im Kopf der Probe,
//             damit niemand eine davon vergisst (CLAUDE.md Abschnitt 21a)
//   zustand   optionale Ergaenzungen zum Standard-Testzustand
//   oeffnen   stellt den zu vergleichenden Zustand her (Menue aufklappen o. Ae.).
//             Bekommt das Dokument des iframes, NICHT das eigene.
//
// Einen Baustein hinzufuegen heisst: hier einen Eintrag ergaenzen und einmal
//   python tools/schnappschuss.py <id> <alter-stand>
// laufen lassen. Kein neues HTML-Geruest - das ist der Unterschied zu den
// Einzelproben probe-symbole.html/probe-fortschritt.html.

// Zweiergruppe (Paddy + Anna, "Einkauf fuer alle rechnen: An") nachstellen, OHNE dass etwas
// ans Netz geht - wie bei cloud-laden, nur dass load() hier antwortet. Alles, was die App
// sonst noch an CloudSync/CloudGroup fragt (Speichern, Listener, Mitgliedseintrag), faengt
// ein Proxy als stilles Nichts ab: eine Funktion, die zugleich als Promise taugt - Listener
// geben sie als Abmelder zurueck, await liest sie als "erledigt".
// Genutzt von gruppe-fuer-alle und einkauf-minus.
function zweiergruppeNachstellen(w) {
  function nichts() {
    var f = function () {};
    f.then = function (ok) { return w.Promise.resolve(ok ? ok() : undefined); };
    f.catch = function () { return f; };
    f.finally = function (g) { if (g) g(); return f; };
    return f;
  }
  function attrappe(basis) {
    return new w.Proxy(basis, { get: function (t, k) { return k in t ? t[k] : nichts; } });
  }
  var MEAL = { id: "rvgbowl", name: "Hähnchen-Reis-Bowl", category: "Hauptgericht",
    nutrition: { kcal: 540, carbs: 55, protein: 42, fat: 14 },
    ingredients: [{ name: "Hähnchenbrust", grams: 150 }, { name: "Reis", grams: 80 },
                  { name: "Brokkoli", grams: 120 }] };
  // Zwei weitere fuer Durchlaeufe mit vollem Plan: Brokkoli steckt auch in den Nudeln, damit
  // das Zusammenzaehlen derselben Zutat aus verschiedenen Meals mitgeprueft wird.
  var NUDELN = { id: "rvgnudeln", name: "Brokkoli-Nudeln", category: "Hauptgericht",
    nutrition: { kcal: 480, carbs: 70, protein: 20, fat: 10 },
    ingredients: [{ name: "Vollkornnudeln", grams: 100 }, { name: "Tomaten", grams: 200 },
                  { name: "Brokkoli", grams: 60 }] };
  var SHAKE = { id: "rvgshake", name: "Hafer-Shake", category: "Frühstück",
    nutrition: { kcal: 350, carbs: 45, protein: 18, fat: 9 },
    ingredients: [{ name: "Haferflocken", grams: 50 }, { name: "Banane", grams: 120 }] };
  var GOAL = { mode: "cut", kcal: 1950, protein: 150, carbs: 180, fat: 60, activity: "pal14", training: [] };
  w.CloudEntitlement = null;
  w.CloudSync = attrappe({ enabled: true,
    load: function () { return w.Promise.resolve({ groupId: "vg-gruppe", onboarded: true, goal: GOAL }); },
    loadRecipes: function () { return w.Promise.resolve([MEAL, NUDELN, SHAKE]); }
  });
  w.CloudGroup = attrappe({ enabled: true,
    fetch: function () { return w.Promise.resolve({ data: { name: "Wir", settings: { shopForAll: true } }, fromCache: false }); },
    fetchMembers: function () { return w.Promise.resolve({ fromCache: false, members: [
      { uid: "vergleich", name: "Paddy", role: "owner" }, { uid: "vg-anna", name: "Anna", role: "edit" }] }); },
    loadPlans: function () { return w.Promise.resolve([]); }
  });
  w.__onCloudAuth({ uid: "vergleich", emailVerified: true, displayName: "Paddy", email: "" });
}

var BAUSTEINE = [
  {
    id: "dropdown",
    titel: "Dropdown / Überlaufmenü",
    was: "Öffnen-Animation, Pfeiltasten, Fokusring, Rand bei wenig Platz.",
    stellen: [
      "togglePlanMenu() — index.html:11405",
      "toggleProfileMenu() — index.html:11428",
      "toggleWeightMenu() — index.html:11462",
      "openAssignMenu() — index.html:11497"
    ],
    oeffnen: function (doc) {
      var b = doc.querySelector('[data-action="profile-menu"]');
      if (b) { b.click(); return "Profilmenü geöffnet"; }
      return "Profil-Knopf nicht gefunden";
    }
  },

  {
    id: "leere-zustaende",
    titel: "Leere Zustände",
    was: "Sehen sie gleich aus? Hat jeder eine klare nächste Aktion?",
    stellen: [
      ".empty — index.html:7207 (Rezeptbuch)",
      ".wch-empty — index.html:6022 (Gewichtsverlauf)",
      ".ms-empty-ings — index.html:8102 ff. (Meal-Blatt)",
      ".wl-empty — index.html:7646 (Gewichtsliste)",
      ".pempty — index.html:9241 (Picker)",
      ".shop-empty — index.html:9781 (Vorkochen), :9812 (Einkaufsliste)",
      "↑ erst beim Umbau gefunden — die Bestandsaufnahme hielt sie für klassenlose <p>"
    ],
    // Ohne Meals und ohne Plan sind die leeren Zustaende ueberhaupt erst zu sehen.
    zustand: { recipes: [], plans: {}, weights: [] },
    // Zwei Schritte mit Pause dazwischen: Der Reiterwechsel rendert neu, der
    // Einkaufslisten-Knopf entsteht erst dabei. Ein `b.click(); s.click()` in einem Zug
    // greift ins Leere (20.09.2026).
    schritte: [
      '[data-action="tab"][data-tab="plan"]',
      '[data-action="shopping"]'
    ]
  },

  {
    id: "tabs",
    titel: "Tabs und Segmente",
    was: "Drei Bauarten für dieselbe Sache — gleiche Höhe, gleiche Bewegung, gleicher Fokus?",
    stellen: [
      ".tabs — index.html:160 (Hauptreiter)",
      ".daybar — css/mobil.css:158 (Tagesleiste)",
      ".kal-seg — index.html:6534 (Zeitraum im Fortschritt)"
    ],
    oeffnen: function (doc) {
      var b = doc.querySelector('[data-action="tab"][data-tab="progress"]');
      if (b) { b.click(); return "Fortschritt geöffnet (zeigt .kal-seg)"; }
      return "Reiter nicht gefunden";
    }
  },

  {
    id: "akkordeon",
    titel: "Akkordeon / Aufklappen",
    was: "Natives <details> gegen data-action=\"toggle-*\" — zwei Mechanismen, ein Zweck.",
    stellen: [
      "<details> — 6 Stellen (u. a. .wg-wk :7534, .ing-nut :8574, .grp-note :11175)",
      "data-action=\"toggle-*\" — 6 Stellen (toggle-day-goals :4519, toggle-cat :6811, toggle-fav :7297)"
    ],
    // Der Wiege-Dialog traegt `.wg-wk` - den einzigen Aufklapper, der seinen Pfeil
    // bis zum 20.09.2026 aus den Zeichen "▾"/"▴" baute statt aus dem gemeinsamen SVG.
    // Dafuer braucht es die Einwilligung und einen Messwert, sonst ist die Karte leer.
    zustand: {
      weightConsent: { given: true, at: 1758000000000, version: 1 },
      weights: [{ m: "2026-W36", kg: 84 }]
    },
    schritte: [
      '[data-action="tab"][data-tab="progress"]',
      '[data-action="weigh"]'
    ]
  },

  {
    id: "buttons",
    titel: "Buttons",
    was: "Rahmenlose Textknöpfe im Fuß — und die Radien der Zutaten-Knöpfe (1 px).",
    stellen: [
      ".btn.primary (34×), .btn.ghost.sm (32×), .btn.ghost (20×)",
      "Kontext statt Variante: onb-skip, wg-recalc, ms-ing-add, shop-ic, plan-auto",
      "NEU 21.09.: .btn.link (+.inline/.leise) ersetzt auth-forgot/toggle-all/foot-link",
      "⚠ Der Hauptgewinn ist UNSICHTBAR: die Trefferflächen. Nur am Gerät spürbar."
    ],
    oeffnen: function () { return "Startseite — der Fuß steht ganz unten"; }
  },

  {
    id: "dialoge",
    titel: "Bestätigen oder Rückgängig?",
    was: "Links fragt „Woche leeren“ erst nach. Rechts leert es sofort — und legt "
       + "„Rückgängig“ in den Toast. Beide Seiten anklicken und vergleichen.",
    stellen: [
      "deleteRecipe() — confirmModal entfernt, undoToast auf 10 s verlängert",
      "clearWeek() — confirmModal entfernt, undoToast unverändert 5 s",
      "Unangetastet: die 11 übrigen confirmModal — sie erklären, betreffen Dritte "
        + "oder sind endgültig (Konto löschen)",
      "⚠ Ein Standbild zeigt hier NICHTS — die Änderung ist ein weggefallener Dialog."
    ],
    // ⚠ OHNE gefuellten Plan zeigt diese Probe NICHTS: clearWeek() bricht bei
    // planStats() === 0 sofort mit "Der Plan ist schon leer" ab - auf BEIDEN Seiten
    // gleich, und man vergliche zweimal denselben Toast (TROUBLESHOOTING 174).
    //
    // Der Plan wird deshalb von der App selbst angelegt, ueber den Auto-Planer. Einen
    // plans-Block hier hineinzuschreiben ginge nicht ohne isoWeekKey() nachzubauen -
    // und Nachbau von Produktionscode ist in diesem Projekt ausgeschlossen
    // (CLAUDE.md 11). Der Testzustand hat Ziel und ein Rezept, mehr braucht autoPlanWeek
    // nicht.
    schritte: [
      '[data-action="tab"][data-tab="plan"]',
      '[data-action="auto-plan"]',
      '[data-action="plan-menu"]'
    ],
    oeffnen: function (doc) {
      var m = doc.querySelector(".menu");
      if (!m) return "⚠ Plan-Menü nicht offen — ist der Plan gefüllt?";
      return "Plan gefüllt, Menü offen — jetzt LINKS und RECHTS „Woche leeren“ antippen";
    }
  },

  {
    id: "makro-toleranz",
    titel: "Übernommenes Meal bearbeiten",
    was: "Links steht bei „Makros gesamt“ schon „manuell angepasst“, obwohl nichts "
       + "geändert wurde. Rechts nicht. Danach beidseits eine Zutatenmenge ändern: "
       + "Nur rechts rechnen die kcal mit.",
    stellen: [
      "macroWeichtAb() — index.html:9235 (Toleranz 0,5 statt exakter Gleichheit)",
      "⚠ Der Hauptgewinn ist ein VERHALTEN: kcal rechnen beim Ändern der Menge mit."
    ],
    // Leerer Bestand: Dann ist "Hauptgericht" nach dem Uebernehmen die einzige und damit
    // die erste Kategorie - und die erste steht in "Meine Meals" offen (collapsedCats).
    zustand: { recipes: [] },
    // Wirklich uebernehmen statt eine Kopie hineinzuschreiben: Eine Kopie hier muesste
    // copyFromCookbook() nachbauen (CLAUDE.md 11).
    schritte: [
      '[data-action="tab"][data-tab="recipes"]',
      '[data-rtab="buch"]',
      '[data-cbcat="Hauptgericht"]',
      '[data-adopt="chili-rinderhack-bohnen"]',
      '[data-rtab="meine"]',
      '[data-action="view"]',
      '[data-edit]'
    ]
  },

  {
    id: "alter-16",
    titel: "Einführung: Alter unter 16",
    was: "Beide Seiten tragen 14 Jahre ein und tippen auf „Weiter“. Links geht es weiter "
       + "zum Körperfett, rechts erscheint der Hinweis „zwischen 16 und 120 Jahre“.",
    stellen: [
      "ONB_NUM.age.min — index.html (Grenze 16, eine Quelle)",
      "missingCalc() — liest dieselbe Grenze, statt sie auszuschreiben"
    ],
    // Frisch: Ohne Ziel startet die Einfuehrung von selbst.
    zustand: { goal: null, onboarded: false },
    // Echte Klicks und Eingaben in Folge - die Einfuehrung baut jeden Schritt neu auf,
    // deshalb mit Pausen statt in einem Zug.
    oeffnen: function (doc) {
      var w = doc.defaultView;
      function weiter() { var b = doc.querySelector(".onb-next"); if (b) b.click(); }
      function tippe(sel, wert) {
        var el = doc.querySelector(sel); if (!el) return;
        el.value = wert; el.dispatchEvent(new w.Event("input", { bubbles: true }));
      }
      function koerper() {
        if (!doc.querySelector('[data-num="age"]')) {    // noch nicht dort: Name o. Ae.
          tippe("#onb-text", "Vergleich"); weiter(); w.setTimeout(koerper, 500); return;
        }
        var m = doc.querySelector('[data-opt="sex"][data-v="m"]'); if (m) m.click();
        tippe('[data-num="age"]', "14");
        tippe('[data-num="height"]', "175");
        tippe('[data-num="weight"]', "70");
        w.setTimeout(weiter, 300);
      }
      weiter();
      w.setTimeout(koerper, 500);
      return "Einführung bis „Körperdaten“, 14 Jahre eingetragen, „Weiter“ getippt";
    }
  },

  {
    id: "toast",
    titel: "Toast: Glas statt weißer Pille",
    was: "Der Toast mit „Rückgängig“ steht dauerhaft über dem Plan. Links die alte Pille "
       + "(im Dunkeln weiß), rechts Glas wie die Reiterleiste. Oben Hell/Dunkel umschalten.",
    stellen: [
      "#toast — css/komponenten.css (eine Regel für alle ~130 Aufrufe)",
      "Rückfälle ohne Blur und bei „Transparenz reduzieren“ — direkt darunter"
    ],
    zustand: {},
    // Echtes #toast-Element und echtes CSS, nur ohne den Ausblende-Timer von toast()/
    // undoToast() - sonst waere er nach 2 bzw. 5 Sekunden weg, bevor man vergleicht.
    // Markup wie in undoToast(): <span> + button.toast-undo.
    oeffnen: function (doc) {
      var t = doc.getElementById("toast"); if (!t) return "kein #toast gefunden";
      t.textContent = "";
      var s = doc.createElement("span"); s.textContent = "Meal gelöscht"; t.appendChild(s);
      var b = doc.createElement("button"); b.type = "button"; b.className = "toast-undo";
      b.textContent = "Rückgängig"; t.appendChild(b);
      t.classList.add("show", "has-undo");
      return "Toast mit „Rückgängig“ dauerhaft eingeblendet";
    }
  },

  {
    id: "zahl-hinweise",
    titel: "Hinweis bei Zahlen außerhalb der Grenzen",
    was: "Beide Seiten tragen 12 Jahre ein und tippen auf „Weiter“. Links „Alter: bitte ein "
       + "Wert zwischen 16 und 120 Jahre“, rechts „Trag dein Alter zwischen 16 und 120 Jahren "
       + "ein“. Danach selbst probieren: Größe 300, Gewicht 500 – und im Wiegen-Dialog.",
    stellen: [
      "onbNumMissing() — Alter, Größe, Gewicht, Trainingsdauer (Wörter aus ONB_NUM.bad)",
      "onbMissing(\"target\") — Zielgewicht",
      "Wiegen-Dialog — zwei Stellen, gleicher Satz"
    ],
    zustand: { goal: null, onboarded: false },
    oeffnen: function (doc) {
      var w = doc.defaultView;
      function weiter() { var b = doc.querySelector(".onb-next"); if (b) b.click(); }
      function tippe(sel, wert) {
        var el = doc.querySelector(sel); if (!el) return;
        el.value = wert; el.dispatchEvent(new w.Event("input", { bubbles: true }));
      }
      function koerper() {
        if (!doc.querySelector('[data-num="age"]')) {
          tippe("#onb-text", "Vergleich"); weiter(); w.setTimeout(koerper, 500); return;
        }
        var m = doc.querySelector('[data-opt="sex"][data-v="m"]'); if (m) m.click();
        tippe('[data-num="age"]', "12");
        tippe('[data-num="height"]', "175");
        tippe('[data-num="weight"]', "70");
        w.setTimeout(weiter, 300);
      }
      weiter();
      w.setTimeout(koerper, 500);
      return "Einführung bis „Körperdaten“, 12 Jahre eingetragen, „Weiter“ getippt";
    }
  },

  {
    id: "cloud-laden",
    titel: "Erster Cloud-Abgleich auf frischem Gerät",
    was: "Angemeldet, der Abgleich läuft noch. Links der leere Plan, der wie „alles weg“ "
       + "aussieht, rechts die Ladeanzeige. Auch die anderen Reiter antippen.",
    stellen: [
      "render() — Ladeanzeige, solange !cloudBaselineOk && !state.goal",
      "startCloudSync() — zeichnet nach dem Abgleich neu (zwei Stellen + catch)"
    ],
    // Frisches Geraet: kein Ziel, keine Meals. Ein Cloud-Profil, damit die App nach dem
    // Start in der Cloud-Anmeldung steht statt lokal loszulaufen.
    zustand: { goal: null, onboarded: false, recipes: [], plans: {} },
    profil: { name: "Vergleich", email: "", uid: "vergleich", cloud: true },
    // Die Anmeldemaske ist hier der erwartete Startpunkt - nicht auf enterApp() warten.
    nurInhalt: true,
    // Anmeldung nachstellen, OHNE dass etwas ans Netz geht: CloudSync wird durch eine
    // Attrappe ersetzt, deren load() nie antwortet - genau der haengende Abgleich aus dem
    // Instagram-Browser. Danach laeuft der echte handleCloudUser() -> enterApp() ->
    // startCloudSync(). Der Pro-Listener entfaellt, er ginge sonst an Firestore.
    oeffnen: function (doc) {
      var w = doc.defaultView;
      w.CloudEntitlement = null;
      w.CloudSync = { enabled: true, load: function () { return new Promise(function () {}); } };
      w.__onCloudAuth({ uid: "vergleich", emailVerified: true, displayName: "Vergleich", email: "" });
      return "Anmeldung nachgestellt, der Abgleich hängt absichtlich";
    }
  },

  {
    id: "gruppe-fuer-alle",
    titel: "Gruppe: erst „nur ich“, „für euch beide“ bewusst wählen",
    was: "Zweiergruppe (Paddy + Anna), ein Meal wird automatisch in den ersten Mittag gelegt, "
       + "danach wird das Personen-Symbol der Karte angetippt. Rechts: Toast „Für dich eingeplant“ "
       + "mit „Für euch beide“ (8 s), Karte ohne Schild, Menü mit drei Wahlen. Links (live): "
       + "„für alle“ ohne Hinweis, der Tipp aufs Symbol schaltet stumm um. Danach selbst: "
       + "„Für euch beide“ wählen – Karte zeigt „· für 2“ und beide Kürzel; „Einkaufsliste“ "
       + "öffnen – dort steht „Wie eure Gruppe“.",
    stellen: [
      "Plankarte .r-meta + title + Schild — renderPlan(), Kartenschleife",
      "Personen-Symbol — openAssignMenu(), Einfachauswahl bei zwei Personen",
      "Auto-Planer — autoPlanWeek(), plant nur für mich",
      "eingeplantMelden() — Picker, Schnellauswahl, Barcode (2×), Meal anlegen + einplanen",
      "Einkaufsliste .shop-pers-src — persAusGruppe()"
    ],
    zustand: { goal: null, onboarded: false, recipes: [], plans: {} },
    profil: { name: "Paddy", email: "", uid: "vergleich", cloud: true },
    nurInhalt: true,
    // Gruppe nachstellen, OHNE dass etwas ans Netz geht - wie bei cloud-laden, nur dass
    // load() hier antwortet. Alles, was die App sonst noch an CloudSync/CloudGroup fragt
    // (Speichern, Listener, Mitgliedseintrag), faengt ein Proxy als stilles Nichts ab:
    // eine Funktion, die zugleich als Promise taugt - Listener geben sie als Abmelder
    // zurueck, await liest sie als "erledigt".
    oeffnen: function (doc) {
      var w = doc.defaultView;
      zweiergruppeNachstellen(w);
      // Nach dem Abgleich: Plan-Reiter, erster "Meal wählen", das Meal im Picker antippen.
      // NICHT nach fester Uhr: Die beiden Seiten laden unterschiedlich schnell, und ein
      // Picker, der vor dem Abgleich aufgeht, ist leer - mit festen 1,2 s klappte es links
      // und rechts nicht (05.10.2026). Also: so lange versuchen, bis das Meal drinsteht.
      function versuch(n) {
        var tab = doc.querySelector('[data-action="tab"][data-tab="plan"]');
        if (tab && tab.getAttribute("aria-selected") !== "true") tab.click();
        // Den Mittag des SICHTBAREN Tages nehmen: Am Handy zeigt der Streifen heute, nicht
        // Montag - eine Karte am Montag saehe man nicht, und das Menue hinge im Nichts.
        var pick = [].filter.call(doc.querySelectorAll('[data-action="pick"][data-meal="mi"]'), function (x) {
          var r = x.getBoundingClientRect();
          return r.width > 0 && r.left >= 0 && r.right <= w.innerWidth;
        })[0];
        if (pick) pick.click();
        w.setTimeout(function () {
          var item = doc.querySelector('[data-assign="rvgbowl"]');
          if (item) {
            item.click();
            // Das Personen-Symbol antippen: rechts geht das Menue auf, links schaltet es
            // stumm weiter - genau der Unterschied, um den es geht.
            w.setTimeout(function () {
              var symbol = [].filter.call(doc.querySelectorAll('[data-action="assign"]'), function (x) {
                var r = x.getBoundingClientRect();
                return r.width > 0 && r.left >= 0 && r.right <= w.innerWidth;
              })[0];
              if (symbol) symbol.click();
            }, 1500);
            return;
          }
          var zu = doc.querySelector(".modal [data-close]");
          if (zu) zu.click();
          if (n < 20) w.setTimeout(function () { versuch(n + 1); }, 500);
        }, 400);
      }
      w.setTimeout(function () { versuch(0); }, 800);
      return "Gruppe nachgestellt (ohne Netz), Meal wird gleich eingeplant";
    }
  },

  {
    id: "einkauf-minus",
    titel: "Einkaufsliste in der Gruppe: „−“ gilt für diesen Einkauf",
    was: "Zweiergruppe, ein Meal „für euch beide“, die Einkaufsliste geht von selbst auf "
       + "(„2 Personen · Wie eure Gruppe“, 240 g Brokkoli). Selbst auf „−“ tippen. Rechts: "
       + "1 Person, 120 g, „Wie eure Gruppe“ verschwindet. Links (live): „−“ tut nichts. "
       + "Danach rechts schließen und neu öffnen: wieder 2 Personen – nichts bleibt hängen.",
    stellen: [
      "shopPersons() — in der Gruppe: Gruppenzahl, außer bei offener Liste verstellt",
      "shopPersOffen — erlischt mit dem Schließen (node.isConnected)",
      "persAusGruppe() — „Wie eure Gruppe“, solange die Zahl der Gruppe entspricht",
      "Einkaufsliste .pbtn — in der Gruppe nicht gespeichert, ohne Gruppe wie bisher"
    ],
    zustand: { goal: null, onboarded: false, recipes: [], plans: {} },
    profil: { name: "Paddy", email: "", uid: "vergleich", cloud: true },
    nurInhalt: true,
    oeffnen: function (doc) {
      var w = doc.defaultView;
      zweiergruppeNachstellen(w);
      // Nach dem Abgleich: Plan-Reiter, ein Meal in den Sonntagmittag (der zaehlt in der
      // Einkaufsliste immer - vergangene Tage der Woche nicht), dann die Einkaufsliste.
      // Ohne Zutaten zeigt sie nur den leeren Zustand, ohne Personenzahl. Wie bei
      // gruppe-fuer-alle nicht nach fester Uhr, sondern so lange versuchen, bis es klappt.
      function versuch(n) {
        if (doc.querySelector(".shop-persons")) return;
        var tab = doc.querySelector('[data-action="tab"][data-tab="plan"]');
        if (tab && tab.getAttribute("aria-selected") !== "true") tab.click();
        var hatMeal = !!doc.querySelector('[data-action="assign"]');
        w.setTimeout(function () {
          if (!hatMeal) {
            var picks = doc.querySelectorAll('[data-action="pick"][data-meal="mi"]');
            if (picks.length) picks[picks.length - 1].click();
            w.setTimeout(function () {
              var item = doc.querySelector('[data-assign="rvgbowl"]');
              if (item) {
                item.click();
                // "Für euch beide" im Toast: Nur ein Meal fuer alle rechnet mit der
                // Personenzahl - bei "nur ich" aenderte "-" die Zahl, aber keine Menge.
                // Links (vorher) gibt es den Knopf genauso, die Ausgangslage ist gleich.
                w.setTimeout(function () {
                  var beide = [].filter.call(doc.querySelectorAll("button"), function (b) {
                    return b.textContent.trim() === "Für euch beide";
                  })[0];
                  if (beide) beide.click();
                }, 500);
              } else { var zu = doc.querySelector(".modal [data-close]"); if (zu) zu.click(); }
              if (n < 20) w.setTimeout(function () { versuch(n + 1); }, 1400);
            }, 400);
            return;
          }
          // Den Toast "Für dich eingeplant" erst abwarten lassen ist nicht noetig - die
          // Liste legt sich darueber.
          var s = [].filter.call(doc.querySelectorAll('[data-action="shopping"]'), function (x) {
            return x.getBoundingClientRect().width > 0;
          })[0];
          if (s) s.click();
          if (n < 20) w.setTimeout(function () { versuch(n + 1); }, 500);
        }, 400);
      }
      w.setTimeout(function () { versuch(0); }, 800);
      return "Gruppe nachgestellt (ohne Netz), Einkaufsliste geht gleich auf";
    }
  }
];
