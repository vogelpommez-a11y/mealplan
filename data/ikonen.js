/* ikonen.js - Paddy's Mealplan
 *
 * Strich-, Aktions- und Einzel-Icons als SVG-Pfade.
 *
 * Reine Daten, keine Logik. Ausgeschnitten aus index.html, unveraendert.
 * Wird als klassisches <script> VOR der App-IIFE geladen; die Konstanten stehen
 * dadurch im globalen Bereich und werden von der IIFE gelesen.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  // ---------- Strich-Icons fuer die Kategorie-Ueberschriften ----------
  // Nur diese sieben werden gebraucht; Meals selbst zeigen immer ein Foto (siehe photoFor).
  const ICONS = {
    pot:      '<path d="M4 9.5h16v6a4.5 4.5 0 0 1-4.5 4.5h-7A4.5 4.5 0 0 1 4 15.5v-6Z"/><path d="M2.5 9.5h19"/><path d="M2 12.5h2M20 12.5h2"/><path d="M12 6.5V4.5"/><path d="M9 4.5h6"/>',
    utensils: '<path d="M5 2.5v6M7.75 2.5v6M10.5 2.5v6"/><path d="M4 8.5h7.5V10a3.75 3.75 0 0 1-7.5 0V8.5Z"/><path d="M7.75 13.75V21.5"/><path d="M19.5 2.5c-1.9 1.9-3 4.6-3 7.4v2.35h4.5V2.5Z"/><path d="M19.5 12.25V21.5"/>',
    salad:    '<path d="M3 12h18a9 9 0 0 1-18 0Z"/><path d="M12 12c0-3 2-5 5-5 0 3-2 5-5 5Z"/><path d="M12 12c0-3-2-5-5-5 0 3 2 5 5 5Z"/>',
    bread:    '<path d="M3.5 9.5c0-2.4 2-4 4.5-4h8c2.5 0 4.5 1.6 4.5 4 0 1.5-1 2.5-2.5 2.5v6.5H6V12c-1.5 0-2.5-1-2.5-2.5Z"/>',
    cake:     '<path d="M4.5 20.5v-7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v7"/><path d="M2.5 20.5h19"/><path d="M4.5 15.5c1.4 0 1.4 1.5 2.9 1.5s1.4-1.5 2.9-1.5 1.4 1.5 2.9 1.5 1.4-1.5 2.9-1.5 1.4 1.5 2.9 1.5"/><path d="M12 11.5V8.5"/><circle cx="12" cy="7" r="1.4"/>',
    fruit:    '<path d="M12 7.8c-1-1.6-3-2.2-4.7-1.1C4.8 8.2 4 11.2 5 14.6c.9 3 2.6 5.4 4.6 5.4 1 0 1.4-.5 2.4-.5s1.4.5 2.4.5c2 0 3.7-2.4 4.6-5.4 1-3.4.2-6.4-2.3-7.9-1.7-1.1-3.7-.5-4.7 1.1Z"/><path d="M12 7.8V4.6c0-1 1-2 2.5-2"/>',
    heart:    '<path d="M20.8 6.6a5 5 0 0 0-7.1 0L12 8.3l-1.7-1.7a5 5 0 1 0-7.1 7.1l8.8 8.8 8.8-8.8a5 5 0 0 0 0-7.1Z"/>',
    // Trinkglas mit Fuellstandslinie. Kam mit dem Eiweisshake-Wechsel dazu: "Getraenk" fiel
    // vorher auf den Topf zurueck (CAT_ICON[cat] || "pot"). Bewusst zwei Striche statt eines
    // detaillierten Glases - bei den 16 px der .cathead verschmilzt alles Feinere.
    // Die Breite ist gegengeprueft: eine erste Fassung lief nur von x=6 bis 18 und war bei
    // 16 px halb so breit wie Topf und Besteck - sie las sich als Becher, nicht als Glas.
    // Wer den Pfad aendert, prueft ihn bei 16 px gegen ein Nachbaricon, nicht bei 64 px.
    drink:    '<path d="M4.5 4h15l-1.5 15.3a2 2 0 0 1-2 1.7H8a2 2 0 0 1-2-1.7Z"/><path d="M5.2 9.5h13.6"/>',
  };
  const CAT_ICON = { "Frühstück": "bread", "Hauptgericht": "utensils", "Snack": "fruit", "Dessert": "cake", "Beilage": "salad", "Getränk": "drink" };
  // Dieselben Symbole an den Slot-Ueberschriften des Wochenplans, damit Plan und
  // Meals-Reiter dieselbe Bildsprache sprechen. Bewusst eine EIGENE Zuordnung und nicht
  // CAT_ICON durchgereicht: Slots sind keine Kategorien. "Hauptgericht" faellt auf zwei
  // Slots (mi/ab) - beide mit Besteck saehen gleich aus, deshalb bekommt der Abend den
  // Topf. Frei erfunden wird nichts, alle vier Symbole gibt es bereits in ICONS.
  const MEAL_ICON = { fr: "bread", mi: "utensils", ab: "pot", sn: "fruit" };

  // Aktions-Icons, u. a. fuer Profilbild-Aendern und Mitglied-entfernen. "view" (Ansehen)
  // entfiel mit openRecipeDetail/openRecipeForm (siehe plans/MealAnsicht.MD) - edit/del
  // bleiben, andere Aufrufer brauchen sie weiterhin.
  const ACT_ICONS = {
    edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
    del:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2"/><path d="M6 6v14a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V6"/><path d="M10 11v6M14 11v6"/></svg>',
    // Rechtliches im Profilmenue. Auf dem Handy ist das der Weg zu Impressum und
    // Datenschutz - eine Fusszeile muesste man erst ans Seitenende scrollen, ein klarer
    // Menuepunkt ist fuer mobile Seiten der uebliche und empfohlene Zugang.
    legal:  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></svg>',
  };
  // Werkzeug-Icons der Wochenplan-Leiste (Teilen / Leeren)
  const TOOL_ICONS = {
    share: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg>',
    clear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/></svg>',
    // Taschenrechner — vom frueheren Kalorienrechner-Reiter uebernommen (Wiedererkennung).
    recalc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8"/><path d="M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01"/></svg>',
    // Einkaufswagen. Zwei Ausloeser fuehren zur Einkaufsliste - der breite Knopf unter dem
    // Plan (Rechner) und der Icon-Knopf im Kopf (Handy). Dasselbe Icon aus einer Quelle,
    // damit die beiden nicht auseinanderlaufen (gleiche Ueberlegung wie bei BARCODE_SVG).
    cart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 6h15l-1.5 9h-12z"/><path d="M6 6 5 2H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>',
    // Zauberstab mit zwei Funken: der Auto-Wochenplaner (D2). Bewusst KEIN Kalender- oder
    // Listensymbol - die stehen im Wochenplan schon fuer den Plan selbst; hier geht es um
    // das automatische Fuellen, nicht um die Woche.
    wand: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 21 11-11"/><path d="m12.5 8.5 3 3"/><path d="M17.5 2.5 18.6 5l2.5 1.1-2.5 1.1-1.1 2.5-1.1-2.5L13.9 6l2.5-1.1Z"/><path d="M6.5 3 7.2 4.6 8.8 5.3 7.2 6 6.5 7.6 5.8 6 4.2 5.3l1.6-.7Z"/></svg>',
  };
  // Hantel (Trainingstag). Als EINZIGES Icon der App mit gefuellten Flaechen statt reiner
  // Konturen — und das aus einem geprueften Grund: Bei 13 px, wie es in der Tages-Kopfzeile
  // steht, verschmelzen duenne Striche. Eine Kontur-Hantel mit je zwei Scheiben wurde dort
  // zu einem unleserlichen Gewusel, eine mit je einer Scheibe zu einem „H". Zwei gefuellte
  // Bloecke plus Stange bleiben klein eindeutig als Hantel lesbar.
  // Wer das Icon gegen ein Kontur-Icon tauscht, muss es bei 13 px gegenpruefen.
  const ICON_DUMBBELL = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2" y="7.5" width="5" height="9" rx="1.6" fill="currentColor"/><rect x="17" y="7.5" width="5" height="9" rx="1.6" fill="currentColor"/><path d="M7 12h10" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
  // Flagge fuers "Grundziel" in der Ring-Kennzahlenliste (goalRingHtml).
  const ICON_FLAG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 21V4"/><path d="M5 4h13l-3 4.5L18 13H5"/></svg>';
  // Zwei-Personen-Icon fuer den "Zuweisung aendern"-Knopf einer geplanten Karte (ersetzt
  // den Stift, der wie "bearbeiten" liest, obwohl die Aktion "wer isst mit" bedeutet).
  const ICON_PEOPLE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="8.5" cy="8" r="3"/><path d="M2.5 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M15.3 6.3a3 3 0 0 1 0 5.7"/><path d="M17 14.4c2.3.6 4 2.8 4 5.6"/></svg>';
