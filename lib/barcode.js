/* barcode.js - Paddy's Mealplan
 *
 * Barcode-Infrastruktur: ZXing nachladen, Codes erkennen, Naehrwerte bei Open Food Facts holen.
 *
 * Der sichtbare Sucher (scanBarcodeLive) bleibt bewusst im Kern: er haengt am Overlay-Stapel der Zurueck-Taste (overlayOpened/overlayClosed) und ist damit UI-gebunden, nicht Infrastruktur.
 *
 * Fassade nach dem Vorbild der Firebase-Bruecke (window.CloudAuth & Co.):
 * der Kern holt sich die Namen einmal am Anfang der IIFE, alle Aufrufstellen
 * bleiben dadurch unveraendert.
 */
(function (global) {
  "use strict";

  // ---------- Barcode-Scan (Open Food Facts) ----------
  // Foto vom Barcode -> Code lokal aus dem Bild lesen -> Nummer bei Open Food Facts
  // nachschlagen. Nur die Barcode-NUMMER verlaesst das Geraet, nie das Foto selbst.
  // Erkennung bevorzugt die native BarcodeDetector-API (Chrome/Edge/Android); die
  // gibt es auf iOS/Safari nicht - dort laedt loadZXing() beim ersten Scan eine
  // Open-Source-Bibliothek (ZXing) nach. Sie liegt seit Paket A2 LOKAL im Repo
  // (vendor/zxing.min.js, @zxing/library@0.21.3), nicht mehr auf einem Fremd-CDN:
  // kein Drittserver-Abruf, offline-tauglich und Store-konform (kein Remote-Code).
  // Relativer Pfad wegen des GitHub-Pages-Unterpfads /mealplan/.
  let zxLoad = null;
  function loadZXing() {
    if (window.ZXing) return Promise.resolve();
    if (!zxLoad) zxLoad = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = "vendor/zxing.min.js";
      s.onload = resolve;
      s.onerror = () => { zxLoad = null; s.remove(); reject(new Error("zxing-load")); };
      document.head.appendChild(s);
    });
    return zxLoad;
  }
  const BARCODE_FORMATS = ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"];
  // Barcode-Icon, geteilt zwischen Zutatenzeile (applyBarcode) und Plan-Schnellzugriff
  // (quickAddByBarcode) - ein Icon fuer denselben Scan-Einstieg statt zwei Kopien.
  const BARCODE_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round"><path stroke-width="2.4" d="M4 5v14"/><path stroke-width="1.4" d="M7.5 5v14"/><path stroke-width="2.4" d="M10.5 5v14"/><path stroke-width="1.4" d="M13.5 5v14"/><path stroke-width="1.4" d="M16.5 5v14"/><path stroke-width="2.4" d="M19.5 5v14"/></svg>`;
  // Eigene Liste fuer den Einladungs-Scanner - BARCODE_FORMATS bewusst NICHT um "qr_code"
  // erweitern, sonst wuerde der Zutaten-Scanner ploetzlich auch QR-Codes annehmen.
  const QR_FORMATS = ["qr_code"];
  // QR-Code fuer die Einladung zeichnen. Laeuft ueber dieselbe lokale ZXing-Bibliothek wie
  // der Scanner (vendor/zxing.min.js) - keine zweite Abhaengigkeit, kein CDN.
  async function qrSvg(text, size) {
    await loadZXing();
    const writer = new window.ZXing.BrowserQRCodeSvgWriter();
    const svg = writer.write(text, size, size);
    // BrowserQRCodeSvgWriter setzt nur width/height, kein viewBox - die Module bleiben in
    // absoluten Nutzereinheiten. Ohne viewBox skaliert das CSS (width/height: 100%) die
    // Zeichenflaeche zwar, aber die Module selbst wandern nicht mit - kleinere Container
    // schneiden dann echte Modulspalten ab, statt den Code zu verkleinern.
    svg.setAttribute("viewBox", "0 0 " + size + " " + size);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "QR-Code für die Einladung");
    return svg;
  }
  async function detectBarcode(file) {
    if (window.BarcodeDetector) {
      try {
        const det = new window.BarcodeDetector({ formats: BARCODE_FORMATS });
        const bmp = await createImageBitmap(file);
        const hits = await det.detect(bmp);
        if (hits && hits[0] && hits[0].rawValue) return hits[0].rawValue;
      } catch (e) { /* z. B. Format nicht unterstuetzt - fällt auf ZXing zurueck */ }
    }
    await loadZXing();
    const url = URL.createObjectURL(file);
    try {
      const reader = new window.ZXing.BrowserMultiFormatReader();
      const res = await reader.decodeFromImageUrl(url);
      return res && res.getText ? res.getText() : null;
    } finally {
      URL.revokeObjectURL(url);
    }
  }
  // Open Food Facts liefert die Naehrwerte unabhaengig von fest/fluessig immer unter
  // den "_100g"-Feldern (auch Cola steht unter carbohydrates_100g, nicht _100ml) -
  // deshalb reicht hier eine feste Basis, ohne nach Einheit zu unterscheiden.
  // Produktname: die deutschen Felder zuerst — "product_name" ist bei hier ueblichen
  // Produkten haeufig die englische oder kleingeschriebene Fassung ("coca-cola"),
  // waehrend "product_name_de" den Namen liefert, den man auf der Packung liest.
  // Beschreibende generic_name-Felder als letzter Ausweg, damit lieber "Nuss-Nugat-Creme"
  // im Feld steht als gar nichts. Laenge auf das maxlength des Eingabefelds gekappt.
  function offName(p) {
    const cands = [p.product_name_de, p.product_name, p.generic_name_de, p.generic_name];
    for (let i = 0; i < cands.length; i++) {
      const s = String(cands[i] == null ? "" : cands[i]).replace(/\s+/g, " ").trim();
      if (s) return s.slice(0, 60);
    }
    return null;
  }
  // Wertet OFF's serving_size/quantity-Feld aus ("65 g", "1 Stück (65 g)", "6 x 65 g").
  // grams ist das erkannte Gewicht der Bezugsgroesse - bei "1 Stück (65 g)" das eines
  // einzelnen Stuecks, bei "6 x 65 g" ebenfalls eines einzelnen Stuecks (count traegt die
  // Anzahl), bei reinem "500 g" das der ganzen Packung. count ist NUR gesetzt, wenn eine
  // Stueckzahl im Text stand - erst dann darf ein Aufrufer die Einheit auf "Stück"
  // umschalten. Ohne jede erkennbare Zahl+Einheit liefert die Funktion null.
  function offServingSize(p) {
    // serving_size (echte Portionsangabe) hat Vorrang vor quantity (Packungsgroesse);
    // serving sagt dem Aufrufer, welche der beiden Quellen gewonnen hat - eine
    // Packungsgroesse ist KEINE Portion (siehe quickAddByBarcode).
    // Komma global ersetzen: OFF-Texte tragen oft mehr als eine Zahl ("1,5 l (1,58 kg)").
    const serv = String((p && p.serving_size) || "").trim();
    const raw = (serv || String((p && p.quantity) || "")).replace(/,/g, ".").trim();
    if (!raw) return null;
    // "x" und das Mal-Zeichen "×" kommen bei OFF beide vor ("6 x 65 g", "6 × 65 g").
    const multi = raw.match(/(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(g|ml)\b/i);
    if (multi) {
      const count = parseFloat(multi[1]), grams = parseFloat(multi[2]);
      if (count > 0 && grams > 0) return { grams, count, serving: !!serv };
    }
    const piece = raw.match(/(\d+(?:\.\d+)?)\s*(?:stück|stk|riegel|scheiben?|packung|beutel)\.?\D*?(\d+(?:\.\d+)?)\s*(g|ml)/i);
    if (piece) {
      const count = parseFloat(piece[1]), grams = parseFloat(piece[2]);
      if (count > 0 && grams > 0) return { grams, count, serving: !!serv };
    }
    const plain = raw.match(/(\d+(?:\.\d+)?)\s*(g|ml|l|kg)\b/i);
    if (plain) {
      let grams = parseFloat(plain[1]);
      const unit = plain[2].toLowerCase();
      if (unit === "l" || unit === "kg") grams *= 1000;
      if (grams > 0) return { grams, count: null, serving: !!serv };
    }
    return null;
  }
  async function fetchOffNutrition(code) {
    const url = "https://world.openfoodfacts.org/api/v2/product/" + encodeURIComponent(code) +
      ".json?fields=product_name,product_name_de,generic_name,generic_name_de,nutriments,status,serving_size,quantity";
    const res = await fetch(url);
    if (!res.ok) throw new Error("off-http-" + res.status);
    const data = await res.json();
    if (data.status !== 1 || !data.product) return null;
    const n = data.product.nutriments || {};
    const num = v => (typeof v === "number" && isFinite(v) && v >= 0) ? v : null;
    const kcal = num(n["energy-kcal_100g"]), carbs = num(n.carbohydrates_100g),
          protein = num(n.proteins_100g), fat = num(n.fat_100g);
    if (kcal == null && carbs == null && protein == null && fat == null) return null;
    return { name: offName(data.product), kcal, carbs, protein, fat, servingSize: offServingSize(data.product) };
  }

  global.PM = global.PM || {};
  global.PM.barcode = {
    BARCODE_FORMATS: BARCODE_FORMATS,
    BARCODE_SVG: BARCODE_SVG,
    QR_FORMATS: QR_FORMATS,
    detectBarcode: detectBarcode,
    fetchOffNutrition: fetchOffNutrition,
    loadZXing: loadZXing,
    offServingSize: offServingSize,
    qrSvg: qrSvg,
  };
})(window);
