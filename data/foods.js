/* foods.js - Paddy's Mealplan
 *
 * Zutaten- und Naehrwerttabelle (FOODS).
 *
 * Reine Daten, keine Logik. Ausgeschnitten aus index.html, unveraendert.
 * Wird als klassisches <script> VOR der App-IIFE geladen; die Konstanten stehen
 * dadurch im globalen Bereich und werden von der IIFE gelesen.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  // ---------- Zutaten-Datenbank fuer die Suche ----------
  // Handgepflegte Rundwerte fuer GENERISCHE Lebensmittel — bewusst keine Markenprodukte
  // und bewusst kein Auszug aus einer fremden Datenbank: ein solcher Auszug waere eine
  // abgeleitete Datenbank und zoege deren Lizenzbedingungen nach sich (z. B. ODbL bei
  // Open Food Facts). Markenprodukte deckt stattdessen der Barcode-Scan ab, der einzelne
  // Produkte live abfragt statt Daten auf Vorrat mitzuliefern.
  // Format: [Name, kcal, KH, Protein, Fett, Einheit?, Synonyme?, GrammJeStueck?] je 100 g
  // bzw. 100 ml, bei Einheit "st" je Stueck. Fehlende Einheit = "g". Die Synonyme stehen nur im
  // Suchschluessel, nicht in der Anzeige — sie fangen ab, wonach Leute tatsaechlich
  // suchen ("Huhn" statt "Hähnchenbrustfilet", "Möhren" statt "Karotten") und decken
  // regionale Namen ab. Weil sie hinten angehaengt werden, ranken sie automatisch
  // hinter den echten Namenstreffern.
  //
  // Das letzte Feld (GrammJeStueck) traegt doppelt: es macht einen Eintrag fuer den
  // Schnelleintrag im Wochenplan zaehlbar (siehe pieceFoods) und steht bewusst HIER, direkt
  // neben den Naehrwerten, auf die es sich bezieht - eine zweite Tabelle "Name -> Gewicht"
  // waere eine Namensverknuepfung, die bei jedem Umbenennen still bricht. Gemeint ist immer
  // der verzehrbare Anteil eines mittelgrossen Stuecks (Avocado ohne Kern und Schale).
  /*FOODS_START*/
  const FOODS = [
    // Getreide, Beilagen
    ["Reis, weiß, roh", 350, 78, 7, 0.6], ["Reis, weiß, gekocht", 130, 28, 2.4, 0.3],
    ["Reis, Vollkorn, roh", 350, 74, 8, 2.5], ["Reis, Vollkorn, gekocht", 123, 25, 2.7, 1],
    ["Basmatireis, roh", 349, 78, 8, 0.8],
    ["Nudeln, roh", 350, 71, 12, 1.5, "g", "Pasta Spaghetti Penne Fusilli"],
    ["Nudeln, gekocht", 140, 28, 5, 0.7, "g", "Pasta Spaghetti"],
    ["Vollkornnudeln, roh", 335, 62, 14, 2.5, "g", "Pasta"],
    ["Spätzle, frisch", 165, 28, 6, 2.5], ["Couscous, roh", 355, 72, 12, 1.5],
    ["Bulgur, roh", 342, 69, 12, 1.3], ["Quinoa, roh", 368, 58, 14, 6],
    ["Hirse, roh", 354, 69, 11, 4], ["Haferflocken", 372, 59, 13, 7, "g", "Oats Porridge"],
    ["Dinkelflocken", 340, 63, 12, 2.7], ["Cornflakes, ungesüßt", 360, 84, 7, 0.9],
    ["Müsli, Basis", 360, 60, 10, 8], ["Knäckebrot", 340, 65, 10, 2],
    ["Weizenmehl Type 405", 348, 72, 10, 1, "g", "Mehl"], ["Dinkelmehl Type 630", 344, 70, 11, 1.4],
    ["Vollkornmehl, Weizen", 325, 60, 12, 2], ["Hartweizengrieß", 350, 72, 12, 1],
    ["Kartoffeln", 70, 15, 2, 0.1, "g", "Erdäpfel"], ["Süßkartoffeln", 86, 20, 1.6, 0.1, "g", "Batate"],
    ["Pommes frites, TK", 160, 24, 2.5, 5.5], ["Kartoffelpüree, zubereitet", 85, 13, 2, 2.5],
    ["Gnocchi", 160, 32, 4, 1], ["Maisgrieß / Polenta, roh", 355, 73, 8, 1.5],
    ["Buchweizen, roh", 343, 71, 13, 3.4], ["Amaranth, roh", 371, 63, 14, 7],
    ["Reisnudeln, roh", 360, 82, 7, 0.6, "g", "Glasnudeln"], ["Roggenmehl Type 1150", 325, 65, 8, 1.5],
    // Brot und Backwaren
    ["Vollkornbrot", 210, 35, 8, 2], ["Mischbrot", 240, 45, 7, 1.2],
    ["Roggenbrot", 220, 42, 6, 1.2], ["Toastbrot", 270, 48, 9, 4],
    ["Weizenbrötchen", 270, 53, 9, 1.5, "g", "Semmel Schrippe Rundstück", 60], ["Vollkornbrötchen", 240, 42, 9, 2, "g", null, 70],
    ["Pumpernickel", 190, 36, 6, 1.2], ["Baguette", 270, 55, 8, 1],
    ["Tortilla-Wrap, Weizen", 300, 50, 8, 7], ["Fladenbrot / Pita", 275, 55, 9, 1.5],
    ["Sonnenblumenkernbrot", 250, 38, 9, 6], ["Ciabatta", 265, 51, 9, 2],
    ["Laugenbrezel", 280, 55, 9, 2.5, "g", "Brezn Breze", 80], ["Naan-Brot", 310, 50, 9, 8],
    // Fleisch und Wurst
    ["Hähnchenbrustfilet", 105, 0, 23, 1.2, "g", "Huhn Hendl Chicken Geflügel Poulet"],
    ["Hähnchenschenkel, ohne Haut", 145, 0, 19, 7.5, "g", "Huhn Keule Geflügel"],
    ["Putenbrustfilet", 105, 0, 24, 1, "g", "Truthahn Geflügel"],
    ["Hackfleisch, gemischt", 230, 0, 18, 17, "g", "Faschiertes Mett Gehacktes"],
    ["Rinderhackfleisch, mager", 130, 0, 21, 5, "g", "Rindfleisch Faschiertes Gehacktes"],
    ["Rinderfilet", 125, 0, 21, 4, "g", "Rindfleisch Steak"],
    ["Rumpsteak", 140, 0, 22, 5.5, "g", "Rindfleisch Steak"],
    ["Schweineschnitzel, mager", 105, 0, 22, 2, "g", "Schweinefleisch"],
    ["Schweinefilet", 110, 0, 22, 2, "g", "Schweinefleisch"], ["Schweinebauch", 320, 0, 17, 28],
    ["Kasseler", 145, 0, 21, 7], ["Lammkeule", 160, 0, 20, 9],
    ["Frühstücksspeck / Bacon", 400, 0, 17, 37], ["Kochschinken", 110, 1, 19, 3],
    ["Serranoschinken", 240, 0, 30, 13], ["Salami", 380, 1, 19, 33],
    ["Bratwurst", 300, 1, 14, 27], ["Wiener Würstchen", 270, 1, 12, 24],
    ["Leberkäse", 290, 2, 13, 25], ["Fleischwurst", 300, 1, 12, 27],
    ["Hähnchen-Nuggets, TK", 250, 17, 14, 14],
    ["Putenhackfleisch", 120, 0, 20, 4], ["Entenbrust, mit Haut", 210, 0, 19, 15],
    ["Kalbsschnitzel", 108, 0, 21, 2.5], ["Rehrücken / Wild", 120, 0, 22, 3, "g", "Reh Hirsch"],
    ["Leberwurst", 330, 2, 14, 30], ["Mortadella", 290, 1, 15, 25],
    ["Chorizo", 380, 2, 21, 31], ["Cabanossi", 340, 1, 18, 29],
    ["Currywurst, ohne Soße", 300, 1, 13, 27],
    // Fisch und Meeresfrüchte
    ["Lachsfilet", 200, 0, 20, 13], ["Lachs, geräuchert", 180, 0, 22, 10],
    ["Forelle", 105, 0, 20, 3], ["Kabeljau", 76, 0, 17, 0.7],
    ["Seelachsfilet", 80, 0, 18, 0.9], ["Zander", 83, 0, 19, 0.7],
    ["Pangasiusfilet", 90, 0, 15, 3], ["Thunfisch, roh", 145, 0, 23, 5],
    ["Thunfisch in Wasser, Dose", 105, 0, 24, 1], ["Thunfisch in Öl, abgetropft", 190, 0, 25, 10],
    ["Garnelen", 85, 0, 19, 1], ["Hering", 210, 0, 18, 15],
    ["Makrele, geräuchert", 280, 0, 21, 22], ["Sardinen in Öl", 220, 0, 21, 15],
    ["Fischstäbchen, TK", 200, 18, 12, 9],
    ["Scholle", 90, 0, 17, 2], ["Rotbarsch", 92, 0, 18, 2],
    ["Steinbeißer", 82, 0, 17, 1], ["Miesmuscheln", 85, 3, 12, 2, "g", "Muscheln"],
    ["Tintenfisch / Calamari", 92, 3, 16, 1.5], ["Krabbenfleisch / Surimi", 95, 9, 12, 1, "g", "Krabben"],
    // Milchprodukte und Eier
    ["Magerquark", 67, 4, 12, 0.3, "g", "Topfen Quark"], ["Speisequark 20 %", 110, 3.5, 12, 5, "g", "Topfen"],
    ["Speisequark 40 %", 145, 3, 11, 10, "g", "Topfen"], ["Skyr, natur", 63, 4, 11, 0.2],
    ["Naturjoghurt 3,5 %", 65, 4.7, 3.5, 3.5], ["Joghurt, mager 0,1 %", 40, 5, 4, 0.1],
    ["Griechischer Joghurt 10 %", 130, 4, 4, 10], ["Hüttenkäse / körniger Frischkäse", 100, 3, 13, 4, "g", "Cottage Cheese"],
    ["Milch 3,5 %", 64, 4.8, 3.4, 3.5, "ml"], ["Milch 1,5 %", 47, 4.9, 3.4, 1.5, "ml"],
    ["Magermilch 0,3 %", 35, 5, 3.4, 0.2, "ml"], ["Hafermilch, ungesüßt", 45, 6.5, 0.8, 1.5, "ml"],
    ["Mandelmilch, ungesüßt", 15, 0.3, 0.5, 1.2, "ml"], ["Sojadrink, ungesüßt", 39, 0.6, 3.3, 1.9, "ml"],
    ["Sojajoghurt, natur", 50, 1.5, 4, 2.5],
    ["Sahne 30 %", 290, 3, 2.4, 30, "ml", "Rahm Obers Schlagsahne"], ["Saure Sahne 10 %", 115, 3.5, 3, 10],
    ["Schmand 24 %", 240, 3.5, 3, 24], ["Crème fraîche", 300, 3, 2.5, 30],
    ["Frischkäse, Doppelrahmstufe", 250, 3, 6, 24], ["Frischkäse, light", 145, 4, 9, 10],
    ["Gouda, mittelalt", 355, 0, 25, 28], ["Emmentaler", 380, 0, 28, 30],
    ["Bergkäse", 400, 0, 29, 31], ["Parmesan", 400, 0, 36, 28],
    ["Mozzarella", 250, 1, 18, 19], ["Mozzarella, light", 165, 1, 22, 8],
    ["Feta", 265, 1, 14, 22], ["Camembert", 290, 0.5, 20, 23],
    ["Harzer Käse", 125, 0, 30, 0.7], ["Schmelzkäse", 280, 4, 12, 24],
    ["Butter", 740, 0.6, 0.7, 82], ["Margarine", 720, 0.4, 0.2, 80],
    ["Ei, Größe M", 80, 0.4, 7, 5.7, "st"], ["Eiklar", 52, 0.7, 11, 0.2],
    ["Eigelb", 350, 0.6, 16, 31],
    ["Buttermilch", 35, 4.5, 3.4, 0.5, "ml"], ["Kefir", 45, 4, 3.3, 1.5, "ml"],
    ["Ricotta", 155, 3, 9, 11], ["Ziegenkäse, weich", 300, 0.5, 19, 25],
    ["Halloumi", 320, 2, 22, 25], ["Kondensmilch 7,5 %", 135, 9.5, 7, 7.5, "ml"],
    // Hülsenfrüchte und pflanzliches Eiweiß
    ["Linsen, roh", 340, 50, 24, 1.5], ["Rote Linsen, roh", 350, 52, 24, 1.5],
    ["Linsen, Dose, abgetropft", 105, 15, 8, 0.5], ["Kichererbsen, roh", 365, 45, 19, 6],
    ["Kichererbsen, Dose", 120, 15, 7, 2.6], ["Kidneybohnen, Dose", 110, 14, 8, 0.6],
    ["Weiße Bohnen, Dose", 100, 14, 7, 0.5], ["Zuckerschoten", 42, 5, 3, 0.2], ["Erbsen, TK", 80, 11, 5.5, 0.5],
    ["Tofu, natur", 130, 1, 14, 8], ["Räuchertofu", 165, 1, 17, 10],
    ["Tempeh", 190, 8, 19, 9], ["Seitan", 145, 4, 25, 2],
    ["Sojaschnetzel, trocken", 340, 20, 50, 2], ["Hummus", 250, 15, 8, 17],
    ["Erdnussbutter", 600, 12, 25, 50],
    ["Edamame", 120, 8, 11, 5], ["Schwarze Bohnen, Dose", 90, 12, 7, 0.5],
    ["Erbsenprotein-Pulver", 380, 5, 80, 6],
    // Gemüse
    ["Brokkoli", 34, 3, 3.8, 0.4], ["Blumenkohl", 25, 3, 2.5, 0.3],
    ["Karotten", 40, 7, 0.9, 0.2, "g", "Möhren Mohrrüben Karotte", 70], ["Zucchini", 19, 2, 1.6, 0.4],
    ["Aubergine", 25, 3, 1, 0.2, "g", "Melanzani"], ["Paprika, rot", 37, 6, 1, 0.4, "g", "Paprikaschote", 150],
    ["Tomaten", 18, 3, 0.9, 0.2, "g", "Paradeiser Tomate", 90], ["Kirschtomaten", 20, 3.4, 0.9, 0.2],
    ["Passierte Tomaten", 32, 5, 1.4, 0.2], ["Tomatenmark", 80, 13, 4, 0.5],
    ["Gurke", 12, 1.8, 0.6, 0.1], ["Eisbergsalat", 13, 2, 0.9, 0.2],
    ["Feldsalat", 21, 0.7, 2, 0.4], ["Rucola", 25, 2, 2.6, 0.7],
    ["Spinat, frisch", 23, 0.6, 2.9, 0.4], ["Spinat, TK", 25, 1, 3, 0.4],
    ["Zwiebeln", 28, 5, 1.2, 0.2], ["Knoblauch", 140, 28, 6, 0.5],
    ["Lauch", 29, 3.3, 2.2, 0.3, "g", "Porree"], ["Champignons", 22, 0.6, 2.7, 0.3, "g", "Pilze"],
    ["Kräuterseitlinge", 33, 3, 3, 0.4, "g", "Pilze"], ["Weißkohl", 25, 4, 1.3, 0.2, "g", "Kraut"],
    ["Rotkohl", 30, 4.5, 1.5, 0.2], ["Rosenkohl", 36, 3.3, 4.5, 0.3],
    ["Grünkohl", 45, 2.5, 4.3, 0.9], ["Sauerkraut", 20, 1, 1.5, 0.3],
    ["Kürbis, Hokkaido", 63, 12, 1.7, 0.5], ["Knollensellerie", 30, 2.3, 1.6, 0.3],
    ["Rote Bete", 43, 8, 1.5, 0.2], ["Radieschen", 15, 2, 1, 0.1],
    ["Mais, Dose", 90, 16, 3, 1.2], ["Grüne Bohnen", 32, 5, 2.4, 0.2],
    ["Spargel", 20, 2, 2, 0.2], ["Avocado", 160, 1, 2, 15, "g", null, 150],
    ["Oliven, grün", 145, 1, 1, 14], ["Ingwer", 80, 15, 1.8, 0.8],
    ["Chili, frisch", 40, 6, 2, 0.4],
    ["Pak Choi", 13, 1.2, 1.5, 0.2], ["Fenchel", 20, 3, 1.2, 0.2],
    ["Kohlrabi", 27, 4, 2, 0.1], ["Okra", 33, 4, 2, 0.2],
    ["Artischocke", 47, 6, 3, 0.2], ["Rettich", 16, 2, 1, 0.1],
    ["Wirsing", 27, 3, 3, 0.4], ["Staudensellerie", 16, 2, 0.7, 0.2, "g", "Selleriestange Stangensellerie"],
    ["Frühlingszwiebel", 32, 4.5, 1.8, 0.2, "g", "Lauchzwiebel"], ["Schalotte", 72, 14, 2.5, 0.1],
    // Obst
    ["Apfel", 52, 12, 0.3, 0.2, "g", null, 150], ["Banane", 90, 20, 1.1, 0.3, "g", null, 120],
    ["Orange", 47, 9, 0.9, 0.1, "g", null, 150], ["Birne", 55, 12, 0.4, 0.1, "g", null, 150],
    ["Mandarine", 50, 12, 0.7, 0.2, "g", "Clementine Klementine", 70],
    ["Erdbeeren", 32, 6, 0.7, 0.3], ["Heidelbeeren", 45, 9, 0.7, 0.3],
    ["Himbeeren", 34, 5, 1.2, 0.3], ["Weintrauben", 70, 16, 0.7, 0.2],
    ["Kiwi", 60, 11, 1, 0.5, "g", null, 75], ["Ananas", 50, 12, 0.5, 0.1],
    ["Mango", 60, 13, 0.8, 0.4], ["Wassermelone", 30, 7, 0.6, 0.2],
    ["Pfirsich", 39, 8, 0.9, 0.2, "g", null, 130], ["Zitrone", 30, 3, 1, 0.3],
    ["Datteln, getrocknet", 280, 65, 2.5, 0.4], ["Rosinen", 300, 70, 3, 0.5],
    ["Aprikosen, getrocknet", 240, 50, 3.5, 0.5], ["Apfelmus, ungesüßt", 45, 10, 0.3, 0.1],
    ["Pflaumen", 46, 10, 0.7, 0.3], ["Kirschen", 63, 14, 1, 0.2],
    ["Nektarine", 44, 9, 1.1, 0.3, "g", null, 130], ["Granatapfel", 68, 14, 1.5, 0.5],
    ["Papaya", 43, 8, 0.6, 0.3], ["Feigen, frisch", 65, 14, 0.8, 0.3],
    ["Brombeeren", 35, 5, 1.4, 0.4], ["Johannisbeeren, rot", 35, 6, 1.3, 0.2],
    ["Preiselbeeren", 45, 8, 0.4, 0.3],
    // Nüsse, Samen, Öle
    ["Mandeln", 580, 5, 21, 50], ["Walnüsse", 650, 7, 15, 63],
    ["Cashewkerne", 560, 27, 18, 44], ["Haselnüsse", 640, 7, 14, 61],
    ["Erdnüsse", 570, 8, 25, 48], ["Pistazien", 570, 17, 20, 45],
    ["Sonnenblumenkerne", 580, 12, 21, 49], ["Kürbiskerne", 560, 12, 25, 46],
    ["Leinsamen", 530, 3, 24, 42], ["Chiasamen", 480, 5, 17, 31],
    ["Sesamöl", 884, 0, 0, 100], ["Olivenöl", 900, 0, 0, 100, "ml", "Öl Speiseöl"], ["Rapsöl", 900, 0, 0, 100, "ml", "Öl Speiseöl"],
    ["Sonnenblumenöl", 900, 0, 0, 100, "ml", "Öl Speiseöl"], ["Kokosöl", 900, 0, 0, 100, "ml", "Öl"],
    ["Kokosmilch", 190, 3, 2, 19, "ml"],
    ["Paranüsse", 660, 4, 14, 66], ["Macadamianüsse", 720, 5, 8, 76],
    ["Pekannüsse", 690, 4, 9, 72], ["Kokosraspeln", 600, 6, 6, 57],
    ["Studentenfutter", 480, 30, 14, 35],
    // Süßes, Snacks, Würzendes
    ["Zucker", 400, 100, 0, 0], ["Honig", 305, 75, 0.4, 0],
    ["Ahornsirup", 260, 65, 0, 0], ["Marmelade", 250, 60, 0.4, 0.1],
    ["Zartbitterschokolade 70 %", 570, 33, 8, 42], ["Vollmilchschokolade", 540, 57, 7, 31],
    ["Nuss-Nougat-Creme", 540, 57, 6, 31], ["Kartoffelchips", 540, 50, 6, 34],
    ["Salzstangen", 370, 75, 10, 2], ["Reiswaffeln", 385, 82, 8, 3, "g", null, 9],
    ["Speiseeis, Vanille", 200, 22, 3.5, 11], ["Proteinpulver, Whey", 380, 5, 78, 6, "g", "Eiweißpulver Shake Molkenprotein"],
    ["Proteinriegel", 350, 30, 33, 10], ["Ketchup", 110, 24, 1.2, 0.1],
    ["Mayonnaise", 700, 2, 1, 75], ["Senf", 90, 5, 5, 5],
    ["Sojasoße", 60, 5, 8, 0, "ml"], ["Balsamico-Essig", 90, 17, 0.5, 0, "ml"],
    ["Gemüsebrühe, zubereitet", 5, 0.5, 0.2, 0.2, "ml"],
    ["Popcorn, ungesüßt", 385, 60, 11, 13], ["Müsliriegel", 400, 60, 7, 14],
    ["Traubenzucker", 400, 100, 0, 0, "g", "Dextrose"], ["Puderzucker", 400, 100, 0, 0],
    ["Agavendicksaft", 310, 76, 0.2, 0.5], ["Frischhefe", 105, 3, 12, 0.4, "g", "Hefe"],
    ["Speisestärke", 350, 88, 0.3, 0.1, "g", "Stärke Maisstärke"], ["Vanillezucker", 380, 95, 0, 0],
    ["Pesto", 450, 5, 5, 45], ["Currypaste, rot", 100, 10, 3, 6],
    ["Barbecue-Soße", 170, 38, 1, 0.5, "g", "BBQ-Soße"],
    // Getränke
    ["Orangensaft", 45, 10, 0.7, 0.1, "ml"], ["Apfelsaft", 46, 11, 0.1, 0.1, "ml"],
    ["Cola", 42, 10.6, 0, 0, "ml"], ["Bier", 43, 3.6, 0.5, 0, "ml"],
    ["Rotwein", 85, 2.6, 0.1, 0, "ml"], ["Weißwein", 82, 2, 0.1, 0, "ml"],
    ["Sekt / Prosecco", 80, 2, 0.2, 0, "ml"], ["Kaffee, schwarz", 1, 0, 0.1, 0, "ml"],
    ["Energydrink", 45, 11, 0, 0, "ml"]
  ];
  /*FOODS_END*/
