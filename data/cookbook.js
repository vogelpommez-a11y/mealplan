/* cookbook.js - Paddy's Mealplan
 *
 * Der Rezeptkatalog (COOKBOOK).
 *
 * Reine Daten, keine Logik. Ausgeschnitten aus index.html, unveraendert.
 * Wird als klassisches <script> VOR der App-IIFE geladen; die Konstanten stehen
 * dadurch im globalen Bereich und werden von der IIFE gelesen.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  // ---------- Rezeptbuch ----------
  // Ein KATALOG, kein Bestand: Diese Meals liegen nicht in state.recipes, sondern werden
  // im Meals-Reiter unter "Rezeptbuch" gezeigt und per Tipp uebernommen. Erst dabei
  // entsteht eine Kopie im eigenen Konto.
  //
  // Warum nicht der ganze Katalog direkt in die Sammlung: 36 fremde Meals im eigenen Bestand
  // erdruecken die eigenen, kosten bei jedem Konto denselben Cloud-Speicher, und ein
  // Veganer schleppt zwei Drittel mit, die er nie kocht. Der Katalog kostet nichts, bis
  // jemand zugreift.
  //
  // `id` ist der dauerhafte Schluessel: Er landet beim Uebernehmen als `lib` an der Kopie
  // (siehe adoptFromCookbook) und verbindet sie mit dem Original - so laesst sich spaeter
  // eine korrigierte Fassung zuordnen. Er darf sich NIE aendern, auch wenn der Name sich
  // aendert.
  //
  // Das BILD steht dagegen in `img` und wird NICHT aus der id abgeleitet: Eine id darf einen
  // Umlaut tragen ("rührei-avocadobrot"), ein Dateiname sollte keinen. Eine Ableitung muesste
  // die Slug-Regel des Werkzeugs in JS nachbauen - zwei Fassungen derselben Regel laufen
  // auseinander (siehe docs/TROUBLESHOOTING.md 89).
  //
  // Mit Pro waechst genau diese Ansicht auf die grosse Bibliothek, die monatlich wechselt -
  // deshalb dieselbe Struktur und derselbe Uebernahme-Weg (siehe plans/Auto_Wochenplaner_D2.MD).
  const COOKBOOK = [
    { id: "overnight-oats-soja-beeren", name: "Overnight Oats mit Sojajoghurt und Beeren",
      category: "Frühstück", time: 5, tags: ["vegan", "vegetarisch", "laktosefrei"], mealPrep: true, img: "overnight-oats-soja-beeren.webp",
      nutrition: { kcal: 452, carbs: 48, protein: 20, fat: 17 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Sojajoghurt, natur", grams: 200, kcal: 50, carbs: 1.5, protein: 4, fat: 2.5 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 },
        { name: "Erdnussbutter", grams: 15, kcal: 600, carbs: 12, protein: 25, fat: 50 },
        { name: "Zimt, gemahlen", grams: 0.5, unit: "tl", kcal: 6, carbs: 2.1, protein: 0.1, fat: 0.1 }
      ],
      steps: "1. Haferflocken mit dem Sojajoghurt verrühren.\n2. Zugedeckt über Nacht in den Kühlschrank stellen.\n3. Am Morgen Heidelbeeren und Erdnussbutter daraufgeben.\n4. Mit ½ TL Zimt bestreuen." },

    { id: "rührei-avocadobrot", name: "Rührei mit Avocado auf Vollkornbrot",
      category: "Frühstück", time: 10, tags: ["vegetarisch"], mealPrep: false, img: "ruehrei-avocadobrot.webp",
      nutrition: { kcal: 523, carbs: 30, protein: 29, fat: 29 },
      ingredients: [
        { name: "Ei, Größe M", grams: 3, unit: "st", kcal: 80, carbs: 0.4, protein: 7, fat: 5.7 },
        { name: "Salz", grams: 0.25, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Vollkornbrot", grams: 80, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Avocado", grams: 70, kcal: 160, carbs: 1, protein: 2, fat: 15 },
        { name: "Schnittlauch", grams: 5, kcal: 30, carbs: 1.9, protein: 3.3, fat: 0.7 }
      ],
      steps: "1. Eier verquirlen und mit ¼ TL Salz und ¼ TL Pfeffer würzen.\n2. Bei mittlerer Hitze langsam stocken lassen, bis die Masse gerade fest ist – zu heiß und das Rührei wird trocken.\n3. Vollkornbrot toasten.\n4. Avocado darauf zerdrücken.\n5. Rührei daraufgeben und mit gehacktem Schnittlauch bestreuen." },

    { id: "rotes-linsen-dal", name: "Rotes Linsen-Dal mit Reis",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "rotes-linsen-dal.webp",
      nutrition: { kcal: 666, carbs: 101, protein: 27, fat: 14 },
      ingredients: [
        { name: "Basmatireis, roh", grams: 60, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Ingwer", grams: 8, kcal: 80, carbs: 15, protein: 1.8, fat: 0.8 },
        { name: "Knoblauch", grams: 5, kcal: 140, carbs: 28, protein: 6, fat: 0.5 },
        { name: "Kurkuma, gemahlen", grams: 1, unit: "tl", kcal: 9, carbs: 2, protein: 0.3, fat: 0.1 },
        { name: "Kreuzkümmel, gemahlen", grams: 1, unit: "tl", kcal: 8, carbs: 0.9, protein: 0.4, fat: 0.5 },
        { name: "Rote Linsen, roh", grams: 70, kcal: 350, carbs: 52, protein: 24, fat: 1.5 },
        { name: "Passierte Tomaten", grams: 150, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Kokosmilch", grams: 60, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 }
      ],
      steps: "1. Reis nach Packungsangabe aufsetzen.\n2. Zwiebel, Ingwer und Knoblauch fein hacken und in einem Topf glasig anschwitzen.\n3. 1 TL Kurkuma und 1 TL Kreuzkümmel kurz mitrösten, bis es duftet.\n4. Linsen, passierte Tomaten und Kokosmilch zugeben.\n5. 15–20 Min. köcheln, bis die Linsen zerfallen.\n6. Mit ½ TL Salz abschmecken und mit dem Reis anrichten." },

    { id: "haehnchen-bowl-brokkoli", name: "Hähnchen-Bowl mit Brokkoli und Reis",
      category: "Hauptgericht", time: 30, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "haehnchen-bowl-brokkoli.webp", photo: "rice",
      nutrition: { kcal: 672, carbs: 76, protein: 58, fat: 14 },
      ingredients: [
        { name: "Basmatireis, roh", grams: 80, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Hähnchenbrustfilet", grams: 180, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Paprikapulver", grams: 1, unit: "tl", kcal: 6, carbs: 1.3, protein: 0.3, fat: 0.3 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Sesamöl", grams: 10, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        { name: "Brokkoli", grams: 200, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Sojasoße", grams: 15, unit: "ml", kcal: 60, carbs: 5, protein: 8, fat: 0 }
      ],
      steps: "1. Reis nach Packungsangabe garen.\n2. Hähnchen würfeln und mit 1 TL Paprikapulver und ½ TL Salz würzen.\n3. Sesamöl erhitzen und das Fleisch scharf anbraten, bis es innen 75 °C erreicht – kein rosa Fleisch mehr, der Saft tritt klar aus.\n4. Brokkoliröschen und Karottenscheiben 4–5 Min. dämpfen, bis sie bissfest sind.\n5. Reis, Gemüse und Hähnchen in einer Schüssel anrichten.\n6. Mit Sojasoße beträufeln." },

    { id: "ofen-feta-kichererbsen", name: "Ofen-Feta mit Kichererbsen und Tomaten",
      category: "Hauptgericht", time: 30, tags: ["vegetarisch", "glutenfrei"], mealPrep: true, img: "ofen-feta-kichererbsen.webp", photo: "casserole",
      nutrition: { kcal: 659, carbs: 42, protein: 31, fat: 38 },
      ingredients: [
        { name: "Kichererbsen, Dose", grams: 200, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Kirschtomaten", grams: 200, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Oregano, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.7, protein: 0.1, fat: 0.1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Feta", grams: 100, kcal: 265, carbs: 1, protein: 14, fat: 22 }
      ],
      steps: "1. Ofen auf 200 °C Ober-/Unterhitze vorheizen.\n2. Kichererbsen abspülen und abtropfen lassen.\n3. Kichererbsen, Kirschtomaten und die in Spalten geschnittene Zwiebel in eine Auflaufform geben.\n4. Mit Olivenöl, 1 TL Oregano, ½ TL Salz und ¼ TL Pfeffer mischen.\n5. Feta in die Mitte setzen.\n6. 25 Min. backen, bis die Tomaten aufplatzen.\n7. Alles grob verrühren – der zerfallende Feta bindet dabei die Sauce." },

    { id: "tofu-gemuesepfanne", name: "Tofu-Gemüsepfanne mit Reisnudeln",
      category: "Hauptgericht", time: 20, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "tofu-gemuesepfanne.webp",
      nutrition: { kcal: 696, carbs: 63, protein: 40, fat: 29 },
      ingredients: [
        { name: "Reisnudeln, roh", grams: 55, kcal: 360, carbs: 82, protein: 7, fat: 0.6 },
        { name: "Räuchertofu", grams: 180, kcal: 165, carbs: 1, protein: 17, fat: 10 },
        { name: "Sesamöl", grams: 10, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        { name: "Paprika", grams: 150, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Zuckerschoten", grams: 100, kcal: 42, carbs: 5, protein: 3, fat: 0.2 },
        { name: "Ingwer", grams: 8, kcal: 80, carbs: 15, protein: 1.8, fat: 0.8 },
        { name: "Sojasoße, glutenfrei", grams: 15, unit: "ml", kcal: 60, carbs: 5, protein: 8, fat: 0 }
      ],
      steps: "1. Reisnudeln nach Packungsangabe einweichen.\n2. Tofu würfeln.\n3. Sesamöl stark erhitzen und den Tofu rundum knusprig braten.\n4. Paprikastreifen und Zuckerschoten zugeben und 3–4 Min. mitbraten.\n5. Geriebenen Ingwer unterrühren.\n6. Nudeln unterheben und mit Sojasoße abschmecken." },

    { id: "haehnchen-zucchini-feta", name: "Hähnchen-Zucchini-Pfanne mit Feta",
      category: "Hauptgericht", time: 20, tags: ["highprotein", "lowcarb", "glutenfrei"], mealPrep: true, img: "haehnchen-zucchini-feta.webp", photo: "chicken",
      nutrition: { kcal: 504, carbs: 10, protein: 58, fat: 25 },
      ingredients: [
        { name: "Hähnchenbrustfilet", grams: 200, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Zucchini", grams: 250, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Kirschtomaten", grams: 100, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Oregano, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.7, protein: 0.1, fat: 0.1 },
        { name: "Feta", grams: 50, kcal: 265, carbs: 1, protein: 14, fat: 22 }
      ],
      steps: "1. Hähnchen würfeln und mit ½ TL Salz und ¼ TL Pfeffer würzen.\n2. Olivenöl in einer großen Pfanne erhitzen und das Fleisch scharf anbraten, bis es innen 75 °C hat – kein rosa Fleisch mehr, der Saft tritt klar aus.\n3. Zucchini in Halbmonde schneiden, zugeben und 5 Min. mitbraten.\n4. Kirschtomaten halbieren und kurz mitziehen lassen.\n5. 1 TL Oregano unterrühren und die Pfanne vom Herd nehmen.\n6. Feta darüberbröseln." },

    { id: "blumenkohl-curry-tofu", name: "Blumenkohl-Curry mit Tofu",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "lowcarb", "glutenfrei", "laktosefrei", "highprotein"], mealPrep: true, img: "blumenkohl-curry-tofu.webp",
      nutrition: { kcal: 539, carbs: 18, protein: 43, fat: 32 },
      ingredients: [
        { name: "Räuchertofu", grams: 180, kcal: 165, carbs: 1, protein: 17, fat: 10 },
        { name: "Blumenkohl", grams: 300, kcal: 25, carbs: 3, protein: 2.5, fat: 0.3 },
        { name: "Currypaste, rot", grams: 20, kcal: 100, carbs: 10, protein: 3, fat: 6 },
        { name: "Ingwer", grams: 8, kcal: 80, carbs: 15, protein: 1.8, fat: 0.8 },
        { name: "Kokosmilch", grams: 60, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Spinat, frisch", grams: 100, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        { name: "Limettensaft", grams: 15, unit: "ml", kcal: 25, carbs: 8, protein: 0.4, fat: 0.2 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 }
      ],
      steps: "1. Tofu würfeln und in einem Topf rundum knusprig anbraten, dann herausnehmen.\n2. Blumenkohl in Röschen teilen.\n3. Currypaste und geriebenen Ingwer im selben Topf kurz anrösten.\n4. Blumenkohl zugeben und mitrösten.\n5. Mit Kokosmilch ablöschen und 10 Min. köcheln, bis der Blumenkohl weich ist.\n6. Spinat und Tofu unterheben.\n7. Mit Limettensaft und ½ TL Salz abschmecken." },

    { id: "skyr-beeren-nuesse", name: "Skyr mit Beeren und Walnüssen",
      category: "Snack", time: 3, tags: ["vegetarisch", "highprotein", "glutenfrei"], mealPrep: false, img: "skyr-beeren-nuesse.webp",
      nutrition: { kcal: 251, carbs: 13, protein: 25, fat: 10 },
      ingredients: [
        { name: "Skyr, natur", grams: 200, kcal: 63, carbs: 4, protein: 11, fat: 0.2 },
        { name: "Himbeeren", grams: 80, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Walnüsse", grams: 15, kcal: 650, carbs: 7, protein: 15, fat: 63 }
      ],
      steps: "1. Skyr in eine Schüssel geben.\n2. Himbeeren daraufsetzen.\n3. Walnüsse grob hacken und darüberstreuen." },

    { id: "quark-haferflocken-banane", name: "Quark-Haferflocken-Schale mit Banane",
      category: "Frühstück", time: 5, tags: ["vegetarisch", "highprotein"], mealPrep: true, img: "quark-haferflocken-banane.webp",
      nutrition: { kcal: 518, carbs: 65, protein: 40, fat: 9 },
      ingredients: [
        { name: "Magerquark", grams: 250, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Haferflocken", grams: 50, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Banane", grams: 120, kcal: 90, carbs: 20, protein: 1.1, fat: 0.3 },
        { name: "Leinsamen", grams: 10, kcal: 530, carbs: 3, protein: 24, fat: 42 },
        { name: "Zimt, gemahlen", grams: 0.5, unit: "tl", kcal: 6, carbs: 2.1, protein: 0.1, fat: 0.1 }
      ],
      steps: "1. Magerquark mit den Haferflocken verrühren.\n2. Einen Schluck Wasser oder Milch untermischen – ohne Flüssigkeit wird die Schale zu fest.\n3. Banane in Scheiben schneiden und auflegen.\n4. Mit Leinsamen und ½ TL Zimt bestreuen." },

    { id: "protein-pancakes-skyr", name: "Protein-Pancakes mit Skyr und Beeren",
      category: "Frühstück", time: 15, tags: ["vegetarisch", "highprotein"], mealPrep: false, img: "protein-pancakes-skyr.webp",
      nutrition: { kcal: 496, carbs: 51, protein: 43, fat: 11 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Eiklar", grams: 150, kcal: 52, carbs: 0.7, protein: 11, fat: 0.2 },
        { name: "Ei, Größe M", grams: 1, unit: "st", kcal: 80, carbs: 0.4, protein: 7, fat: 5.7 },
        { name: "Backpulver", grams: 1, unit: "tl", kcal: 4, carbs: 2.3, protein: 0, fat: 0 },
        { name: "Vanilleextrakt", grams: 1, unit: "tl", kcal: 12, carbs: 0.5, protein: 0, fat: 0 },
        { name: "Salz", grams: 0.25, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Skyr, natur", grams: 100, kcal: 63, carbs: 4, protein: 11, fat: 0.2 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 }
      ],
      steps: "1. Haferflocken fein mahlen.\n2. Eiklar, Ei, 1 TL Backpulver, 1 TL Vanilleextrakt und ¼ TL Salz zugeben und zu einem dickflüssigen Teig verrühren.\n3. Teig 5 Min. quellen lassen.\n4. Pfanne bei mittlerer Hitze erhitzen und kleine Pancakes 2–3 Min. je Seite backen, bis die Ränder stocken – zu heiß und sie werden außen dunkel, bevor die Mitte fest ist.\n5. Mit Skyr und Heidelbeeren anrichten." },

    { id: "tofu-ruehrei-vollkornbrot", name: "Tofu-Rührei auf Vollkornbrot",
      category: "Frühstück", time: 10, tags: ["vegan", "vegetarisch", "highprotein", "laktosefrei"], mealPrep: false, img: "tofu-ruehrei-vollkornbrot.webp",
      nutrition: { kcal: 445, carbs: 25, protein: 34, fat: 22 },
      ingredients: [
        { name: "Tofu, natur", grams: 200, kcal: 130, carbs: 1, protein: 14, fat: 8 },
        { name: "Rapsöl", grams: 5, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Kurkuma, gemahlen", grams: 0.5, unit: "tl", kcal: 9, carbs: 2, protein: 0.3, fat: 0.1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Vollkornbrot", grams: 60, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Frühlingszwiebel", grams: 20, kcal: 32, carbs: 4.5, protein: 1.8, fat: 0.2 },
        { name: "Schnittlauch", grams: 5, kcal: 30, carbs: 1.9, protein: 3.3, fat: 0.7 }
      ],
      steps: "1. Tofu mit der Gabel grob zerdrücken – nicht pürieren, die Struktur macht den Unterschied.\n2. Rapsöl erhitzen und den Tofu 4–5 Min. braten.\n3. Mit ½ TL Kurkuma, ½ TL Salz und ¼ TL Pfeffer würzen.\n4. Vollkornbrot toasten.\n5. Tofu auf dem Brot anrichten.\n6. Frühlingszwiebel in Ringe schneiden und mit dem Schnittlauch darüberstreuen." },

    { id: "chia-pudding-soja-beeren", name: "Chia-Pudding mit Sojadrink und Beeren",
      category: "Frühstück", time: 5, tags: ["vegan", "vegetarisch", "highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "chia-pudding-soja-beeren.webp",
      nutrition: { kcal: 310, carbs: 11, protein: 25, fat: 14 },
      ingredients: [
        { name: "Chiasamen", grams: 25, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        { name: "Sojadrink, ungesüßt", grams: 250, unit: "ml", kcal: 39, carbs: 0.6, protein: 3.3, fat: 1.9 },
        { name: "Erbsenprotein-Pulver", grams: 15, kcal: 380, carbs: 5, protein: 80, fat: 6 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 }
      ],
      steps: "1. Chiasamen, Sojadrink und Erbsenprotein-Pulver verrühren.\n2. Nach 5 Min. noch einmal umrühren – sonst setzen sich die Samen am Boden ab.\n3. Über Nacht in den Kühlschrank stellen.\n4. Am Morgen die Heidelbeeren daraufgeben." },

    { id: "ofenlachs-suesskartoffel", name: "Ofenlachs mit Süßkartoffeln und Brokkoli",
      category: "Hauptgericht", time: 35, tags: ["glutenfrei", "laktosefrei"], mealPrep: true, img: "ofenlachs-suesskartoffel.webp", photo: "fish",
      nutrition: { kcal: 661, carbs: 56, protein: 40, fat: 30 },
      ingredients: [
        { name: "Süßkartoffeln", grams: 250, kcal: 86, carbs: 20, protein: 1.6, fat: 0.1 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Lachsfilet", grams: 150, kcal: 200, carbs: 0, protein: 20, fat: 13 },
        { name: "Brokkoli", grams: 150, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Zitronensaft", grams: 15, unit: "ml", kcal: 22, carbs: 6, protein: 0.4, fat: 0.2 }
      ],
      steps: "1. Ofen auf 200 °C Ober-/Unterhitze vorheizen und ein Blech mit Backpapier auslegen.\n2. Süßkartoffeln würfeln, mit Olivenöl, ½ TL Salz und ¼ TL Pfeffer mischen und 20 Min. rösten.\n3. Lachs auf das Blech legen und weitere 12 Min. garen, bis er innen 62 °C erreicht – er lässt sich dann mit der Gabel in Segmente teilen.\n4. Brokkoli in Röschen teilen und 5 Min. dämpfen.\n5. Alles anrichten und den Lachs mit Zitronensaft beträufeln." },

    { id: "putenpfanne-vollkornnudeln", name: "Putenpfanne mit Vollkornnudeln",
      category: "Hauptgericht", time: 25, tags: ["highprotein"], mealPrep: true, img: "putenpfanne-vollkornnudeln.webp",
      nutrition: { kcal: 588, carbs: 51, protein: 58, fat: 15 },
      ingredients: [
        { name: "Vollkornnudeln, roh", grams: 70, kcal: 335, carbs: 62, protein: 14, fat: 2.5 },
        { name: "Putenbrustfilet", grams: 180, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Champignons", grams: 150, kcal: 22, carbs: 0.6, protein: 2.7, fat: 0.3 },
        { name: "Paprika, rot", grams: 100, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Thymian, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.6, protein: 0.1, fat: 0.1 }
      ],
      steps: "1. Vollkornnudeln bissfest kochen.\n2. Putenbrustfilet in Streifen schneiden und mit ½ TL Salz und ¼ TL Pfeffer würzen.\n3. Olivenöl heiß werden lassen und die Pute scharf anbraten, bis sie innen 75 °C hat – kein rosa Fleisch mehr, der Saft tritt klar aus.\n4. Pute herausnehmen.\n5. Champignons und Paprika in derselben Pfanne braten, bis die Flüssigkeit verdampft ist.\n6. 1 TL Thymian unterrühren.\n7. Nudeln und Pute zurück in die Pfanne geben und einmal durchschwenken." },

    { id: "chili-rinderhack-bohnen", name: "Chili mit Rinderhack und Kidneybohnen",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "chili-rinderhack-bohnen.webp",
      nutrition: { kcal: 560, carbs: 47, protein: 50, fat: 16 },
      ingredients: [
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Rapsöl", grams: 5, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Rinderhackfleisch, mager", grams: 150, kcal: 130, carbs: 0, protein: 21, fat: 5 },
        { name: "Kreuzkümmel, gemahlen", grams: 1, unit: "tl", kcal: 8, carbs: 0.9, protein: 0.4, fat: 0.5 },
        { name: "Paprikapulver", grams: 1, unit: "tl", kcal: 6, carbs: 1.3, protein: 0.3, fat: 0.3 },
        { name: "Chiliflocken", grams: 0.5, unit: "tl", kcal: 6, carbs: 1.1, protein: 0.2, fat: 0.3 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Passierte Tomaten", grams: 200, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Kidneybohnen, Dose", grams: 150, kcal: 110, carbs: 14, protein: 8, fat: 0.6 },
        { name: "Mais, Dose", grams: 60, kcal: 90, carbs: 16, protein: 3, fat: 1.2 }
      ],
      steps: "1. Zwiebeln würfeln und in Rapsöl glasig anschwitzen.\n2. Rinderhackfleisch zugeben und krümelig anbraten, bis nichts mehr rot ist.\n3. 1 TL Kreuzkümmel, 1 TL Paprikapulver, ½ TL Chiliflocken und ½ TL Salz kurz mitrösten.\n4. Passierte Tomaten, abgespülte Kidneybohnen und Mais zugeben.\n5. 20 Min. offen köcheln lassen, bis das Chili sämig ist." },

    { id: "linsen-bolognese-vollkorn", name: "Linsen-Bolognese mit Vollkornnudeln",
      category: "Hauptgericht", time: 30, tags: ["vegan", "vegetarisch", "laktosefrei"], mealPrep: true, img: "linsen-bolognese-vollkorn.webp",
      nutrition: { kcal: 653, carbs: 93, protein: 30, fat: 13 },
      ingredients: [
        { name: "Zwiebeln", grams: 60, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Knoblauch", grams: 5, kcal: 140, carbs: 28, protein: 6, fat: 0.5 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Linsen, roh", grams: 70, kcal: 340, carbs: 50, protein: 24, fat: 1.5 },
        { name: "Passierte Tomaten", grams: 200, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Oregano, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.7, protein: 0.1, fat: 0.1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Vollkornnudeln, roh", grams: 60, kcal: 335, carbs: 62, protein: 14, fat: 2.5 }
      ],
      steps: "1. Zwiebel, Karotte und Knoblauch fein würfeln.\n2. Olivenöl erhitzen und das Gemüse darin anschwitzen.\n3. Linsen und passierte Tomaten zugeben und mit Wasser auffüllen, bis alles bedeckt ist.\n4. 25 Min. köcheln, bis die Linsen weich sind.\n5. Mit 1 TL Oregano, ½ TL Salz und ¼ TL Pfeffer abschmecken.\n6. Vollkornnudeln bissfest garen und die Sauce daraufgeben." },

    { id: "haehnchen-brokkoli-auflauf", name: "Hähnchen-Brokkoli-Auflauf",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "lowcarb", "glutenfrei"], mealPrep: true, img: "haehnchen-brokkoli-auflauf.webp",
      nutrition: { kcal: 539, carbs: 13, protein: 72, fat: 20 },
      ingredients: [
        { name: "Brokkoli", grams: 300, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Hähnchenbrustfilet", grams: 200, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Frischkäse, light", grams: 80, kcal: 145, carbs: 4, protein: 9, fat: 10 },
        { name: "Muskat, gemahlen", grams: 0.25, unit: "tl", kcal: 12, carbs: 1.1, protein: 0.1, fat: 0.8 },
        { name: "Gouda, mittelalt", grams: 30, kcal: 355, carbs: 0, protein: 25, fat: 28 }
      ],
      steps: "1. Ofen auf 200 °C Ober-/Unterhitze vorheizen.\n2. Brokkoli in Röschen teilen und 4 Min. vorgaren – roh bleibt er im Ofen hart.\n3. Hähnchen würfeln und mit ½ TL Salz und ¼ TL Pfeffer würzen.\n4. Brokkoli und Hähnchen in eine Auflaufform geben.\n5. Frischkäse mit etwas Wasser glattrühren, ¼ TL Muskat einrühren und darübergießen.\n6. Gouda darüberreiben.\n7. 20 Min. backen, bis das Hähnchen innen 75 °C hat und der Käse Farbe nimmt." },

    { id: "garnelen-zucchini-tomaten", name: "Garnelen mit Zucchini und Kirschtomaten",
      category: "Hauptgericht", time: 20, tags: ["highprotein", "lowcarb", "glutenfrei", "laktosefrei"], mealPrep: false, img: "garnelen-zucchini-tomaten.webp", photo: "seafood",
      nutrition: { kcal: 349, carbs: 12, protein: 44, fat: 14 },
      ingredients: [
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Zucchini", grams: 250, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Kirschtomaten", grams: 150, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Knoblauch", grams: 5, kcal: 140, carbs: 28, protein: 6, fat: 0.5 },
        { name: "Chiliflocken", grams: 0.5, unit: "tl", kcal: 6, carbs: 1.1, protein: 0.2, fat: 0.3 },
        { name: "Garnelen", grams: 200, kcal: 85, carbs: 0, protein: 19, fat: 1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Petersilie", grams: 5, kcal: 36, carbs: 3, protein: 3, fat: 0.8 }
      ],
      steps: "1. Olivenöl in einer Pfanne heiß werden lassen.\n2. Zucchini in Streifen schneiden und 3 Min. braten.\n3. Kirschtomaten halbieren und kurz mitziehen lassen.\n4. Gehackten Knoblauch und ½ TL Chiliflocken zugeben.\n5. Garnelen erst zum Schluss einlegen und 2 Min. garen, bis sie durchgehend rosa und undurchsichtig sind – länger und sie werden zäh.\n6. Mit ½ TL Salz abschmecken und mit gehackter Petersilie bestreuen." },

    { id: "kichererbsen-curry-spinat", name: "Kichererbsen-Curry mit Spinat und Reis",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "kichererbsen-curry-spinat.webp",
      nutrition: { kcal: 638, carbs: 83, protein: 27, fat: 19 },
      ingredients: [
        { name: "Basmatireis, roh", grams: 45, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Zwiebeln", grams: 60, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Ingwer", grams: 8, kcal: 80, carbs: 15, protein: 1.8, fat: 0.8 },
        { name: "Knoblauch", grams: 5, kcal: 140, carbs: 28, protein: 6, fat: 0.5 },
        { name: "Currypulver", grams: 2, unit: "tl", kcal: 7, carbs: 1.2, protein: 0.3, fat: 0.3 },
        { name: "Kichererbsen, Dose", grams: 200, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Passierte Tomaten", grams: 150, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Kokosmilch", grams: 60, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Spinat, frisch", grams: 150, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 }
      ],
      steps: "1. Reis nach Packungsangabe aufsetzen.\n2. Zwiebel, Ingwer und Knoblauch fein hacken und anschwitzen.\n3. 2 TL Currypulver kurz mitrösten, bis es duftet.\n4. Kichererbsen, passierte Tomaten und Kokosmilch zugeben und 10 Min. köcheln.\n5. Spinat unterheben – er fällt in einer Minute zusammen.\n6. Mit ½ TL Salz abschmecken und mit dem Reis anrichten." },

    { id: "quinoa-bowl-edamame", name: "Quinoa-Bowl mit Edamame und Avocado",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "quinoa-bowl-edamame.webp",
      nutrition: { kcal: 724, carbs: 66, protein: 37, fat: 32 },
      ingredients: [
        { name: "Quinoa, roh", grams: 70, kcal: 368, carbs: 58, protein: 14, fat: 6 },
        { name: "Edamame", grams: 200, kcal: 120, carbs: 8, protein: 11, fat: 5 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Avocado", grams: 50, kcal: 160, carbs: 1, protein: 2, fat: 15 },
        { name: "Sesamöl", grams: 5, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        { name: "Limettensaft", grams: 15, unit: "ml", kcal: 25, carbs: 8, protein: 0.4, fat: 0.2 },
        { name: "Sojasoße, glutenfrei", grams: 15, unit: "ml", kcal: 60, carbs: 5, protein: 8, fat: 0 },
        { name: "Sesam", grams: 10, kcal: 573, carbs: 12, protein: 18, fat: 50 }
      ],
      steps: "1. Quinoa heiß abspülen, bis das Wasser klar bleibt – die Saponine an der Schale schmecken sonst bitter.\n2. Quinoa mit der doppelten Menge Wasser 15 Min. garen.\n3. Edamame 3 Min. blanchieren.\n4. Karotte fein raspeln.\n5. Quinoa, Edamame und Karotte in einer Schüssel schichten und die Avocado in Scheiben darauflegen.\n6. Mit Sesamöl, Limettensaft und Sojasoße beträufeln und mit Sesam bestreuen." },

    { id: "huettenkaese-vollkornbrot", name: "Hüttenkäse auf Vollkornbrot mit Radieschen",
      category: "Snack", time: 5, tags: ["vegetarisch", "highprotein"], mealPrep: false, img: "huettenkaese-vollkornbrot.webp", photo: "sandwich",
      nutrition: { kcal: 286, carbs: 27, protein: 25, fat: 7 },
      ingredients: [
        { name: "Vollkornbrot", grams: 60, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Hüttenkäse", grams: 150, kcal: 100, carbs: 3, protein: 13, fat: 4 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Radieschen", grams: 50, kcal: 15, carbs: 2, protein: 1, fat: 0.1 },
        { name: "Schnittlauch", grams: 5, kcal: 30, carbs: 1.9, protein: 3.3, fat: 0.7 }
      ],
      steps: "1. Vollkornbrot toasten.\n2. Hüttenkäse daraufgeben und mit ¼ TL Pfeffer würzen.\n3. Radieschen in dünne Scheiben schneiden und auflegen.\n4. Schnittlauch hacken und darüberstreuen." },

    { id: "edamame-sesam-snack", name: "Edamame mit Sesam und Meersalz",
      category: "Snack", time: 10, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: false, img: "edamame-sesam-snack.webp", photo: "salad",
      nutrition: { kcal: 344, carbs: 18, protein: 24, fat: 20 },
      ingredients: [
        { name: "Edamame", grams: 200, kcal: 120, carbs: 8, protein: 11, fat: 5 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Sesamöl", grams: 5, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        { name: "Sesam", grams: 10, kcal: 573, carbs: 12, protein: 18, fat: 50 },
        { name: "Chiliflocken", grams: 0.5, unit: "tl", kcal: 6, carbs: 1.1, protein: 0.2, fat: 0.3 }
      ],
      steps: "1. Wasser mit ½ TL Salz aufkochen.\n2. Edamame darin 4 Min. kochen und abgießen.\n3. Mit Sesamöl schwenken.\n4. Mit Sesam und ½ TL Chiliflocken bestreuen.\n5. Die Bohnen aus der Schote essen." },

    { id: "thunfisch-quark-dip", name: "Thunfisch-Quark-Dip mit Gurke",
      category: "Snack", time: 5, tags: ["highprotein", "glutenfrei"], mealPrep: false, img: "thunfisch-quark-dip.webp", photo: "fish",
      nutrition: { kcal: 224, carbs: 9, protein: 43, fat: 2 },
      ingredients: [
        { name: "Thunfisch in Wasser, Dose", grams: 100, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Magerquark", grams: 150, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Zitronensaft", grams: 15, unit: "ml", kcal: 22, carbs: 6, protein: 0.4, fat: 0.2 },
        { name: "Salz", grams: 0.25, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Dill", grams: 5, kcal: 43, carbs: 3, protein: 3.5, fat: 1.1 },
        { name: "Gurke", grams: 100, kcal: 12, carbs: 1.8, protein: 0.6, fat: 0.1 }
      ],
      steps: "1. Thunfisch gut abtropfen lassen.\n2. Mit dem Magerquark verrühren.\n3. Mit Zitronensaft, ¼ TL Salz und ¼ TL Pfeffer abschmecken.\n4. Dill hacken und unterrühren.\n5. Gurke in Stifte schneiden und zum Dippen dazustellen." },

    { id: "schoko-protein-quark", name: "Schoko-Protein-Quark",
      category: "Dessert", time: 5, tags: ["vegetarisch", "highprotein", "glutenfrei"], mealPrep: false, img: "schoko-protein-quark.webp", photo: "cake",
      nutrition: { kcal: 347, carbs: 23, protein: 45, fat: 8 },
      ingredients: [
        { name: "Magerquark", grams: 250, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Proteinpulver, Whey", grams: 15, kcal: 380, carbs: 5, protein: 78, fat: 6 },
        { name: "Backkakao", grams: 10, kcal: 350, carbs: 11, protein: 20, fat: 21 },
        { name: "Honig", grams: 10, kcal: 305, carbs: 75, protein: 0.4, fat: 0 },
        { name: "Zartbitterschokolade 70 %", grams: 10, kcal: 570, carbs: 33, protein: 8, fat: 42 }
      ],
      steps: "1. Magerquark mit einem Schluck Wasser cremig rühren.\n2. Proteinpulver und 10 g Backkakao einrühren – erst das Wasser, dann das Pulver, sonst klumpt es.\n3. Mit 10 g Honig süßen.\n4. Zartbitterschokolade grob hacken und darüberstreuen." },

    { id: "dattel-nuss-bissen", name: "Dattel-Nuss-Bissen mit Kakao",
      category: "Dessert", time: 15, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "dattel-nuss-bissen.webp", photo: "cake",
      nutrition: { kcal: 318, carbs: 34, protein: 7, fat: 17 },
      ingredients: [
        { name: "Datteln, getrocknet", grams: 40, kcal: 280, carbs: 65, protein: 2.5, fat: 0.4 },
        { name: "Cashewkerne", grams: 25, kcal: 560, carbs: 27, protein: 18, fat: 44 },
        { name: "Backkakao", grams: 5, kcal: 350, carbs: 11, protein: 20, fat: 21 },
        { name: "Salz", grams: 0.25, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Kokosraspeln", grams: 8, kcal: 600, carbs: 6, protein: 6, fat: 57 }
      ],
      steps: "1. Datteln und Cashewkerne im Mixer zu einer klebrigen Masse zerkleinern.\n2. 5 g Backkakao und ¼ TL Salz untermischen.\n3. Kleine Kugeln formen.\n4. In Kokosraspeln wälzen und 30 Min. kalt stellen." },

    { id: "ofengemuese-blech", name: "Ofengemüse vom Blech",
      category: "Beilage", time: 30, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "ofengemuese-blech.webp",
      nutrition: { kcal: 232, carbs: 22, protein: 6, fat: 12 },
      ingredients: [
        { name: "Zucchini", grams: 200, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Paprika, rot", grams: 150, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Karotten", grams: 100, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Rosmarin, getrocknet", grams: 1, unit: "tl", kcal: 4, carbs: 0.8, protein: 0.1, fat: 0.2 },
        { name: "Thymian, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.6, protein: 0.1, fat: 0.1 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 }
      ],
      steps: "1. Ofen auf 200 °C Ober-/Unterhitze vorheizen.\n2. Zucchini, Paprika und Karotten in gleich große Stücke schneiden.\n3. Mit Olivenöl, 1 TL Rosmarin, 1 TL Thymian, ½ TL Salz und ¼ TL Pfeffer mischen.\n4. Auf dem Blech in einer Lage verteilen – gestapelt dämpft das Gemüse, statt zu rösten.\n5. 25 Min. backen, bis die Ränder bräunen." },

    { id: "quinoa-salat-kichererbsen", name: "Quinoa-Salat mit Kichererbsen",
      category: "Beilage", time: 20, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "quinoa-salat-kichererbsen.webp",
      nutrition: { kcal: 378, carbs: 45, protein: 14, fat: 13 },
      ingredients: [
        { name: "Quinoa, roh", grams: 40, kcal: 368, carbs: 58, protein: 14, fat: 6 },
        { name: "Gurke", grams: 100, kcal: 12, carbs: 1.8, protein: 0.6, fat: 0.1 },
        { name: "Kirschtomaten", grams: 100, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Kichererbsen, Dose", grams: 100, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Olivenöl", grams: 8, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Zitronensaft", grams: 15, unit: "ml", kcal: 22, carbs: 6, protein: 0.4, fat: 0.2 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Petersilie", grams: 5, kcal: 36, carbs: 3, protein: 3, fat: 0.8 }
      ],
      steps: "1. Quinoa heiß abspülen und 15 Min. garen.\n2. Vollständig auskühlen lassen – warm eingerührt wird der Salat matschig.\n3. Gurke würfeln und Kirschtomaten halbieren.\n4. Quinoa, Gemüse und abgespülte Kichererbsen mischen.\n5. Mit Olivenöl, Zitronensaft, ½ TL Salz und ¼ TL Pfeffer abschmecken.\n6. Petersilie hacken und untermengen." },

    { id: "beeren-protein-shake-hafer", name: "Beeren-Protein-Shake mit Hafermilch",
      category: "Getränk", time: 5, tags: ["vegan", "vegetarisch", "highprotein", "laktosefrei"], mealPrep: false, img: "beeren-protein-shake-hafer.webp",
      nutrition: { kcal: 336, carbs: 26, protein: 30, fat: 11 },
      ingredients: [
        { name: "Hafermilch, ungesüßt", grams: 300, unit: "ml", kcal: 45, carbs: 6.5, protein: 0.8, fat: 1.5 },
        { name: "Erbsenprotein-Pulver", grams: 30, kcal: 380, carbs: 5, protein: 80, fat: 6 },
        { name: "Himbeeren", grams: 100, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Leinsamen", grams: 10, kcal: 530, carbs: 3, protein: 24, fat: 42 }
      ],
      steps: "1. Hafermilch, Erbsenprotein-Pulver, Himbeeren und Leinsamen in den Mixer geben.\n2. Mixen, bis keine Stücke mehr zu sehen sind.\n3. Für einen dickeren Shake gefrorene Himbeeren nehmen." },

    { id: "gruener-smoothie-spinat", name: "Grüner Smoothie mit Spinat und Banane",
      category: "Getränk", time: 5, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: false, img: "gruener-smoothie-spinat.webp", photo: "drink",
      nutrition: { kcal: 217, carbs: 28, protein: 6, fat: 7 },
      ingredients: [
        { name: "Spinat, frisch", grams: 60, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        { name: "Mandelmilch, ungesüßt", grams: 250, unit: "ml", kcal: 15, carbs: 0.3, protein: 0.5, fat: 1.2 },
        { name: "Banane", grams: 120, kcal: 90, carbs: 20, protein: 1.1, fat: 0.3 },
        { name: "Chiasamen", grams: 10, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        { name: "Zitronensaft", grams: 15, unit: "ml", kcal: 22, carbs: 6, protein: 0.4, fat: 0.2 },
        { name: "Ingwer", grams: 8, kcal: 80, carbs: 15, protein: 1.8, fat: 0.8 }
      ],
      steps: "1. Spinat mit der Mandelmilch mixen, bis keine Blattstücke mehr zu sehen sind.\n2. Banane, Chiasamen, Zitronensaft und geriebenen Ingwer zugeben.\n3. Noch einmal kurz durchmixen." },

    // Die vier ehemaligen Beispiel-Meals (SEED). Sie sind am 15.08.2026 in den Katalog
    // gewandert, statt geloescht zu werden: Ihre Bilder lagen bereits im eingefrorenen Stil
    // vor, und das Rindersteak ist bis heute das einzige seiner Art im Rezeptbuch.
    // Die `id` ist bewusst der vorhandene Dateiname - so musste keine Datei umbenannt und
    // kein Eintrag im Herkunftsnachweis angefasst werden.
    // Zwei Dinge sind dabei geradegezogen worden: Das Oel stand im FREITEXT und fiel damit
    // aus jeder Rechnung (TROUBLESHOOTING 85), und die Zutatennamen trafen die FOODS-Tabelle
    // nicht ("Whey-Protein Vanille", "Beeren, gemischt"). Stueckangaben sind in Gramm
    // umgerechnet - eine halbe Paprika ist eine Schaetzung, 75 g sind eine Menge.
    { id: "protein-porridge-mit-beeren", name: "Protein-Porridge mit Beeren",
      category: "Frühstück", time: 10, tags: ["highprotein", "vegetarisch"], mealPrep: true,
      img: "protein-porridge-mit-beeren.webp",
      nutrition: { kcal: 564, carbs: 57, protein: 42, fat: 17 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Milch 1,5 %", grams: 250, unit: "ml", kcal: 64, carbs: 4.8, protein: 3.4, fat: 3.5 },
        { name: "Proteinpulver, Whey", grams: 30, kcal: 380, carbs: 5, protein: 78, fat: 6 },
        { name: "Heidelbeeren", grams: 50, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 },
        { name: "Himbeeren", grams: 50, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Chiasamen", grams: 5, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        { name: "Zimt, gemahlen", grams: 0.5, unit: "tl", kcal: 6, carbs: 2.1, protein: 0.1, fat: 0.1 }
      ],
      steps: "1. Haferflocken mit der Milch aufkochen.\n2. 3–4 Min. bei milder Hitze quellen lassen, bis der Porridge cremig bindet.\n3. Topf vom Herd nehmen und erst dann das Proteinpulver unterrühren – in der kochenden Masse flockt es.\n4. Heidelbeeren und Himbeeren auflegen.\n5. Mit Chiasamen und ½ TL Zimt bestreuen." },

    { id: "haehnchen-mit-pute-und-reis", name: "Hähnchen mit Pute und Reis",
      category: "Hauptgericht", time: 30, tags: ["highprotein", "laktosefrei"], mealPrep: true,
      img: "haehnchen-mit-pute-und-reis.webp",
      nutrition: { kcal: 616, carbs: 71, protein: 51, fat: 14 },
      ingredients: [
        { name: "Basmatireis, roh", grams: 80, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Hähnchenbrustfilet", grams: 100, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Putenbrustfilet", grams: 75, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Paprikapulver", grams: 1, unit: "tl", kcal: 6, carbs: 1.3, protein: 0.3, fat: 0.3 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Paprika, rot", grams: 75, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Zucchini", grams: 100, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Sojasoße", grams: 15, unit: "ml", kcal: 60, carbs: 5, protein: 8, fat: 0 }
      ],
      steps: "1. Reis nach Packungsangabe kochen.\n2. Hähnchen- und Putenbrust würfeln und mit 1 TL Paprikapulver, ½ TL Salz und ¼ TL Pfeffer würzen.\n3. Olivenöl stark erhitzen und das Fleisch scharf anbraten, bis es innen 75 °C hat – kein rosa Fleisch mehr, der Saft tritt klar aus.\n4. Paprika und Zucchini in Streifen schneiden und 3–4 Min. mitbraten.\n5. Mit Sojasoße ablöschen.\n6. Alles auf dem Reis anrichten." },

    { id: "rindersteak-mit-ofenkartoffeln", name: "Rindersteak mit Ofenkartoffeln",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: false,
      img: "rindersteak-mit-ofenkartoffeln.webp",
      nutrition: { kcal: 636, carbs: 51, protein: 56, fat: 22 },
      ingredients: [
        { name: "Kartoffeln", grams: 300, kcal: 70, carbs: 15, protein: 2, fat: 0.1 },
        { name: "Olivenöl", grams: 10, unit: "ml", kcal: 900, carbs: 0, protein: 0, fat: 100 },
        { name: "Rosmarin, getrocknet", grams: 1, unit: "tl", kcal: 4, carbs: 0.8, protein: 0.1, fat: 0.2 },
        { name: "Rumpsteak", grams: 200, kcal: 140, carbs: 0, protein: 22, fat: 5.5 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 },
        { name: "Brokkoli", grams: 150, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 }
      ],
      steps: "1. Ofen auf 200 °C Ober-/Unterhitze vorheizen.\n2. Kartoffeln würfeln, mit Olivenöl und 1 TL Rosmarin vermengen und 25 Min. rösten.\n3. Rumpsteak mit ½ TL Salz und ¼ TL Pfeffer würzen.\n4. In einer heißen Pfanne von jeder Seite 2–3 Min. braten.\n5. Steak 5 Min. ruhen lassen – sonst läuft der Saft beim Anschneiden aus.\n6. Brokkoli in Röschen teilen und 5 Min. dämpfen.\n7. Alles anrichten." },

    // "Getränk", nicht "Snack" (24.08.2026): Ueber CAT_TO_MEAL ist "Snack" exklusiv an den
    // Slot sn gebunden - der Shake war von Hand nirgendwo sonst planbar, obwohl ein Shake zum
    // Fruehstueck oder nach dem Training der Normalfall ist. Der zweite Shake im Katalog
    // (beeren-protein-shake-hafer) stand von Anfang an als "Getränk" da; das hier war die
    // Abweichung. Zwei gewollte Folgen: von Hand ueberall planbar (catFitsMeal laesst
    // Getraenke ueberall zu), und der Auto-Planer plant ihn NICHT mehr automatisch ein -
    // catPlanFitsMeal ist bewusst enger, seit der Planer vier Shakes ins Mittagessen legte.
    { id: "eiweissshake-mit-whey-und-milch", name: "Eiweißshake mit Whey und Milch",
      category: "Getränk", time: 5, tags: ["highprotein", "vegetarisch", "glutenfrei"], mealPrep: false,
      img: "eiweissshake-mit-whey-und-milch.webp",
      nutrition: { kcal: 414, carbs: 40, protein: 35, fat: 13 },
      ingredients: [
        { name: "Milch 1,5 %", grams: 300, unit: "ml", kcal: 64, carbs: 4.8, protein: 3.4, fat: 3.5 },
        { name: "Proteinpulver, Whey", grams: 30, kcal: 380, carbs: 5, protein: 78, fat: 6 },
        { name: "Banane", grams: 120, kcal: 90, carbs: 20, protein: 1.1, fat: 0.3 },
        { name: "Eiswürfel", grams: 100, kcal: 0, carbs: 0, protein: 0, fat: 0 }
      ],
      steps: "1. Milch, Proteinpulver, Banane und Eiswürfel in den Mixer geben.\n2. Cremig mixen." },


    // Gießteig, nicht Rollteig: Quark zu Mehl 200 : 44 = 4,55 - belegt durch die
    // Protein-Pizza-Familie (4,5-7,7, gebunden mit zwei Eiern), NICHT durch den klassischen
    // Quark-Öl-Teig (0,36-1,4, wird ausgerollt). Deshalb heißt es in Schritt 4
    // "verstreichen" und nicht "ausrollen" - die beiden Familien vertragen sich nicht.
    { id: "protein-pizza-schinken", name: "Protein-Pizza mit Schinken",
      category: "Hauptgericht", time: 35, tags: ["highprotein"], mealPrep: false,
      img: "protein-pizza-schinken.webp",
      nutrition: { kcal: 650, carbs: 49, protein: 69, fat: 19 },
      ingredients: [
        { name: "Magerquark", grams: 200, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Ei, Größe M", grams: 2, unit: "st", kcal: 80, carbs: 0.4, protein: 7, fat: 5.7 },
        { name: "Weizenmehl Type 405", grams: 44, kcal: 348, carbs: 72, protein: 10, fat: 1 },
        { name: "Backpulver", grams: 1, unit: "tl", kcal: 4, carbs: 2.3, protein: 0, fat: 0 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Passierte Tomaten", grams: 80, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Oregano, getrocknet", grams: 1, unit: "tl", kcal: 3, carbs: 0.7, protein: 0.1, fat: 0.1 },
        { name: "Kochschinken", grams: 60, kcal: 110, carbs: 1, protein: 19, fat: 3 },
        { name: "Mozzarella, light", grams: 60, kcal: 165, carbs: 1, protein: 22, fat: 8 },
        { name: "Rucola", grams: 20, kcal: 25, carbs: 2, protein: 2.6, fat: 0.7 }
      ],
      steps: "1. Ofen auf 220 °C Ober-/Unterhitze vorheizen, ein Blech mit Backpapier auslegen.\n2. Magerquark mit den Eiern glatt rühren.\n3. Mehl, 1 TL Backpulver und ½ TL Salz unterrühren, bis ein dickflüssiger Teig entsteht.\n4. Teig auf dem Blech zu einem runden Boden verstreichen, etwa einen halben Zentimeter dick.\n5. Boden 10–12 Min. vorbacken, bis die Oberfläche trocken ist und der Rand bräunt – ohne diesen Schritt weicht der Quarkboden unter der Sauce durch.\n6. Passierte Tomaten daraufstreichen und mit 1 TL Oregano bestreuen.\n7. Kochschinken in Streifen schneiden und auf der Sauce verteilen.\n8. Mozzarella darüberzupfen.\n9. Weitere 10–12 Min. backen, bis der Käse Farbe nimmt.\n10. Rucola nach dem Backen auflegen." },
    { id: "risotto-spargel", name: "Risotto mit grünem Spargel",
      category: "Hauptgericht", time: 35, tags: ["vegetarisch", "glutenfrei"], mealPrep: false,
      img: "risotto-spargel.webp",
      nutrition: { kcal: 596, carbs: 75, protein: 21, fat: 17 },
      ingredients: [
        { name: "Spargel", grams: 250, kcal: 20, carbs: 2, protein: 2, fat: 0.2 },
        { name: "Gemüsebrühe, zubereitet", grams: 260, unit: "ml", kcal: 5, carbs: 0.5, protein: 0.2, fat: 0.2 },
        { name: "Schalotte", grams: 40, kcal: 72, carbs: 14, protein: 2.5, fat: 0.1 },
        { name: "Butter", grams: 10, kcal: 740, carbs: 0.6, protein: 0.7, fat: 82 },
        { name: "Risottoreis, roh", grams: 80, kcal: 350, carbs: 77, protein: 7, fat: 0.9 },
        { name: "Weißwein", grams: 60, unit: "ml", kcal: 82, carbs: 2, protein: 0.1, fat: 0 },
        { name: "Parmesan", grams: 25, kcal: 400, carbs: 0, protein: 36, fat: 28 },
        { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 },
        { name: "Pfeffer, gemahlen", grams: 0.25, unit: "tl", kcal: 6, carbs: 1.5, protein: 0.2, fat: 0.1 }
      ],
      steps: "1. Spargel waschen, die holzigen Enden abschneiden und die Stangen in 3 cm lange Stücke schneiden.\n2. Gemüsebrühe erhitzen und heiß halten – kalte Brühe unterbricht den Garvorgang bei jedem Angießen.\n3. Schalotte fein würfeln und in der Hälfte der Butter glasig anschwitzen.\n4. Risottoreis zugeben und 2 Min. mitrösten, bis die Körner glasig sind.\n5. Mit Weißwein ablöschen und rühren, bis die Flüssigkeit aufgesogen ist.\n6. Eine Kelle heiße Brühe angießen und rühren, bis der Reis sie aufgenommen hat.\n7. So 18–20 Min. weiterarbeiten, bis der Reis außen cremig und innen noch bissfest ist.\n8. Die Spargelstücke nach der Hälfte dieser Zeit mitkochen lassen.\n9. Topf vom Herd nehmen, die restliche Butter und den geriebenen Parmesan unterrühren.\n10. Zugedeckt 2 Min. ruhen lassen.\n11. Mit ½ TL Salz und ¼ TL Pfeffer abschmecken." },
  ];
