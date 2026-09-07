/* bilder.js - Paddy's Mealplan
 *
 * Gerichtsfotos: Zuordnung und Stichwortregeln.
 *
 * Reine Daten, keine Logik. Ausgeschnitten aus index.html, unveraendert.
 * Wird als klassisches <script> VOR der App-IIFE geladen; die Konstanten stehen
 * dadurch im globalen Bereich und werden von der IIFE gelesen.
 *
 * Regeln fuer diesen Ordner: data/CLAUDE.md
 */
  // ---------- Gerichtsfotos (nach Namen zugeordnet) ----------
  //
  // BILDRECHTE: Alle mitgelieferten Gerichtsfotos sind SELBST erzeugt - mit
  // tools/meal-bilder.py ueber die OpenAI Images API (gpt-image-2). Die kommerzielle
  // Nutzung ist nach den OpenAI-Nutzungsbedingungen erlaubt. Zu jedem Bild ist in
  // img/bilder-protokoll.json festgehalten, mit welcher Beschreibung und wann es
  // entstanden ist; im Impressum steht dazu ein Sammelhinweis.
  //
  // Bis zum 07.09.2026 waren das CC0-Stockfotos aus fremden Quellen, jedes mit einem
  // eigenen Nachweis in einer Konstante PHOTO_CREDITS. Die ist mit dem Austausch
  // entfallen - es gibt keinen fremden Urheber mehr zu nennen.
  //
  // NEUE BILDER ENTSTEHEN UEBER tools/meal-bilder.py, nicht von Hand und nicht aus
  // fremden Quellen. Der Stil-Baustein im Werkzeug ist eingefroren; wer ihn aendert,
  // muss die ganze Sammlung neu erzeugen. Beschreibungen der Motive stehen in
  // tools/bildsatz-stichworte.json.
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

    // Seit 07.09.2026. Die zwoelf schliessen die Luecken, die beim Messen an typischen
    // Gerichtnamen auffielen: Schnitzel landete auf einem Ribeye-Steak, Currywurst auf
    // einem Burger, jede Gemuesepfanne auf Blattsalat, Skyr auf einer Obstschale - und
    // Edamame, Proteinriegel oder Tempeh auf gar nichts. Gerade der Fitness-Bereich war
    // am duennsten besetzt, weil die Liste aelter ist als das Rezeptbuch.
    "schnitzel": "img/schnitzel.webp",
    "wurst": "img/wurst.webp",
    "braten": "img/braten.webp",
    "hack": "img/hack.webp",
    "tofu": "img/tofu.webp",
    "legumes": "img/legumes.webp",
    "bowl": "img/bowl.webp",
    "veggiepan": "img/veggiepan.webp",
    "skyr": "img/skyr.webp",
    "nuts": "img/nuts.webp",
    "shake": "img/shake.webp",
    "grain": "img/grain.webp",
  };
  /*PHOTOS_END*/
  // Reihenfolge: spezifisch -> generisch, erster Treffer gewinnt.
  // Vorsicht bei Teilwoertern: "eis" steckt auch in "Rindfleisch", "reis" in "Preiselbeere".
  //
  // Vier Stellen, an denen die REIHENFOLGE die eigentliche Aussage ist - sie stehen so,
  // weil includes() keine Wortgrenzen kennt. tools/pruefstand-bildstichworte.py haelt sie fest:
  //   * "schnitzel" vor "wurst"  - "Wiener Schnitzel" enthaelt "wiener".
  //   * "wurst" vor "curry"      - "Currywurst" enthaelt "curry".
  //   * "pasta" vor "hack"       - "Nudeln mit Hackfleisch" ist ein Nudelgericht.
  //   * "salat" vor "veggiepan"  - "Gemuesesalat" enthaelt beides, gemeint ist der Salat.
  //   * "sandwich" vor "nuts"    - "Erdnussbutter-Brot" ist ein Brot, kein Nussteller.
  // Aus demselben Grund steht in "braten" NICHT das Wort "braten": es steckt in
  // "gebratener Reis" und haette jede Pfanne zum Schweinebraten gemacht.
  const PHOTO_RULES = [
    [["nudelsuppe","ramen","pho ","udon","soba","glasnudel","bami","pad thai","yakisoba","chow mein","wok"], "noodle"],
    [["schnitzel","cordon bleu","paniert"], "schnitzel"],
    [["currywurst","bratwurst","würstchen","wuerstchen","wiener","hotdog","hot dog","weißwurst","weisswurst","leberkäse","leberkaese","fleischkäse","fleischkaese"], "wurst"],
    [["burger","cheeseburger","hamburger"], "burger"],
    [["curry","dal","dhal","tikka","masala","korma","madras","vindaloo"], "curry"],
    [["pizza","flammkuchen","calzone","focaccia"], "pizza"],
    [["auflauf","gratin","überbacken","ueberbacken","lasagne","moussaka"], "casserole"],
    [["spaghetti","pasta","bolognese","penne","tagliatelle","carbonara","spätzle","spaetzle","gnocchi","tortellini","ravioli","maccheroni","makkaroni","nudel","cannelloni","fusilli","farfalle","rigatoni","linguine","pesto","arrabbiata","schupfnudel","maultasche"], "pasta"],
    [["frikadelle","bulette","hackbraten","hackfleisch","hackbällchen","hackbaellchen","fleischbällchen","fleischbaellchen","köfte","koefte"], "hack"],
    [["porridge","haferbrei","haferflocken","müsli","muesli","granola","overnight","oats","chia","grießbrei","griessbrei","milchreis"], "porridge"],
    [["waffel","waffle"], "waffle"],
    [["toast","french toast","arme ritter"], "toast"],
    [["pfannkuchen","eierkuchen","pancake","crêpe","crepe","kaiserschmarrn"], "pancake"],
    [["omelett","rührei","ruehrei","spiegelei","frittata","shakshuka","eier","pochiert","benedict"], "egg"],
    [["käseplatte","kaeseplatte","käsebrett","kaesebrett","raclette","fondue"], "cheese"],
    [["salat","salad","caprese","rohkost","coleslaw","antipasti"], "salad"],
    [["bowl"], "bowl"],
    [["eintopf","chili","gulasch"], "stew"],
    [["suppe","brühe","bruehe","soup","minestrone","gazpacho","bouillon"], "soup"],
    [["sushi","maki","sashimi","poke","calamari","tintenfisch"], "sushi"],
    [["garnele","shrimp","scampi","gambas","muschel","meeresfrüchte","meeresfruechte","auster"], "seafood"],
    [["lachs","salmon","fisch","forelle","thunfisch","kabeljau","dorsch","seelachs","scholle","hering","matjes"], "fish"],
    [["tofu","tempeh","seitan","sojaschnetzel","sojagranulat"], "tofu"],
    [["hähnchen","haehnchen","huhn","hühn","huehn","chicken","geflügel","gefluegel","pute","truthahn","hendl","wings","nuggets"], "chicken"],
    [["steak","filet","medaillon"], "steak"],
    [["schweinebraten","rollbraten","krustenbraten","sauerbraten","roulade","kassler","haxe","kotelett","schwein","lamm","spareribs","pulled pork","ente","gans"], "braten"],
    [["rind","fleisch","geschnetzeltes","ragout","speck","bacon","schinken"], "beef"],
    [["risotto","paella","reis","rice","bibimbap","jambalaya"], "rice"],
    [["quinoa","couscous","bulgur","hirse","buchweizen","amaranth"], "grain"],
    [["wrap","döner","doener","kebab","dürüm","duerum","gyros","burrito","quesadilla"], "wrap"],
    [["taco"], "taco"],
    [["sandwich","baguette","stulle","panini","brötchen","broetchen","brot","falafel","bagel","ciabatta","croissant","brezel","brezn"], "sandwich"],
    [["nuss","nüsse","nuesse","mandel","walnuss","cashew","pistazie","energy ball","energyball","proteinriegel","protein riegel","riegel","dattel"], "nuts"],
    [["eiscreme","speiseeis","sorbet","gelato"], "icecream"],
    [["kuchen","torte","cake","brownie","muffin","cupcake","dessert","schokolade","schoko","tiramisu","gebäck","gebaeck","donut","pudding","mousse","creme","crème","panna cotta","strudel","keks","cookie","quiche","tarte"], "cake"],
    [["kartoffel","erdäpfel","erdaepfel","püree","puree","rösti","roesti","pommes","fritten","fries","kroketten","knödel","knoedel","kloß","kloss","bratkartoffel","ofenkartoffel","wedges"], "potato"],
    [["kichererbse","linsen","bohnen","edamame","hummus","erbsen"], "legumes"],
    [["gemüsepfanne","gemuesepfanne","ofengemüse","ofengemuese","blechgemüse","blechgemuese","gemüse","gemuese","veggie","vegetarisch","vegan","ratatouille","spinat","brokkoli","blumenkohl","spargel","grünkohl","gruenkohl","zucchini","aubergine","pilz","champignon","zoodles"], "veggiepan"],
    [["skyr","magerquark","quark","topfen","hüttenkäse","huettenkaese","körniger frischkäse","koerniger frischkaese","joghurt"], "skyr"],
    [["proteinshake","protein shake","eiweißshake","eiweissshake","whey","shake"], "shake"],
    [["kaffee","espresso","cappuccino","latte"], "coffee"],
    [["smoothie","saft","limonade","tee ","matcha","kakao","milch"], "drink"],
    [["apfel","banane","beere","erdbeer","himbeer","obst","frucht","melone","birne","orange","traube","kirsche","mango","ananas","pfirsich"], "fruit"],
  ];
  // Zweite Chance, wenn kein Stichwort greift: passendes Foto je Kategorie.
  // Hauptgericht fehlt bewusst - das kann alles sein, dort passt das neutrale Bild.
  const CAT_PHOTO = { "Frühstück": "porridge", "Snack": "fruit", "Dessert": "cake", "Beilage": "salad", "Getränk": "drink" };
