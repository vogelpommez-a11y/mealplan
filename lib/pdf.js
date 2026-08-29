/* pdf.js - Paddy's Mealplan
 *
 * Eigener PDF-Schreiber: Zeichenkodierung, Marken-Kopf, PNG-Parser, Deflate/Inflate, Byte-Ausgabe.
 *
 * Vollstaendig unabhaengig vom App-Zustand - kein state, kein render, kein DOM der App. buildPrintable() bleibt im Kern, weil es state und getRecipe braucht.
 *
 * Fassade nach dem Vorbild der Firebase-Bruecke (window.CloudAuth & Co.):
 * der Kern holt sich die Namen einmal am Anfang der IIFE, alle Aufrufstellen
 * bleiben dadurch unveraendert.
 */
(function (global) {
  "use strict";

  // ----- PDF selbst erzeugen (kein window.print, sandbox-sicher) -----
  // "×" (0327) fehlte hier - im Ausschneide-Pruefstand fuer den neuen PDF-Marken-Kopf
  // gefunden: Zutaten-Mengen wie "(×3)" in der Einkaufslisten-PDF zeigten "(?3)".
  const WINANSI = { "ä":"344","ö":"366","ü":"374","Ä":"304","Ö":"326","Ü":"334","ß":"337","·":"267","–":"226","—":"227","…":"205","é":"351","è":"350","ê":"352","á":"341","à":"340","â":"342","ç":"347","ñ":"361","€":"200","°":"260","„":"204","“":"223","”":"224","‘":"221","’":"222","×":"327" };
  function pdfEsc(str) {
    let out = "";
    for (const ch of String(str)) {
      const code = ch.codePointAt(0);
      if (ch === "\\") out += "\\\\";
      else if (ch === "(") out += "\\(";
      else if (ch === ")") out += "\\)";
      else if (code >= 32 && code < 127) out += ch;
      else if (WINANSI[ch]) out += "\\" + WINANSI[ch];
      else out += "?";
    }
    return out;
  }
  function trunc(s, n) { s = String(s); return s.length > n ? s.slice(0, n - 1) + "…" : s; }

  // ----- Marken-Kopf fuer die PDFs (Logo, "PADDY'S MEALPLAN", Slogan) -----
  // Nur die Grossbuchstaben/Zeichen, die in der Wortmarke ("PADDY'S MEALPLAN") und im
  // Vektor-Rueckfall-Kreis ("PM") tatsaechlich vorkommen - keine vollstaendige AFM-Tabelle
  // noetig, da Slogan und Metazeilen einfarbig/linksbuendig bleiben und keine Breite brauchen.
  // Werte sind die festen Adobe-Standardbreiten von Helvetica-Bold (1000-Einheiten-Raster,
  // Teil der PDF-Basis-14-Schriften, nicht dokumentspezifisch).
  const HB_WIDTH = { " ": 278, "P": 667, "A": 722, "D": 722, "Y": 722, "’": 278, "S": 667, "M": 833, "E": 667, "L": 556, "N": 722 };
  function hbWidth(str, size) {
    let w = 0;
    for (const ch of str) w += (HB_WIDTH[ch] != null ? HB_WIDTH[ch] : 600);
    return w / 1000 * size;
  }
  // Kreis als 4 Bezier-Kurven (Standardnaeherung, k=0.5523) - rohes PDF kennt keinen
  // Kreis-Operator. f = fuellen; die Fuellfarbe muss VOR dem Aufruf per "rg" gesetzt sein.
  function pdfCirclePath(cx, cy, r) {
    const k = 0.5522847498, rk = r * k;
    return cx + r + " " + cy + " m\n"
      + (cx + r) + " " + (cy + rk) + " " + (cx + rk) + " " + (cy + r) + " " + cx + " " + (cy + r) + " c\n"
      + (cx - rk) + " " + (cy + r) + " " + (cx - r) + " " + (cy + rk) + " " + (cx - r) + " " + cy + " c\n"
      + (cx - r) + " " + (cy - rk) + " " + (cx - rk) + " " + (cy - r) + " " + cx + " " + (cy - r) + " c\n"
      + (cx + rk) + " " + (cy - r) + " " + (cx + r) + " " + (cy - rk) + " " + (cx + r) + " " + cy + " c\nh\n";
  }
  // Logo-Marke: echtes Bild-XObject (logo!=null) oder roter Vektor-Kreis mit "PM" als
  // Rueckfall (gleiches Muster wie der Platzhalter in ROADMAP.html). Path-Operatoren (m/c/f)
  // und "Do" duerfen nicht innerhalb eines BT/ET-Textblocks stehen, deshalb eigene BT/ET
  // nur um den "PM"-Text herum.
  function pdfMarkOps(cx, cy, r, logo) {
    if (logo) {
      const d = r * 2, x = cx - r, y = cy - r;
      return "q\n" + d + " 0 0 " + d + " " + x + " " + y + " cm\n/Im0 Do\nQ\n";
    }
    let ops = "0.863 0.149 0.149 rg\n" + pdfCirclePath(cx, cy, r) + "f\n";
    const fontSize = r * 0.82;
    const tx = cx - hbWidth("PM", fontSize) / 2;
    const ty = cy - fontSize * 0.36;
    ops += "1 1 1 rg BT /F2 " + fontSize.toFixed(2) + " Tf 1 0 0 1 " + tx.toFixed(2) + " " + ty.toFixed(2) + " Tm (PM) Tj ET\n0 0 0 rg\n";
    return ops;
  }
  // Voller Marken-Kopf: Logo + zweifarbige Wortmarke + Slogan + Trennlinie + Dokumenttitel +
  // Metazeile. Genutzt auf Seite 1 beider PDFs (Wochenplan hat nur eine Seite). Inhalt der
  // aufrufenden Funktion beginnt danach bei y=700.
  // Der Dokumenttitel steht bewusst auf 17pt statt der frueheren 24pt: Damals war er das
  // einzige grosse Element der Seite, jetzt fuehrt die Wortmarke darueber. Zwei konkurrierende
  // Ueberschriften in aehnlicher Groesse wuerden sich gegenseitig die Wirkung nehmen -
  // "Wochenplan"/"Einkaufsliste" ist hier die zweite Ebene, nicht die erste.
  function pdfBrandHeader(L, R, docTitle, metaLine, logo) {
    const cx = L + 17, cy = 798, wx = 100, wsize = 15;
    let cs = pdfMarkOps(cx, cy, 17, logo);
    const first = "PADDY’S ";
    cs += "BT\n0 0 0 rg /F2 " + wsize + " Tf 1 0 0 1 " + wx + " 804 Tm (" + pdfEsc(first) + ") Tj\n";
    cs += "0.863 0.149 0.149 rg 1 0 0 1 " + (wx + hbWidth(first, wsize)).toFixed(2) + " 804 Tm (" + pdfEsc("MEALPLAN") + ") Tj\n0 0 0 rg\nET\n";
    cs += "BT\n0.45 0.45 0.45 rg /F3 9.5 Tf 1 0 0 1 " + wx + " 790 Tm (" + pdfEsc("Plan it. Cook it. Lift it.") + ") Tj\n0 0 0 rg\nET\n";
    cs += "0.863 0.149 0.149 RG 1.5 w " + L + " 772 m " + R + " 772 l S\n";
    cs += "BT\n0 0 0 rg /F2 17 Tf 1 0 0 1 " + L + " 750 Tm (" + pdfEsc(docTitle) + ") Tj\n";
    cs += "0.4 0.4 0.4 rg /F1 11 Tf 1 0 0 1 " + L + " 734 Tm (" + pdfEsc(metaLine) + ") Tj\n0 0 0 rg\nET\n";
    return cs;
  }
  // Schlanker Kopf fuer Folgeseiten der Einkaufsliste: kleinere Logo-Marke (dasselbe
  // Bild-XObject, nur anders skaliert - keine zweite Einbettung), Titel + Seitenzahl,
  // duennere Trennlinie. Inhalt beginnt danach bei y=778.
  function pdfSlimHeader(L, R, pageNum, totalPages, logo) {
    let cs = pdfMarkOps(L + 11, 812, 11, logo);
    cs += "BT\n0 0 0 rg /F2 12 Tf 1 0 0 1 100 816 Tm (" + pdfEsc("Einkaufsliste") + ") Tj\n";
    cs += "0.5 0.5 0.5 rg /F1 9 Tf 1 0 0 1 100 802 Tm (" + pdfEsc("Seite " + pageNum + " von " + totalPages) + ") Tj\n0 0 0 rg\nET\n";
    cs += "0.863 0.149 0.149 RG 1 w " + L + " 792 m " + R + " 792 l S\n";
    return cs;
  }

  // ----- Echtes Logo-PNG fuer die PDFs vorbereiten (einmalig, async, gecacht) -----
  // Rohes PDF kennt nur RGB-Bilder + optionale Graustufen-/SMask fuer Transparenz, kein
  // natives RGBA. Das App-Logo (--logoL) ist ein 220x220 RGBA-PNG (per Analyse bestaetigt:
  // bitdepth 8, colortype 6, kein Interlacing). Pipeline: Base64 -> PNG-Chunks lesen ->
  // IDAT inflaten -> PNG-Filter pro Scanline rueckgaengig machen -> in RGB- und
  // Alpha-Puffer trennen -> beide einzeln wieder deflaten (klein, da grossflaechig einfarbig).
  // logoPdfAsset bleibt "undefined" bis zum ersten Versuch, "null" wenn PNG-Format/Browser
  // nicht passt (-> Vektor-Rueckfall in pdfMarkOps), sonst das fertige Objekt.
  let logoPdfAsset;
  function parsePngChunks(bytes) {
    const pos0 = 8;
    const chunks = [];
    let pos = pos0;
    while (pos < bytes.length) {
      const len = (bytes[pos] << 24 | bytes[pos + 1] << 16 | bytes[pos + 2] << 8 | bytes[pos + 3]) >>> 0;
      const type = String.fromCharCode(bytes[pos + 4], bytes[pos + 5], bytes[pos + 6], bytes[pos + 7]);
      chunks.push({ type: type, data: bytes.subarray(pos + 8, pos + 8 + len) });
      pos += 12 + len;
      if (type === "IEND") break;
    }
    return chunks;
  }
  function pngUnfilter(raw, width, height, bpp) {
    const stride = width * bpp;
    const out = new Uint8Array(height * stride);
    let rawPos = 0, outPos = 0;
    for (let y = 0; y < height; y++) {
      const filter = raw[rawPos++];
      for (let x = 0; x < stride; x++) {
        const a = x >= bpp ? out[outPos + x - bpp] : 0;
        const b = y > 0 ? out[outPos - stride + x] : 0;
        const c = (y > 0 && x >= bpp) ? out[outPos - stride + x - bpp] : 0;
        const v = raw[rawPos++];
        let recon;
        if (filter === 0) recon = v;
        else if (filter === 1) recon = v + a;
        else if (filter === 2) recon = v + b;
        else if (filter === 3) recon = v + ((a + b) >> 1);
        else { // Paeth
          const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c);
          recon = v + (pa <= pb && pa <= pc ? a : (pb <= pc ? b : c));
        }
        out[outPos + x] = recon & 0xff;
      }
      outPos += stride;
    }
    return out;
  }
  function bytesToBinaryString(bytes) {
    let s = "", CHUNK = 8000;
    for (let i = 0; i < bytes.length; i += CHUNK) s += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
    return s;
  }
  async function inflateBytes(bytes) {
    const ds = new DecompressionStream("deflate");
    const w = ds.writable.getWriter();
    w.write(bytes); w.close();
    return new Uint8Array(await new Response(ds.readable).arrayBuffer());
  }
  async function deflateToBinaryString(bytes) {
    const cs = new CompressionStream("deflate");
    const w = cs.writable.getWriter();
    w.write(bytes); w.close();
    const out = new Uint8Array(await new Response(cs.readable).arrayBuffer());
    return bytesToBinaryString(out);
  }
  async function prepareLogoForPdf() {
    if (logoPdfAsset !== undefined) return logoPdfAsset;
    try {
      if (!("CompressionStream" in window) || !("DecompressionStream" in window)) { logoPdfAsset = null; return null; }
      // Das Logo lag frueher als Base64 in --logoL und wurde von hier per getComputedStyle
      // gelesen. Seit es eine eigene Datei ist (img/logo.png, spart 60 KB render-blocking CSS),
      // kommen die Bytes direkt von dort. Der Service Worker haelt sie im Cache, offline ist
      // das also kein Netzzugriff. Schlaegt es doch fehl - etwa unter file:// - bleibt es beim
      // bestehenden Verhalten: logoPdfAsset = null und pdfMarkOps zeichnet die Vektor-Marke.
      const resp = await fetch("img/logo.png", { cache: "force-cache" });
      if (!resp.ok) { logoPdfAsset = null; return null; }
      const bytes = new Uint8Array(await resp.arrayBuffer());
      if (!(bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4E && bytes[3] === 0x47)) { logoPdfAsset = null; return null; }
      const chunks = parsePngChunks(bytes);
      const ihdr = chunks.find(c => c.type === "IHDR");
      if (!ihdr) { logoPdfAsset = null; return null; }
      const d = ihdr.data;
      const width = (d[0] << 24 | d[1] << 16 | d[2] << 8 | d[3]) >>> 0;
      const height = (d[4] << 24 | d[5] << 16 | d[6] << 8 | d[7]) >>> 0;
      const bitDepth = d[8], colorType = d[9], interlace = d[12];
      if (bitDepth !== 8 || colorType !== 6 || interlace !== 0) { logoPdfAsset = null; return null; }
      const idatChunks = chunks.filter(c => c.type === "IDAT");
      let idatLen = 0; idatChunks.forEach(c => idatLen += c.data.length);
      const idat = new Uint8Array(idatLen);
      let off = 0; idatChunks.forEach(c => { idat.set(c.data, off); off += c.data.length; });
      const rawScan = await inflateBytes(idat);
      const px = pngUnfilter(rawScan, width, height, 4);
      const n = width * height;
      const rgb = new Uint8Array(n * 3), alpha = new Uint8Array(n);
      for (let i = 0; i < n; i++) {
        rgb[i * 3] = px[i * 4]; rgb[i * 3 + 1] = px[i * 4 + 1]; rgb[i * 3 + 2] = px[i * 4 + 2];
        alpha[i] = px[i * 4 + 3];
      }
      const rgbStream = await deflateToBinaryString(rgb);
      const alphaStream = await deflateToBinaryString(alpha);
      logoPdfAsset = { w: width, h: height, rgbStream: rgbStream, rgbLen: rgbStream.length, alphaStream: alphaStream, alphaLen: alphaStream.length };
    } catch (e) { logoPdfAsset = null; }
    return logoPdfAsset;
  }

  // PDF-String -> Bytes. Ein JS-Zeichen ist hier genau ein Byte (siehe pdfEsc/Bild-Streams).
  function pdfBytes(pdf) {
    const bytes = new Uint8Array(pdf.length);
    for (let i = 0; i < pdf.length; i++) bytes[i] = pdf.charCodeAt(i) & 0xff;
    return bytes;
  }
  function saveBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }
  // logoPdfAsset ist ein Cache, den prepareLogoForPdf() fuellt und den
  // buildPrintable() im Kern liest. Als Wert in der Fassade waere es eine Kopie
  // vom Ladezeitpunkt - also immer null. Deshalb ein Zugriff statt eines Werts.
  function logoAsset() { return logoPdfAsset; }

  global.PM = global.PM || {};
  global.PM.pdf = {
    logoAsset: logoAsset,
    pdfBrandHeader: pdfBrandHeader,
    pdfBytes: pdfBytes,
    pdfEsc: pdfEsc,
    pdfSlimHeader: pdfSlimHeader,
    prepareLogoForPdf: prepareLogoForPdf,
    saveBlob: saveBlob,
    trunc: trunc,
  };
})(window);
