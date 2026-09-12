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
    // Ei fuer die Schnellauswahl. Oben deutlich schmaler als unten - bei 16 px ist das der
    // einzige Unterschied zum Apfel, ein gleichmaessiges Oval liest sich als Kartoffel.
    egg:      '<path d="M12 2.8C8.8 2.8 5.6 8.4 5.6 13a6.4 6.4 0 0 0 12.8 0c0-4.6-3.2-10.2-6.4-10.2Z"/>',
    // ---------- Ein Symbol je Lebensmittel (12.09.2026) ----------
    // Bis hierher trugen die 36 Eintraege der Schnellauswahl fuenf Sammelsymbole, und seit
    // dem Umbau vom 12.09.2026 stehen sie auch im Wochenplan, auf dem Startreiter, im
    // Meal-Blatt und in der Vorkochliste - dort faellt "alles Obst sieht gleich aus" sofort
    // auf. Deshalb bekommt jede unterscheidbare FORM ihr eigenes Symbol.
    //
    // Bewusst NICHT jeder Name ein eigenes: Orange, Mandarine und Grapefruit sind dieselbe
    // Kugel mit Blatt, Pfirsich, Nektarine, Pflaume, Zwetschge und Kaki dieselbe Steinfrucht.
    // Ein erfundener Unterschied ist bei 28 px nicht lesbar und nur eine weitere Stelle, die
    // altert. Die fuenf Sammelsymbole bleiben: sie tragen die Kategorie-Ueberschriften und
    // den Rueckfall von foodIcon().
    //
    // Alle Pfade sind bei 28 px gegen ihre Nachbarn geprueft (tools/probe-symbole.html) -
    // wer einen aendert, prueft ihn dort erneut und nicht bei 64 px.
    banana:   '<path d="M5.6 4c1.3-.4 2.3.4 2.6 1.8.9 5 4.2 8.1 8.8 8.5 1.4.1 1.9 1.1 1.1 2.1-1.2 1.6-3.5 2.4-6 1.8C7.2 16.9 4.7 11.2 4.8 5.2c0-.6.3-1 .8-1.2Z"/>',
    citrus:   '<circle cx="12" cy="13.5" r="7"/><path d="M12 6.5V4.8"/><path d="M12.6 5.4c1-1.4 2.6-1.9 4-1.4.3 1.4-.6 2.9-2 3.4-.8.3-1.6.2-2-.2Z"/>',
    pear:     '<path d="M12 20.8c-2.9 0-5.1-2.1-5.1-4.8 0-1.9 1.1-3.1 1.9-4.1.7-.9 1-1.7 1-2.7 0-1.7 1-2.9 2.2-2.9s2.2 1.2 2.2 2.9c0 1 .3 1.8 1 2.7.8 1 1.9 2.2 1.9 4.1 0 2.7-2.2 4.8-5.1 4.8Z"/><path d="M12 6.3V4.2"/><path d="M12.4 5.2c.8-1.2 2.1-1.7 3.4-1.4.2 1.3-.7 2.6-2 3"/>',
    kiwi:     '<circle cx="12" cy="12" r="7.8"/><ellipse cx="12" cy="12" rx="1.8" ry="2.1"/><circle cx="12" cy="6.4" r=".6" fill="currentColor" stroke="none"/><circle cx="16.2" cy="9.2" r=".6" fill="currentColor" stroke="none"/><circle cx="16.2" cy="14.8" r=".6" fill="currentColor" stroke="none"/><circle cx="12" cy="17.6" r=".6" fill="currentColor" stroke="none"/><circle cx="7.8" cy="14.8" r=".6" fill="currentColor" stroke="none"/><circle cx="7.8" cy="9.2" r=".6" fill="currentColor" stroke="none"/>',
    stonefruit: '<circle cx="12" cy="13.5" r="7"/><path d="M12 6.6c-1.3 2.3-1.3 4.6 0 6.9s1.3 4.6 0 6.9"/><path d="M12.6 6.3c.6-1.8 2.2-2.9 4-2.7.2 1.8-1 3.4-2.8 3.8"/>',
    cherry:   '<circle cx="8" cy="17" r="3.2"/><circle cx="16.6" cy="17.8" r="2.8"/><path d="M8.7 13.9C9.6 9.5 12.3 5.8 16.6 4.2"/><path d="M16.9 15c-.7-3.1-.5-6.2.2-9.1"/>',
    strawberry: '<path d="M12 20.8c-3.6 0-6.4-3.2-6.4-6.7 0-2.6 2.4-4.5 6.4-4.5s6.4 1.9 6.4 4.5c0 3.5-2.8 6.7-6.4 6.7Z"/><path d="M8.4 8.1c1.1 1 2.3 1.5 3.6 1.5s2.5-.5 3.6-1.5"/><path d="M12 9.6V6.2"/>',
    fig:      '<path d="M12 20.6c-3.3 0-6-2.5-6-5.6 0-3 2.1-4.8 3.4-6.2.8-.9 1.3-1.7 1.5-2.6h2.2c.2.9.7 1.7 1.5 2.6C15.9 10.2 18 12 18 15c0 3.1-2.7 5.6-6 5.6Z"/><path d="M12 6.2V3.9"/><path d="M11.6 5.6c-1.1-1.3-2.8-1.7-4.2-1 .3 1.5 1.7 2.6 3.3 2.6"/><path d="M12.4 5.6c1.1-1.3 2.8-1.7 4.2-1-.3 1.5-1.7 2.6-3.3 2.6"/>',
    mango:    '<path d="M17.7 7c2.4 2.4 1.9 6.6-1 9.5s-7.1 3.4-9.5 1-1.9-6.6 1-9.5 7.1-3.4 9.5-1Z"/><path d="M15.6 8.6c.4-1.8 1.8-3.2 3.6-3.5"/>',
    carrot:   '<path d="M16.2 8.2 7.1 17.3c-1.3 1.3-.6 3.4 1.2 3.7l2.6.4c1 .2 2.1-.2 2.8-.9l6.1-6.1Z"/><path d="m13.4 12.4 1.7 1.7M10.9 14.9l1.7 1.7"/><path d="M17 9c0-2.3 1.9-4.2 4.2-4.2 0 2.3-1.9 4.2-4.2 4.2Z"/>',
    pepper:   '<path d="M12 20c-1.1.7-2.6.8-3.9.2-2.4-1.1-3.4-4.2-2.2-6.9 1-2.2 3.4-3.6 6.1-3.6s5.1 1.4 6.1 3.6c1.2 2.7.2 5.8-2.2 6.9-1.3.6-2.8.5-3.9-.2Z"/><path d="M9.3 19.6c-.5-1.3-.6-2.8-.3-4.3M14.7 19.6c.5-1.3.6-2.8.3-4.3"/><path d="M12 9.7V7.5"/><path d="M12 7.7c1-1.4 2.5-2 4-1.7.1 1.5-1.1 2.9-2.7 3.2"/>',
    tomato:   '<circle cx="12" cy="14" r="6.6"/><path d="M8.6 7.6c1 .9 2.2 1.3 3.4 1.3s2.4-.4 3.4-1.3"/><path d="M8.6 7.6 7 6.2M15.4 7.6 17 6.2"/><path d="M12 8.9V6.2"/>',
    cucumber: '<path d="M18.1 5.9c1.7 1.7.5 5.5-2.6 8.6s-6.9 4.3-8.6 2.6-.5-5.5 2.6-8.6 6.9-4.3 8.6-2.6Z"/><path d="m9.1 12.9 1.9 1.9M11.5 10.5l1.9 1.9M13.9 8.1l1.9 1.9"/>',
    radish:   '<path d="M12 20.6c-2.9 0-5.2-2.2-5.2-4.9 0-2.4 2.3-4.3 5.2-4.3s5.2 1.9 5.2 4.3c0 2.7-2.3 4.9-5.2 4.9Z"/><path d="M12 11.3V8.4"/><path d="M12 8.4c-1.2-2-3.5-2.8-5.3-1.9.3 2 2.2 3.4 4.3 3.2"/><path d="M12 8.4c1.2-2 3.5-2.8 5.3-1.9-.3 2-2.2 3.4-4.3 3.2"/>',
    avocado:  '<path d="M12 20.8c-3.3 0-5.9-2.8-5.9-6.3 0-3.9 2.6-8.5 5.9-8.5s5.9 4.6 5.9 8.5c0 3.5-2.6 6.3-5.9 6.3Z"/><ellipse cx="12" cy="14.8" rx="2.3" ry="2.6"/>',
    olive:    '<ellipse cx="12" cy="12.8" rx="4.8" ry="6.6"/><circle cx="12" cy="12.8" r="1.6"/><path d="M12 6.2V4.4"/>',
    bun:      '<path d="M3.8 14.6c0-3.5 3.7-6.3 8.2-6.3s8.2 2.8 8.2 6.3c0 1.7-1.4 3-3 3H6.8c-1.7 0-3-1.3-3-3Z"/><path d="M9.6 10.4 8.2 14M14.4 10.4 15.8 14"/>',
    pretzel:  '<circle cx="8.4" cy="11.6" r="3"/><circle cx="15.6" cy="11.6" r="3"/><path d="M5.6 13.6c.9 3.3 3.4 5.4 6.4 5.4s5.5-2.1 6.4-5.4"/><path d="M10.1 9.2 12 5.9l1.9 3.3"/>',
    croissant: '<path d="M3.9 16.9c-.5-2.4.5-5.2 2.8-7.4C8.3 8 10.1 7.2 12 7.2s3.7.8 5.3 2.3c2.3 2.2 3.3 5 2.8 7.4-2 .4-4-.3-5.7-1.6-.9-.7-1.6-1-2.4-1s-1.5.3-2.4 1c-1.7 1.3-3.7 2-5.7 1.6Z"/><path d="M6.6 9.6 5.3 7.4M17.4 9.6l1.3-2.2"/>',
    ricecake: '<circle cx="12" cy="12" r="7.8"/><circle cx="9.2" cy="9.6" r=".7" fill="currentColor" stroke="none"/><circle cx="13.1" cy="8.8" r=".7" fill="currentColor" stroke="none"/><circle cx="15.4" cy="11.4" r=".7" fill="currentColor" stroke="none"/><circle cx="11.6" cy="12.1" r=".7" fill="currentColor" stroke="none"/><circle cx="8.4" cy="13.2" r=".7" fill="currentColor" stroke="none"/><circle cx="13.6" cy="15" r=".7" fill="currentColor" stroke="none"/><circle cx="10.2" cy="16" r=".7" fill="currentColor" stroke="none"/>',
    donut:    '<circle cx="12" cy="12" r="7.8"/><circle cx="12" cy="12" r="3.1"/><path d="m8.6 7.2.9 1.3M15.8 8.1l-1 1.1M16.6 14.4l1.3.6M7.2 14l-1.3.8"/>',
    berliner: '<circle cx="12" cy="12.5" r="7.4"/><path d="M4.8 12.6c1.8 1 4.2 1.5 7.2 1.5s5.4-.5 7.2-1.5"/><path d="M10.4 8.4h3.2"/>',
    muffin:   '<path d="M6.4 11.6h11.2l-1.2 7.3c-.1.9-.9 1.6-1.8 1.6H9.4c-.9 0-1.7-.7-1.8-1.6Z"/><path d="M5.3 11.6C4 10.4 4.4 8.2 6.1 7.5c-.1-2 1.8-3.6 3.8-3.1C10.9 3 13.1 3 14.1 4.4c2-.5 3.9 1.1 3.8 3.1 1.7.7 2.1 2.9.8 4.1"/>',
    // Gescanntes Fertigprodukt: EIN Symbol fuer alles mit Barcode. Ein Riegel, eine Dose und
    // ein Joghurtbecher haetten je eine eigene Form - nur weiss die App nie, welche davon in
    // der Packung steckt. Die Packung ist das Einzige, was sicher stimmt.
    package:  '<path d="M4.6 8.2 12 4.6l7.4 3.6v7.6L12 19.4l-7.4-3.6Z"/><path d="M4.6 8.2 12 11.8l7.4-3.6M12 11.8v7.6"/>',
  };
  // ---------- Symbole fuer die Schnellauswahl im Picker ----------
  // Bis zum 11.09.2026 trugen dort ALLE Eintraege dasselbe Fruchtsymbol - auch das
  // Broetchen und das Ei. Die Zuordnung steht bewusst als Liste von NAMEN und nicht als
  // Stichwortregel: Bei 36 Eintraegen ist die Liste ueberschaubar, und eine Stichwortregel
  // liefe genau in die Teilwort-Falle, die dieses Projekt schon kennt - "ei" steckt in
  // "Eisbergsalat", "feige" in nichts, aber "birne" in "Erdbirne".
  //
  // Wer einen Eintrag umbenennt, laesst hier eine tote Zuordnung zurueck. Das ist kein
  // stiller Fehler: tools/pruefstand-stueckliste.py meldet sie.
  const FOOD_ICON = {
    // Obst, das man aus der Hand isst. "fruit" ist der Apfel - das Sammelsymbol war von
    // Anfang an seine Form, deshalb braucht er kein zweites.
    "Apfel": "fruit", "Banane": "banana", "Birne": "pear", "Kiwi": "kiwi",
    "Erdbeeren": "strawberry", "Kirschen": "cherry", "Mango": "mango", "Feigen, frisch": "fig",
    // dieselbe Kugel mit Blatt
    "Orange": "citrus", "Mandarine": "citrus", "Grapefruit": "citrus",
    // dieselbe Steinfrucht mit Naht
    "Pfirsich": "stonefruit", "Nektarine": "stonefruit", "Pflaumen": "stonefruit",
    "Zwetschge": "stonefruit", "Kaki": "stonefruit",
    // rohes Gemuese
    "Karotten": "carrot", "Paprika, rot": "pepper", "Snackpaprika": "pepper",
    "Tomaten": "tomato", "Kirschtomaten": "tomato", "Snackgurke": "cucumber",
    "Radieschen": "radish", "Avocado": "avocado", "Oliven, grün": "olive",
    // Backware vom Baecker
    "Weizenbrötchen": "bun", "Vollkornbrötchen": "bun", "Laugenbrezel": "pretzel",
    "Croissant": "croissant", "Reiswaffeln": "ricecake",
    // Suessgebaeck
    "Berliner": "berliner", "Donut": "donut", "Muffin": "muffin",
    // Ei
    "Ei, Größe S": "egg", "Ei, Größe M": "egg", "Ei, Größe L": "egg",
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
  // Haken fuer einen geplanten Tag im Monatsgitter des Fortschritt-Kalenders.
  // Bewusst nur der Haken ohne Kreis darum: den Kreis zeichnet CSS (.kal-t.on .kal-sym),
  // damit "geplant" Flaeche UND Symbol traegt und nicht allein an der Farbe haengt.
  const ICON_CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 5 5 9-11"/></svg>';
  // Die beiden Monatspfeile. Zwei Konstanten statt einer gedrehten: eine CSS-Spiegelung
  // haette auch den Fokusring und den Press-State mitgedreht.
  const ICON_CHEV_L = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 5-7 7 7 7"/></svg>';
  const ICON_CHEV_R = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 5 7 7-7 7"/></svg>';
  // Die Flamme der WOCHENSERIE - und nur dieser. Die Tagesserie traegt sie ausdruecklich
  // nicht (docs/PRODUCT.md): andere Einheit, andere Aussage.
  // Stand bis zum 03.09.2026 inline in rueckblickHtml() und waere mit dem Rueckblick-Balken
  // verschwunden; seither steht die Serie im Kalenderfuss.
  const ICON_FLAME = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13.5 2c.4 3-1.6 4.2-2.9 5.6C9.2 9 8 10.4 8 12.6a4 4 0 0 0 8 .2c0-1.3-.5-2.3-1-3 .9.4 1.7 1.2 2.2 2.3.3-.7.5-1.6.5-2.6 0-3.4-2.3-5.4-4.2-7.5z"/></svg>';
