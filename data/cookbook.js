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
  // Warum nicht der ganze Katalog direkt in die Sammlung: 34 fremde Meals im eigenen Bestand
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
      nutrition: { kcal: 449, carbs: 47, protein: 20, fat: 16 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Sojajoghurt, natur", grams: 200, kcal: 50, carbs: 1.5, protein: 4, fat: 2.5 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 },
        { name: "Erdnussbutter", grams: 15, kcal: 600, carbs: 12, protein: 25, fat: 50 },
        "Zimt"
      ],
      steps: "Haferflocken mit Sojajoghurt verrühren und über Nacht in den Kühlschrank stellen. Am Morgen Beeren und Erdnussmus daraufgeben, mit Zimt bestreuen." },

    { id: "rührei-avocadobrot", name: "Rührei mit Avocado auf Vollkornbrot",
      category: "Frühstück", time: 10, tags: ["vegetarisch"], mealPrep: false, img: "ruehrei-avocadobrot.webp",
      nutrition: { kcal: 520, carbs: 29, protein: 28, fat: 29 },
      ingredients: [
        { name: "Ei, Größe M", grams: 3, unit: "st", kcal: 80, carbs: 0.4, protein: 7, fat: 5.7 },
        { name: "Vollkornbrot", grams: 80, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Avocado", grams: 70, kcal: 160, carbs: 1, protein: 2, fat: 15 },
        "Schnittlauch, Salz, Pfeffer"
      ],
      steps: "Eier verquirlen, salzen und bei mittlerer Hitze langsam stocken lassen – so bleiben sie cremig. Brot toasten, Avocado darauf zerdrücken, Rührei daraufgeben und mit Schnittlauch bestreuen." },

    { id: "rotes-linsen-dal", name: "Rotes Linsen-Dal mit Reis",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "rotes-linsen-dal.webp",
      nutrition: { kcal: 636, carbs: 95, protein: 25, fat: 13 },
      ingredients: [
        { name: "Rote Linsen, roh", grams: 70, kcal: 350, carbs: 52, protein: 24, fat: 1.5 },
        { name: "Basmatireis, roh", grams: 60, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Kokosmilch", grams: 60, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Passierte Tomaten", grams: 150, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        "Ingwer, Knoblauch, Kurkuma, Kreuzkümmel, Salz"
      ],
      steps: "Zwiebel, Ingwer und Knoblauch anschwitzen, Gewürze kurz mitrösten. Linsen, Tomaten und Kokosmilch zugeben und 15–20 Min. köcheln, bis die Linsen zerfallen. Reis separat garen und dazu servieren." },

    { id: "haehnchen-bowl-brokkoli", name: "Hähnchen-Bowl mit Brokkoli und Reis",
      category: "Hauptgericht", time: 30, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "haehnchen-bowl-brokkoli.webp", photo: "rice",
      nutrition: { kcal: 656, carbs: 74, protein: 56, fat: 13 },
      ingredients: [
        { name: "Hähnchenbrustfilet", grams: 180, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Basmatireis, roh", grams: 80, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Brokkoli", grams: 200, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Sesamöl", grams: 10, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        "Sojasauce, Paprikapulver"
      ],
      steps: "Reis garen. Hähnchen würfeln, würzen und scharf anbraten. Brokkoli und Karotte 4–5 Min. dämpfen, damit sie bissfest bleiben. Alles in einer Schüssel anrichten und mit Sojasauce abschmecken." },

    { id: "ofen-feta-kichererbsen", name: "Ofen-Feta mit Kichererbsen und Tomaten",
      category: "Hauptgericht", time: 30, tags: ["vegetarisch", "glutenfrei"], mealPrep: true, img: "ofen-feta-kichererbsen.webp", photo: "casserole",
      nutrition: { kcal: 654, carbs: 41, protein: 30, fat: 37 },
      ingredients: [
        { name: "Feta", grams: 100, kcal: 265, carbs: 1, protein: 14, fat: 22 },
        { name: "Kichererbsen, Dose", grams: 200, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Kirschtomaten", grams: 200, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Oregano, Salz, Pfeffer"
      ],
      steps: "Kichererbsen, Tomaten und Zwiebel mit Öl und Oregano in eine Auflaufform geben, den Feta in die Mitte setzen. Bei 200 °C etwa 25 Min. backen, dann alles grob verrühren." },

    { id: "tofu-gemuesepfanne", name: "Tofu-Gemüsepfanne mit Reisnudeln",
      category: "Hauptgericht", time: 20, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "tofu-gemuesepfanne.webp",
      nutrition: { kcal: 680, carbs: 60, protein: 38, fat: 29 },
      ingredients: [
        { name: "Räuchertofu", grams: 180, kcal: 165, carbs: 1, protein: 17, fat: 10 },
        { name: "Reisnudeln, roh", grams: 55, kcal: 360, carbs: 82, protein: 7, fat: 0.6 },
        { name: "Paprika", grams: 150, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Zuckerschoten", grams: 100, kcal: 42, carbs: 5, protein: 3, fat: 0.2 },
        { name: "Sesamöl", grams: 10, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        "Sojasauce (glutenfrei), Ingwer"
      ],
      steps: "Reisnudeln nach Packungsangabe einweichen. Tofu würfeln und in Sesamöl knusprig braten, Gemüse zugeben und 3–4 Min. mitbraten. Nudeln unterheben und mit Sojasauce und Ingwer abschmecken." },

    { id: "haehnchen-zucchini-feta", name: "Hähnchen-Zucchini-Pfanne mit Feta",
      category: "Hauptgericht", time: 20, tags: ["highprotein", "lowcarb", "glutenfrei"], mealPrep: true, img: "haehnchen-zucchini-feta.webp", photo: "chicken",
      nutrition: { kcal: 500, carbs: 8, protein: 57, fat: 24 },
      ingredients: [
        { name: "Hähnchenbrustfilet", grams: 200, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Zucchini", grams: 250, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Kirschtomaten", grams: 100, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Feta", grams: 50, kcal: 265, carbs: 1, protein: 14, fat: 22 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Oregano, Salz, Pfeffer"
      ],
      steps: "Hähnchen würfeln, würzen und scharf anbraten. Zucchini in Halbmonde schneiden, zugeben und 5 Min. mitbraten. Tomaten kurz mitziehen lassen, vom Herd nehmen und den Feta darüberbröseln." },

    { id: "blumenkohl-curry-tofu", name: "Blumenkohl-Curry mit Tofu",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "lowcarb", "glutenfrei", "laktosefrei", "highprotein"], mealPrep: true, img: "blumenkohl-curry-tofu.webp",
      nutrition: { kcal: 497, carbs: 13, protein: 37, fat: 31 },
      ingredients: [
        { name: "Räuchertofu", grams: 150, kcal: 165, carbs: 1, protein: 17, fat: 10 },
        { name: "Blumenkohl", grams: 300, kcal: 25, carbs: 3, protein: 2.5, fat: 0.3 },
        { name: "Kokosmilch", grams: 80, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Spinat, frisch", grams: 100, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        "Currypaste, Ingwer, Limette, Salz"
      ],
      steps: "Tofu würfeln und knusprig anbraten, herausnehmen. Blumenkohlröschen mit Currypaste anrösten, mit Kokosmilch ablöschen und 10 Min. köcheln. Spinat und Tofu unterheben, mit Limette abschmecken." },

    { id: "skyr-beeren-nuesse", name: "Skyr mit Beeren und Walnüssen",
      category: "Snack", time: 3, tags: ["vegetarisch", "highprotein", "glutenfrei"], mealPrep: false, img: "skyr-beeren-nuesse.webp",
      nutrition: { kcal: 250, carbs: 13, protein: 25, fat: 10 },
      ingredients: [
        { name: "Skyr, natur", grams: 200, kcal: 63, carbs: 4, protein: 11, fat: 0.2 },
        { name: "Himbeeren", grams: 80, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Walnüsse", grams: 15, kcal: 650, carbs: 7, protein: 15, fat: 63 }
      ],
      steps: "Skyr in eine Schüssel geben, Beeren und grob gehackte Walnüsse darüberstreuen." },

    { id: "quark-haferflocken-banane", name: "Quark-Haferflocken-Schale mit Banane",
      category: "Frühstück", time: 5, tags: ["vegetarisch", "highprotein"], mealPrep: true, img: "quark-haferflocken-banane.webp",
      nutrition: { kcal: 514, carbs: 64, protein: 40, fat: 9 },
      ingredients: [
        { name: "Magerquark", grams: 250, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Haferflocken", grams: 50, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Banane", grams: 120, kcal: 90, carbs: 20, protein: 1.1, fat: 0.3 },
        { name: "Leinsamen", grams: 10, kcal: 530, carbs: 3, protein: 24, fat: 42 },
        "Zimt"
      ],
      steps: "Quark mit den Haferflocken verrühren und einen Schluck Wasser oder Milch untermischen, sonst wird es zu fest. Banane in Scheiben schneiden, mit Leinsamen und Zimt daraufgeben. Hält im Kühlschrank zwei Tage." },

    { id: "protein-pancakes-skyr", name: "Protein-Pancakes mit Skyr und Beeren",
      category: "Frühstück", time: 15, tags: ["vegetarisch", "highprotein"], mealPrep: false, img: "protein-pancakes-skyr.webp",
      nutrition: { kcal: 480, carbs: 48, protein: 43, fat: 11 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Eiklar", grams: 150, kcal: 52, carbs: 0.7, protein: 11, fat: 0.2 },
        { name: "Ei, Größe M", grams: 1, unit: "st", kcal: 80, carbs: 0.4, protein: 7, fat: 5.7 },
        { name: "Skyr, natur", grams: 100, kcal: 63, carbs: 4, protein: 11, fat: 0.2 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 },
        "Backpulver, Vanille, Prise Salz"
      ],
      steps: "Haferflocken fein mahlen, mit Eiklar, Ei und Backpulver zu einem dickflüssigen Teig verrühren und 5 Min. quellen lassen. Bei mittlerer Hitze kleine Pancakes backen – zu heiß und sie werden außen dunkel, bevor die Mitte fest ist. Mit Skyr und Beeren servieren." },

    { id: "tofu-ruehrei-vollkornbrot", name: "Tofu-Rührei auf Vollkornbrot",
      category: "Frühstück", time: 10, tags: ["vegan", "vegetarisch", "highprotein", "laktosefrei"], mealPrep: false, img: "tofu-ruehrei-vollkornbrot.webp",
      nutrition: { kcal: 437, carbs: 24, protein: 33, fat: 22 },
      ingredients: [
        { name: "Tofu, natur", grams: 200, kcal: 130, carbs: 1, protein: 14, fat: 8 },
        { name: "Vollkornbrot", grams: 60, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Frühlingszwiebel", grams: 20, kcal: 32, carbs: 4.5, protein: 1.8, fat: 0.2 },
        { name: "Rapsöl", grams: 5, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Kurkuma, Salz, Pfeffer, Schnittlauch"
      ],
      steps: "Tofu mit der Gabel grob zerdrücken – nicht pürieren, die Struktur macht den Unterschied. In Öl 4–5 Min. braten, mit Kurkuma, Salz und Pfeffer würzen. Auf getoastetem Vollkornbrot anrichten und mit Frühlingszwiebel bestreuen." },

    { id: "chia-pudding-soja-beeren", name: "Chia-Pudding mit Sojadrink und Beeren",
      category: "Frühstück", time: 5, tags: ["vegan", "vegetarisch", "highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "chia-pudding-soja-beeren.webp",
      nutrition: { kcal: 310, carbs: 11, protein: 25, fat: 14 },
      ingredients: [
        { name: "Chiasamen", grams: 25, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        { name: "Sojadrink, ungesüßt", grams: 250, unit: "ml", kcal: 39, carbs: 0.6, protein: 3.3, fat: 1.9 },
        { name: "Erbsenprotein-Pulver", grams: 15, kcal: 380, carbs: 5, protein: 80, fat: 6 },
        { name: "Heidelbeeren", grams: 80, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 }
      ],
      steps: "Chiasamen, Sojadrink und Proteinpulver verrühren, nach fünf Minuten noch einmal umrühren – sonst setzen sich die Samen am Boden ab. Über Nacht in den Kühlschrank, am Morgen die Beeren daraufgeben." },

    { id: "ofenlachs-suesskartoffel", name: "Ofenlachs mit Süßkartoffeln und Brokkoli",
      category: "Hauptgericht", time: 35, tags: ["glutenfrei", "laktosefrei"], mealPrep: true, img: "ofenlachs-suesskartoffel.webp", photo: "fish",
      nutrition: { kcal: 656, carbs: 54, protein: 40, fat: 30 },
      ingredients: [
        { name: "Lachsfilet", grams: 150, kcal: 200, carbs: 0, protein: 20, fat: 13 },
        { name: "Süßkartoffeln", grams: 250, kcal: 86, carbs: 20, protein: 1.6, fat: 0.1 },
        { name: "Brokkoli", grams: 150, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Zitrone, Salz, Pfeffer"
      ],
      steps: "Süßkartoffeln würfeln, mit Öl mischen und bei 200 °C 20 Min. rösten. Lachs auf das Blech legen und weitere 12 Min. garen – er ist fertig, sobald er sich mit der Gabel in Segmente teilen lässt. Brokkoli dämpfen und mit Zitrone servieren." },

    { id: "putenpfanne-vollkornnudeln", name: "Putenpfanne mit Vollkornnudeln",
      category: "Hauptgericht", time: 25, tags: ["highprotein"], mealPrep: true, img: "putenpfanne-vollkornnudeln.webp",
      nutrition: { kcal: 584, carbs: 50, protein: 58, fat: 14 },
      ingredients: [
        { name: "Putenbrustfilet", grams: 180, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Vollkornnudeln, roh", grams: 70, kcal: 335, carbs: 62, protein: 14, fat: 2.5 },
        { name: "Champignons", grams: 150, kcal: 22, carbs: 0.6, protein: 2.7, fat: 0.3 },
        { name: "Paprika, rot", grams: 100, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Kräuter, Salz, Pfeffer"
      ],
      steps: "Nudeln bissfest kochen. Pute in Streifen schneiden, kräftig würzen und heiß anbraten, dann herausnehmen. Champignons und Paprika in derselben Pfanne braten, bis die Flüssigkeit verdampft ist, alles zusammenführen." },

    { id: "chili-rinderhack-bohnen", name: "Chili mit Rinderhack und Kidneybohnen",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: true, img: "chili-rinderhack-bohnen.webp",
      nutrition: { kcal: 543, carbs: 44, protein: 49, fat: 15 },
      ingredients: [
        { name: "Rinderhackfleisch, mager", grams: 150, kcal: 130, carbs: 0, protein: 21, fat: 5 },
        { name: "Kidneybohnen, Dose", grams: 150, kcal: 110, carbs: 14, protein: 8, fat: 0.6 },
        { name: "Passierte Tomaten", grams: 200, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Mais, Dose", grams: 60, kcal: 90, carbs: 16, protein: 3, fat: 1.2 },
        { name: "Zwiebeln", grams: 70, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Rapsöl", grams: 5, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Kreuzkümmel, Paprikapulver, Chili, Salz"
      ],
      steps: "Zwiebeln anschwitzen, Hack krümelig anbraten und die Gewürze kurz mitrösten. Tomaten, Bohnen und Mais zugeben und 20 Min. offen köcheln. Am nächsten Tag schmeckt es besser – das ist das ideale Gericht zum Vorkochen." },

    { id: "linsen-bolognese-vollkorn", name: "Linsen-Bolognese mit Vollkornnudeln",
      category: "Hauptgericht", time: 30, tags: ["vegan", "vegetarisch", "laktosefrei"], mealPrep: true, img: "linsen-bolognese-vollkorn.webp",
      nutrition: { kcal: 642, carbs: 91, protein: 29, fat: 13 },
      ingredients: [
        { name: "Linsen, roh", grams: 70, kcal: 340, carbs: 50, protein: 24, fat: 1.5 },
        { name: "Vollkornnudeln, roh", grams: 60, kcal: 335, carbs: 62, protein: 14, fat: 2.5 },
        { name: "Passierte Tomaten", grams: 200, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Zwiebeln", grams: 60, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Knoblauch, Oregano, Salz, Pfeffer"
      ],
      steps: "Zwiebel und Karotte fein würfeln und in Öl anschwitzen. Linsen und Tomaten zugeben, mit Wasser auffüllen und 25 Min. köcheln, bis die Linsen weich sind. Nudeln separat garen und die Sauce daraufgeben." },

    { id: "haehnchen-brokkoli-auflauf", name: "Hähnchen-Brokkoli-Auflauf",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "lowcarb", "glutenfrei"], mealPrep: true, img: "haehnchen-brokkoli-auflauf.webp",
      nutrition: { kcal: 534, carbs: 12, protein: 72, fat: 20 },
      ingredients: [
        { name: "Hähnchenbrustfilet", grams: 200, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Brokkoli", grams: 300, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Frischkäse, light", grams: 80, kcal: 145, carbs: 4, protein: 9, fat: 10 },
        { name: "Gouda, mittelalt", grams: 30, kcal: 355, carbs: 0, protein: 25, fat: 28 },
        "Muskat, Salz, Pfeffer"
      ],
      steps: "Brokkoli 4 Min. vorgaren, damit er im Ofen nicht hart bleibt. Hähnchen würfeln, würzen und mit dem Brokkoli in eine Form geben. Frischkäse mit etwas Wasser glattrühren, darübergießen, Käse daraufreiben und bei 200 °C 20 Min. backen." },

    { id: "garnelen-zucchini-tomaten", name: "Garnelen mit Zucchini und Kirschtomaten",
      category: "Hauptgericht", time: 20, tags: ["highprotein", "lowcarb", "glutenfrei", "laktosefrei"], mealPrep: false, img: "garnelen-zucchini-tomaten.webp", photo: "seafood",
      nutrition: { kcal: 338, carbs: 10, protein: 43, fat: 13 },
      ingredients: [
        { name: "Garnelen", grams: 200, kcal: 85, carbs: 0, protein: 19, fat: 1 },
        { name: "Zucchini", grams: 250, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Kirschtomaten", grams: 150, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Knoblauch, Chili, Petersilie, Salz"
      ],
      steps: "Zucchini in Streifen schneiden und in heißem Öl 3 Min. braten, Tomaten kurz mitziehen lassen. Garnelen erst zum Schluss zugeben und nur 2 Min. garen – länger und sie werden zäh. Mit Knoblauch, Chili und Petersilie abschmecken." },

    { id: "kichererbsen-curry-spinat", name: "Kichererbsen-Curry mit Spinat und Reis",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "kichererbsen-curry-spinat.webp",
      nutrition: { kcal: 610, carbs: 78, protein: 26, fat: 18 },
      ingredients: [
        { name: "Kichererbsen, Dose", grams: 200, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Spinat, frisch", grams: 150, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        { name: "Kokosmilch", grams: 60, unit: "ml", kcal: 190, carbs: 3, protein: 2, fat: 19 },
        { name: "Passierte Tomaten", grams: 150, kcal: 32, carbs: 5, protein: 1.4, fat: 0.2 },
        { name: "Zwiebeln", grams: 60, kcal: 28, carbs: 5, protein: 1.2, fat: 0.2 },
        { name: "Basmatireis, roh", grams: 45, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        "Currypulver, Ingwer, Knoblauch, Salz"
      ],
      steps: "Reis aufsetzen. Zwiebel, Ingwer und Knoblauch anschwitzen, Curry kurz mitrösten. Kichererbsen, Tomaten und Kokosmilch zugeben, 10 Min. köcheln, dann den Spinat unterheben – er fällt in einer Minute zusammen." },

    { id: "quinoa-bowl-edamame", name: "Quinoa-Bowl mit Edamame und Avocado",
      category: "Hauptgericht", time: 25, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "quinoa-bowl-edamame.webp",
      nutrition: { kcal: 654, carbs: 63, protein: 34, fat: 27 },
      ingredients: [
        { name: "Quinoa, roh", grams: 70, kcal: 368, carbs: 58, protein: 14, fat: 6 },
        { name: "Edamame", grams: 200, kcal: 120, carbs: 8, protein: 11, fat: 5 },
        { name: "Avocado", grams: 50, kcal: 160, carbs: 1, protein: 2, fat: 15 },
        { name: "Karotten", grams: 80, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Sesamöl", grams: 5, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        "Limette, Sojasauce (glutenfrei), Sesam"
      ],
      steps: "Quinoa vor dem Kochen gut abspülen, sonst schmeckt er bitter, und 15 Min. garen. Edamame kurz blanchieren, Karotte fein raspeln. Alles in einer Schüssel schichten, Avocado darauflegen und mit Sesamöl, Limette und Sojasauce abschmecken." },

    { id: "huettenkaese-vollkornbrot", name: "Hüttenkäse auf Vollkornbrot mit Radieschen",
      category: "Snack", time: 5, tags: ["vegetarisch", "highprotein"], mealPrep: false, img: "huettenkaese-vollkornbrot.webp", photo: "sandwich",
      nutrition: { kcal: 284, carbs: 26, protein: 25, fat: 7 },
      ingredients: [
        { name: "Hüttenkäse", grams: 150, kcal: 100, carbs: 3, protein: 13, fat: 4 },
        { name: "Vollkornbrot", grams: 60, kcal: 210, carbs: 35, protein: 8, fat: 2 },
        { name: "Radieschen", grams: 50, kcal: 15, carbs: 2, protein: 1, fat: 0.1 },
        "Schnittlauch, Pfeffer"
      ],
      steps: "Brot toasten, Hüttenkäse daraufgeben und mit Pfeffer würzen. Radieschen in dünne Scheiben schneiden und mit Schnittlauch darüberstreuen." },

    { id: "edamame-sesam-snack", name: "Edamame mit Sesam und Meersalz",
      category: "Snack", time: 10, tags: ["vegan", "vegetarisch", "highprotein", "glutenfrei", "laktosefrei"], mealPrep: false, img: "edamame-sesam-snack.webp", photo: "salad",
      nutrition: { kcal: 284, carbs: 16, protein: 22, fat: 15 },
      ingredients: [
        { name: "Edamame", grams: 200, kcal: 120, carbs: 8, protein: 11, fat: 5 },
        { name: "Sesamöl", grams: 5, kcal: 884, carbs: 0, protein: 0, fat: 100 },
        "Meersalz, Sesam, Chiliflocken"
      ],
      steps: "Edamame 4 Min. in Salzwasser kochen und abgießen. Mit Sesamöl schwenken, mit Meersalz, Sesam und Chiliflocken bestreuen und aus der Schote essen." },

    { id: "thunfisch-quark-dip", name: "Thunfisch-Quark-Dip mit Gurke",
      category: "Snack", time: 5, tags: ["highprotein", "lowcarb", "glutenfrei"], mealPrep: false, img: "thunfisch-quark-dip.webp", photo: "fish",
      nutrition: { kcal: 218, carbs: 8, protein: 42, fat: 2 },
      ingredients: [
        { name: "Thunfisch in Wasser, Dose", grams: 100, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Magerquark", grams: 150, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Gurke", grams: 100, kcal: 12, carbs: 1.8, protein: 0.6, fat: 0.1 },
        "Zitrone, Salz, Pfeffer, Dill"
      ],
      steps: "Thunfisch gut abtropfen lassen und mit dem Quark verrühren, mit Zitrone, Salz und Pfeffer abschmecken. Gurke in Stifte schneiden und zum Dippen dazustellen." },

    { id: "schoko-protein-quark", name: "Schoko-Protein-Quark",
      category: "Dessert", time: 5, tags: ["vegetarisch", "highprotein", "glutenfrei"], mealPrep: false, img: "schoko-protein-quark.webp", photo: "cake",
      nutrition: { kcal: 282, carbs: 14, protein: 42, fat: 6 },
      ingredients: [
        { name: "Magerquark", grams: 250, kcal: 67, carbs: 4, protein: 12, fat: 0.3 },
        { name: "Proteinpulver, Whey", grams: 15, kcal: 380, carbs: 5, protein: 78, fat: 6 },
        { name: "Zartbitterschokolade 70 %", grams: 10, kcal: 570, carbs: 33, protein: 8, fat: 42 },
        "Backkakao, Süße nach Geschmack"
      ],
      steps: "Quark mit Proteinpulver, Kakao und einem Schluck Wasser cremig rühren – erst das Wasser, dann das Pulver, sonst klumpt es. Schokolade grob hacken und darüberstreuen." },

    { id: "dattel-nuss-bissen", name: "Dattel-Nuss-Bissen mit Kakao",
      category: "Dessert", time: 15, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "dattel-nuss-bissen.webp", photo: "cake",
      nutrition: { kcal: 300, carbs: 33, protein: 6, fat: 16 },
      ingredients: [
        { name: "Datteln, getrocknet", grams: 40, kcal: 280, carbs: 65, protein: 2.5, fat: 0.4 },
        { name: "Cashewkerne", grams: 25, kcal: 560, carbs: 27, protein: 18, fat: 44 },
        { name: "Kokosraspeln", grams: 8, kcal: 600, carbs: 6, protein: 6, fat: 57 },
        "Backkakao, Prise Salz"
      ],
      steps: "Datteln und Cashews im Mixer zu einer klebrigen Masse zerkleinern, Kakao und Salz untermischen. Kleine Kugeln formen, in Kokosraspeln wälzen und kalt stellen. Hält im Kühlschrank eine Woche." },

    { id: "ofengemuese-blech", name: "Ofengemüse vom Blech",
      category: "Beilage", time: 30, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "ofengemuese-blech.webp",
      nutrition: { kcal: 224, carbs: 20, protein: 6, fat: 12 },
      ingredients: [
        { name: "Zucchini", grams: 200, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Paprika, rot", grams: 150, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Karotten", grams: 100, kcal: 40, carbs: 7, protein: 0.9, fat: 0.2 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Rosmarin, Thymian, Salz, Pfeffer"
      ],
      steps: "Gemüse in gleich große Stücke schneiden, mit Öl und Kräutern mischen und auf dem Blech verteilen – nicht stapeln, sonst dämpft es statt zu rösten. Bei 200 °C 25 Min. backen." },

    { id: "quinoa-salat-kichererbsen", name: "Quinoa-Salat mit Kichererbsen",
      category: "Beilage", time: 20, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: true, img: "quinoa-salat-kichererbsen.webp",
      nutrition: { kcal: 371, carbs: 43, protein: 14, fat: 13 },
      ingredients: [
        { name: "Quinoa, roh", grams: 40, kcal: 368, carbs: 58, protein: 14, fat: 6 },
        { name: "Kichererbsen, Dose", grams: 100, kcal: 120, carbs: 15, protein: 7, fat: 2.6 },
        { name: "Gurke", grams: 100, kcal: 12, carbs: 1.8, protein: 0.6, fat: 0.1 },
        { name: "Kirschtomaten", grams: 100, kcal: 20, carbs: 3.4, protein: 0.9, fat: 0.2 },
        { name: "Olivenöl", grams: 8, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Zitrone, Petersilie, Salz, Pfeffer"
      ],
      steps: "Quinoa 15 Min. garen und auskühlen lassen – warm eingerührt wird der Salat matschig. Mit Kichererbsen, gewürfelter Gurke und halbierten Tomaten mischen, mit Öl und Zitrone abschmecken." },

    { id: "beeren-protein-shake-hafer", name: "Beeren-Protein-Shake mit Hafermilch",
      category: "Getränk", time: 5, tags: ["vegan", "vegetarisch", "highprotein", "laktosefrei"], mealPrep: false, img: "beeren-protein-shake-hafer.webp",
      nutrition: { kcal: 336, carbs: 26, protein: 30, fat: 11 },
      ingredients: [
        { name: "Hafermilch, ungesüßt", grams: 300, unit: "ml", kcal: 45, carbs: 6.5, protein: 0.8, fat: 1.5 },
        { name: "Erbsenprotein-Pulver", grams: 30, kcal: 380, carbs: 5, protein: 80, fat: 6 },
        { name: "Himbeeren", grams: 100, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Leinsamen", grams: 10, kcal: 530, carbs: 3, protein: 24, fat: 42 }
      ],
      steps: "Alles zusammen mixen, bis keine Stücke mehr zu sehen sind. Gefrorene Beeren machen den Shake dicker und kalt, ganz ohne Eis." },

    { id: "gruener-smoothie-spinat", name: "Grüner Smoothie mit Spinat und Banane",
      category: "Getränk", time: 5, tags: ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], mealPrep: false, img: "gruener-smoothie-spinat.webp", photo: "drink",
      nutrition: { kcal: 207, carbs: 26, protein: 6, fat: 7 },
      ingredients: [
        { name: "Spinat, frisch", grams: 60, kcal: 23, carbs: 0.6, protein: 2.9, fat: 0.4 },
        { name: "Banane", grams: 120, kcal: 90, carbs: 20, protein: 1.1, fat: 0.3 },
        { name: "Mandelmilch, ungesüßt", grams: 250, unit: "ml", kcal: 15, carbs: 0.3, protein: 0.5, fat: 1.2 },
        { name: "Chiasamen", grams: 10, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        "Zitrone, Ingwer"
      ],
      steps: "Spinat zuerst mit der Mandelmilch mixen, dann die Banane zugeben – so bleiben keine Blattstücke zurück. Mit Zitrone und Ingwer abschmecken." },

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
      nutrition: { kcal: 561, carbs: 56, protein: 42, fat: 17 },
      ingredients: [
        { name: "Haferflocken", grams: 60, kcal: 372, carbs: 59, protein: 13, fat: 7 },
        { name: "Milch 1,5 %", grams: 250, unit: "ml", kcal: 64, carbs: 4.8, protein: 3.4, fat: 3.5 },
        { name: "Proteinpulver, Whey", grams: 30, kcal: 380, carbs: 5, protein: 78, fat: 6 },
        { name: "Heidelbeeren", grams: 50, kcal: 45, carbs: 9, protein: 0.7, fat: 0.3 },
        { name: "Himbeeren", grams: 50, kcal: 34, carbs: 5, protein: 1.2, fat: 0.3 },
        { name: "Chiasamen", grams: 5, kcal: 480, carbs: 5, protein: 17, fat: 31 },
        "Zimt"
      ],
      steps: "Haferflocken mit Milch aufkochen und 3–4 Min. bei milder Hitze quellen lassen. Vom Herd nehmen und erst dann das Proteinpulver unterrühren – in der kochenden Masse würde es flocken. Mit Beeren, Chiasamen und Zimt toppen." },

    { id: "haehnchen-mit-pute-und-reis", name: "Hähnchen mit Pute und Reis",
      category: "Hauptgericht", time: 30, tags: ["highprotein", "laktosefrei"], mealPrep: true,
      img: "haehnchen-mit-pute-und-reis.webp",
      nutrition: { kcal: 600, carbs: 69, protein: 50, fat: 13 },
      ingredients: [
        { name: "Hähnchenbrustfilet", grams: 100, kcal: 105, carbs: 0, protein: 23, fat: 1.2 },
        { name: "Putenbrustfilet", grams: 75, kcal: 105, carbs: 0, protein: 24, fat: 1 },
        { name: "Basmatireis, roh", grams: 80, kcal: 349, carbs: 78, protein: 8, fat: 0.8 },
        { name: "Paprika, rot", grams: 75, kcal: 37, carbs: 6, protein: 1, fat: 0.4 },
        { name: "Zucchini", grams: 100, kcal: 19, carbs: 2, protein: 1.6, fat: 0.4 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Sojasauce, Paprikapulver, Salz, Pfeffer"
      ],
      steps: "Reis nach Packungsangabe kochen. Hähnchen- und Putenbrust würfeln, würzen und in Olivenöl scharf anbraten. Paprika und Zucchini kurz mitbraten, mit Sojasauce ablöschen. Alles auf dem Reis anrichten." },

    { id: "rindersteak-mit-ofenkartoffeln", name: "Rindersteak mit Ofenkartoffeln",
      category: "Hauptgericht", time: 35, tags: ["highprotein", "glutenfrei", "laktosefrei"], mealPrep: false,
      img: "rindersteak-mit-ofenkartoffeln.webp",
      nutrition: { kcal: 631, carbs: 50, protein: 56, fat: 22 },
      ingredients: [
        { name: "Rumpsteak", grams: 200, kcal: 140, carbs: 0, protein: 22, fat: 5.5 },
        { name: "Kartoffeln", grams: 300, kcal: 70, carbs: 15, protein: 2, fat: 0.1 },
        { name: "Brokkoli", grams: 150, kcal: 34, carbs: 3, protein: 3.8, fat: 0.4 },
        { name: "Olivenöl", grams: 10, kcal: 900, carbs: 0, protein: 0, fat: 100 },
        "Rosmarin, Salz, Pfeffer"
      ],
      steps: "Kartoffeln würfeln, mit Olivenöl und Rosmarin vermengen und im Ofen bei 200 °C ca. 25 Min. rösten. Steak salzen, pfeffern und in einer heißen Pfanne von jeder Seite 2–3 Min. braten, dann kurz ruhen lassen – sonst läuft der Saft aus. Brokkoli dämpfen und alles anrichten." },

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
        "Eiswürfel"
      ],
      steps: "Milch, Proteinpulver, Banane und ein paar Eiswürfel in den Mixer geben und cremig mixen." },
  ];
