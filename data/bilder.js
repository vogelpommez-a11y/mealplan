/* bilder.js - Paddy's Mealplan
 *
 * Gerichtsfotos: Zuordnung, Stichwortregeln und Bildnachweise.
 *
 * Reine Daten, keine Logik. Ausgeschnitten aus index.html, unveraendert.
 * Wird als klassisches <script> VOR der App-IIFE geladen; die Konstanten stehen
 * dadurch im globalen Bereich und werden von der IIFE gelesen.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  // ---------- Gerichtsfotos (eingebettet, nach Namen zugeordnet) ----------
  //
  // BILDRECHTE: Alle Fotos stehen unter CC0 1.0 bzw. Public Domain Mark 1.0.
  // Das erlaubt kommerzielle Nutzung, Bearbeitung und Weitergabe ohne Namensnennung.
  // Die Nennung unten erfolgt trotzdem - freiwillig, als Herkunftsnachweis.
  // Bezogen ueber Openverse (openverse.org) und Wikimedia Commons, geprueft am 2026-07-15.
  // Die Bilder wurden mittig auf 460x300 zugeschnitten; sonst unveraendert.
  //
  // Neue Fotos NUR aus Quellen mit belegter freier Lizenz ergaenzen und hier
  // mit Titel, Urheber, Lizenz und Fundstelle eintragen.
  /*CREDITS_START*/
  const PHOTO_CREDITS = {
    pasta: { titel: "Spaghetti Bolognese", urheber: "chooyutshing", lizenz: "Public Domain Mark 1.0", lizenzUrl: "https://creativecommons.org/publicdomain/mark/1.0/", quelle: "https://www.flickr.com/photos/25802865@N08/54706781448" },
    curry: { titel: "Beef curry rice 003", urheber: "Ocdp", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Beef_curry_rice_003.jpg" },
    salad: { titel: "Salad Lettuce", urheber: "Jeffrey Betts", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/salad-lettuce-Z0133GNPXT" },
    porridge: { titel: "Granola Dark Chocolate and Banana", urheber: "Bajinra", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Granola_Dark_Chocolate_and_Banana.jpg" },
    pizza: { titel: "Pizza Cheese", urheber: "Krzysztof Puszczyński", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/pizza-cheese-9IKVHJPX82" },
    burger: { titel: "Hamburgers Buns", urheber: "Niklas Rhöse", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/hamburgers-buns-FNX2GU2Y5P" },
    chicken: { titel: "Free roasted chicken half. cutting", urheber: "ohne Angabe", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://www.rawpixel.com/image/5904464/photo-image-public-domain-wood-food" },
    beef: { titel: "Steak Asparagus", urheber: "Snapwire", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/steak-asparagus-JMJZKYXUWD" },
    fish: { titel: "Salmon Fillet", urheber: "NjoyHarmony", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:SalmonFillet.jpg" },
    soup: { titel: "Free pumpkin soup bowl image", urheber: "ohne Angabe", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://www.rawpixel.com/image/5922901/photo-image-public-domain-leaf-fruit" },
    rice: { titel: "Rice Bowl", urheber: "Kawin Harasai", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/rice-bowl-CCBWIQCNEJ" },
    pancake: { titel: "Pancakes Syrup", urheber: "Altered Reality", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/pancakes-syrup-VD2NUQHVJS" },
    noodle: { titel: "Ramen Noodles", urheber: "Foodie Girl", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/ramen-noodles-KKMQPWQK6H" },
    egg: { titel: "Fried Egg", urheber: "Jarosław Ceborski", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/fried-egg-USO5VWLM54" },
    cake: { titel: "Free chocolate cake slice image", urheber: "ohne Angabe", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://www.rawpixel.com/image/5916247/image-public-domain-food-chocolate" },
    sandwich: { titel: "Food Sandwich", urheber: "Jay Mantri", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/food-sandwich-K5T076FWTJ" },
    potato: { titel: "Free roast potatoes pan image", urheber: "ohne Angabe", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://www.rawpixel.com/image/5917456/image-public-domain-nature-food" },
    drink: { titel: "Strawberry Smoothies", urheber: "WDnet Studio", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/strawberry-smoothies-4L8M6ANLZL" },
    fruit: { titel: "Fruit Bowl", urheber: "Suzy Hazelwood", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://stocksnap.io/photo/fruit-bowl-4MUZH41WMD" },
    neutral: { titel: "Table Setting in Restaurant", urheber: "ohne Angabe", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://www.rawpixel.com/image/5968716/table-setting-restaurant" },
  
    wrap: { titel: "Chicken Shawarma Wrap", urheber: "Andy Li", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Chicken_Shawarma_Wrap_-_Lavash_2024-09-11.jpg" },
    taco: { titel: "Tacos in a Soft Tortilla", urheber: "Kurt Kaiser", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Tacos_in_a_soft_tortilla_4.jpg" },
    toast: { titel: "Avocado on Toast", urheber: "Andy Li", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Avocado_on_Toast_-_Cadence_Clubhouse,_Newhaven_Fort_2025-05-06.jpg" },
    sushi: { titel: "Sushi Plate", urheber: "Mojmir Churavy", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Sushi_Plate_in_Organic_Sushi_Prague_4.jpg" },
    seafood: { titel: "Shrimp Cocktail", urheber: "Daderot", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Shrimp_cocktail_-_Massachusetts.jpg" },
    steak: { titel: "Ribeye Steaks", urheber: "Jon Sullivan", lizenz: "Public Domain Mark 1.0", lizenzUrl: "https://creativecommons.org/publicdomain/mark/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Ribeyes.jpeg" },
    icecream: { titel: "Ice Cream Cone", urheber: "Alex Jones", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Ice_Cream_Dessert_(Unsplash).jpg" },
    waffle: { titel: "Waffle with Granola", urheber: "Andy Li", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:%22granola_breakfast%22_waffle_-_Wafflemeister_2024-08-25.jpg" },
    coffee: { titel: "Coffee Latte", urheber: "Petr Kratochvil", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Coffee-latte_-_Petr_Kratochvil.jpg" },
    casserole: { titel: "Slice of Lasagna", urheber: "Roundhere44", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Slice_of_Lasagna.jpg" },
    stew: { titel: "Beef Stew", urheber: "Kykk wiki", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Beef_stew_kikusui.jpg" },
    cheese: { titel: "Cheese Board", urheber: "Daderot", lizenz: "CC0 1.0 (Public Domain Dedication)", lizenzUrl: "https://creativecommons.org/publicdomain/zero/1.0/", quelle: "https://commons.wikimedia.org/wiki/File:Cheese_board_-_Christchurch,_New_Zealand.jpg" },
  };
  /*CREDITS_END*/
  /*PHOTOS_START*/
  const PHOTOS = {
    "pasta": "img/pasta.webp",
    "curry": "img/curry.webp",
    "salad": "img/salad.jpg",
    "porridge": "img/porridge.jpg",
    "pizza": "img/pizza.jpg",
    "burger": "img/burger.webp",
    "chicken": "img/chicken.webp",
    "beef": "img/beef.webp",
    "fish": "img/fish.webp",
    "soup": "img/soup.webp",
    "rice": "img/rice.webp",
    "pancake": "img/pancake.webp",
    "noodle": "img/noodle.webp",
    "egg": "img/egg.webp",
    "cake": "img/cake.webp",
    "sandwich": "img/sandwich.jpg",
    "potato": "img/potato.webp",
    "drink": "img/drink.webp",
    "fruit": "img/fruit.webp",
    "neutral": "img/neutral.jpg",
  
    "wrap": "img/wrap.webp",
    "taco": "img/taco.webp",
    "toast": "img/toast.webp",
    "sushi": "img/sushi.webp",
    "seafood": "img/seafood.webp",
    "steak": "img/steak.webp",
    "icecream": "img/icecream.webp",
    "waffle": "img/waffle.webp",
    "coffee": "img/coffee.webp",
    "casserole": "img/casserole.webp",
    "stew": "img/stew.webp",
    "cheese": "img/cheese.webp",
  
  };
  /*PHOTOS_END*/
  // Reihenfolge: spezifisch -> generisch, erster Treffer gewinnt.
  // Vorsicht bei Teilwoertern: "eis" steckt auch in "Rindfleisch", "reis" in "Preiselbeere".
  const PHOTO_RULES = [
    [["nudelsuppe","ramen","pho ","udon","soba","glasnudel","bami","pad thai","yakisoba","chow mein","wok"], "noodle"],
    [["burger","cheeseburger","hamburger","frikadelle","bulette","hotdog","hot dog","currywurst","bratwurst","würstchen","wuerstchen","wiener"], "burger"],
    [["curry","dal","dhal","tikka","masala","korma","madras","vindaloo"], "curry"],
    [["pizza","flammkuchen","calzone","focaccia"], "pizza"],
    [["auflauf","gratin","überbacken","ueberbacken","lasagne","moussaka"], "casserole"],
    [["spaghetti","pasta","bolognese","penne","tagliatelle","carbonara","spätzle","spaetzle","gnocchi","tortellini","ravioli","maccheroni","makkaroni","nudel","cannelloni","fusilli","farfalle","rigatoni","linguine","pesto","arrabbiata","schupfnudel","maultasche"], "pasta"],
    [["porridge","haferbrei","haferflocken","müsli","muesli","granola","overnight","oats","joghurt","quark","magerquark","topfen","hüttenkäse","huettenkaese","chia"], "porridge"],
    [["waffel","waffle"], "waffle"],
    [["toast","french toast","arme ritter"], "toast"],
    [["pfannkuchen","eierkuchen","pancake","crêpe","crepe","kaiserschmarrn"], "pancake"],
    [["omelett","rührei","ruehrei","spiegelei","frittata","shakshuka","eier","pochiert","benedict"], "egg"],
    [["käseplatte","kaeseplatte","käsebrett","kaesebrett","raclette","fondue"], "cheese"],
    [["salat","salad","caprese","bowl","rohkost","coleslaw","antipasti","ratatouille","ofengemüse","ofengemuese","gemüse","gemuese","veggie","vegetarisch","vegan","spinat","brokkoli","spargel","grünkohl","gruenkohl","zucchini","aubergine"], "salad"],
    [["eintopf","chili","gulasch"], "stew"],
    [["suppe","brühe","bruehe","soup","minestrone","gazpacho","bouillon"], "soup"],
    [["sushi","maki","sashimi","poke","calamari","tintenfisch"], "sushi"],
    [["garnele","shrimp","scampi","gambas","muschel","meeresfrüchte","meeresfruechte","auster"], "seafood"],
    [["lachs","salmon","fisch","forelle","thunfisch","kabeljau","dorsch","seelachs","scholle","hering","matjes"], "fish"],
    [["hähnchen","haehnchen","huhn","hühn","huehn","chicken","geflügel","gefluegel","pute","truthahn","hendl","wings","nuggets","cordon bleu"], "chicken"],
    [["steak","filet","medaillon"], "steak"],
    [["rind","schnitzel","roulade","braten","lamm","schwein","kotelett","hackbraten","hackfleisch","fleisch","geschnetzeltes","ragout","spareribs","pulled pork","kassler","haxe","speck","bacon","schinken"], "beef"],
    [["risotto","paella","reis","rice","bibimbap","jambalaya","quinoa","couscous","bulgur"], "rice"],
    [["wrap","döner","doener","kebab","dürüm","duerum","gyros","burrito","quesadilla"], "wrap"],
    [["taco"], "taco"],
    [["sandwich","baguette","stulle","panini","brötchen","broetchen","brot","falafel","bagel","ciabatta","croissant","brezel","brezn"], "sandwich"],
    [["eiscreme","speiseeis","sorbet","gelato"], "icecream"],
    [["kuchen","torte","cake","brownie","muffin","cupcake","dessert","schokolade","schoko","tiramisu","gebäck","gebaeck","donut","pudding","mousse","creme","crème","panna cotta","strudel","keks","cookie","quiche","tarte"], "cake"],
    [["kartoffel","erdäpfel","erdaepfel","püree","puree","rösti","roesti","pommes","fritten","fries","kroketten","knödel","knoedel","kloß","kloss","bratkartoffel","ofenkartoffel","wedges"], "potato"],
    [["kaffee","espresso","cappuccino","latte"], "coffee"],
    [["smoothie","shake","saft","limonade","tee ","matcha","kakao","milch"], "drink"],
    [["apfel","banane","beere","erdbeer","himbeer","obst","frucht","melone","birne","orange","traube","kirsche","mango","ananas","pfirsich"], "fruit"],
  ];
  // Zweite Chance, wenn kein Stichwort greift: passendes Foto je Kategorie.
  // Hauptgericht fehlt bewusst - das kann alles sein, dort passt das neutrale Bild.
  const CAT_PHOTO = { "Frühstück": "porridge", "Snack": "fruit", "Dessert": "cake", "Beilage": "salad", "Getränk": "drink" };
