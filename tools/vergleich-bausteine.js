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
  }
];
