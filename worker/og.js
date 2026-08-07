// Cloudflare Worker: Meal-Vorschau in geteilten Links (?s=<id>) + Bild-Ausgabe unter /og/<id>.jpg
//
// Deployment ausschliesslich ueber das Cloudflare-Dashboard (Route www.paddysmealplan.de/*).
// Diese Datei liegt nur zur Nachvollziehbarkeit im Repo (siehe plans/TeilenVereinheitlichen.MD,
// Teil B) - GitHub Pages liefert sie wie jede andere Repo-Datei als statisches Asset mit aus
// (z. B. unter /worker/og.js), die App laedt oder fuehrt sie aber nie aus. Keine Secrets in
// dieser Datei, siehe unten.
//
// Secrets (Worker > Settings > Variables and Secrets):
//   GCP_SA_EMAIL         - E-Mail des Service-Accounts (Rolle: nur "Cloud Datastore Viewer")
//   GCP_SA_PRIVATE_KEY   - privater Schluessel des Service-Accounts, PEM/PKCS8, mit
//                          "-----BEGIN PRIVATE KEY-----"/"-----END PRIVATE KEY-----"
//
// firestore.rules bleibt unveraendert: "allow get: if request.auth != null" (Zeile 62).
// Der Worker authentifiziert sich ueber den Service-Account, nicht ueber die App - geteilte
// Meals werden dadurch NICHT allgemein oeffentlich lesbar in Firestore, nur Titel+Foto
// verlassen ueber diesen Worker gezielt das og-Feld.
//
// Jeder Fehler (Firestore nicht erreichbar, ID unbekannt, Token abgelaufen) faellt still auf
// die unveraenderte Antwort von GitHub Pages zurueck - der Worker darf die App nie blockieren.

const PROJECT_ID = "paddys-mealplan";
const ORIGIN = "https://www.paddysmealplan.de";
// Alphabet aus shareId() (index.html) - ohne l/o/0/1 (verwechselbar), 16 Zeichen.
const SHARE_ID_RE = /^[abcdefghijkmnpqrstuvwxyz23456789]{16}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      const imgMatch = url.pathname.match(/^\/og\/([a-z0-9]{16})\.jpg$/);
      if (imgMatch && SHARE_ID_RE.test(imgMatch[1])) return await handleOgImage(imgMatch[1], env);

      const shareId = url.searchParams.get("s");
      if (shareId && SHARE_ID_RE.test(shareId)) return await handleSharePreview(request, shareId, env);
    } catch (e) {
      // still zurueckfallen, siehe Kopf-Kommentar
    }
    return fetch(request);
  }
};

// ----- a) Normale Anfragen mit ?s=<id>: og:-Tags im HTML ersetzen -----
async function handleSharePreview(request, shareId, env) {
  const originRes = await fetch(request);
  const contentType = originRes.headers.get("content-type") || "";
  if (!originRes.ok || !contentType.includes("text/html")) return originRes;

  const doc = await getSharedDoc(shareId, env).catch(() => null);
  const og = doc && doc.og;
  if (!og || !og.t) return originRes; // kein Snapshot / kein og-Feld -> Seite bleibt unveraendert

  const title = String(og.t).slice(0, 200) + " – Paddy's Mealplan";
  const desc = "Ein Meal aus Paddy's Mealplan – Plan it. Cook it. Lift it.";
  const imgUrl = ORIGIN + "/og/" + shareId + ".jpg";
  const pageUrl = ORIGIN + "/?s=" + shareId;

  return new HTMLRewriter()
    .on('meta[property="og:title"]', { element(el) { el.setAttribute("content", title); } })
    .on('meta[property="og:description"]', { element(el) { el.setAttribute("content", desc); } })
    .on('meta[property="og:image"]', { element(el) { el.setAttribute("content", imgUrl); } })
    .on('meta[property="og:url"]', { element(el) { el.setAttribute("content", pageUrl); } })
    .on('meta[name="twitter:title"]', { element(el) { el.setAttribute("content", title); } })
    .on('meta[name="twitter:description"]', { element(el) { el.setAttribute("content", desc); } })
    .on('meta[name="twitter:image"]', { element(el) { el.setAttribute("content", imgUrl); } })
    .transform(originRes);
}

// ----- b) /og/<id>.jpg: Foto ausliefern -----
// og.img ist bewusst null, wenn das Meal ein eigenes Foto hat (siehe shareMealPayload() in
// index.html) - der Base64-String liegt dann schon in recipes[0].image, og.img wuerde ihn
// nur ein zweites Mal in denselben Payload einbetten. Fallback deshalb auf recipes[0].image.
async function handleOgImage(shareId, env) {
  const doc = await getSharedDoc(shareId, env).catch(() => null);
  let img = doc && doc.og && doc.og.img;
  if (!img && doc && Array.isArray(doc.recipes) && doc.recipes[0]) img = doc.recipes[0].image;

  if (typeof img === "string" && img.startsWith("data:")) {
    const m = img.match(/^data:([^;]+);base64,(.+)$/);
    if (m) {
      return new Response(base64ToBytes(m[2]), {
        headers: { "Content-Type": m[1], "Cache-Control": "public, max-age=86400" }
      });
    }
  }
  if (typeof img === "string" && img.startsWith("img/")) {
    const upstream = await fetch(ORIGIN + "/" + img);
    if (upstream.ok) {
      return new Response(upstream.body, {
        headers: { "Content-Type": upstream.headers.get("Content-Type") || "image/webp", "Cache-Control": "public, max-age=86400" }
      });
    }
  }
  // Fallback: dasselbe neutrale Foto, das photoFor() ohne Treffer auch clientseitig zeigt
  // (PHOTOS.neutral, index.html) - kein eigens erzeugtes Banner noetig.
  const fallback = await fetch(ORIGIN + "/img/neutral.jpg");
  return new Response(fallback.body, {
    headers: { "Content-Type": "image/jpeg", "Cache-Control": "public, max-age=86400" }
  });
}

function base64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

// ----- Firestore REST-Zugriff ueber einen Service-Account -----
// shared/{id} verlangt "allow get: if request.auth != null" - der Worker holt sich dafuer
// einen Google-OAuth2-Access-Token per JWT-Bearer-Flow (RFC 7523), signiert mit dem privaten
// Schluessel des Service-Accounts ueber WebCrypto (kein Node-"jsonwebtoken" im Worker noetig).
// Der Token wird pro Isolate zwischengespeichert, da ein Isolate viele Requests bedient und
// der Token ~1h gueltig ist.
let cachedToken = null; // { token, exp }

async function getSharedDoc(id, env) {
  const token = await getAccessToken(env);
  const res = await fetch(
    "https://firestore.googleapis.com/v1/projects/" + PROJECT_ID + "/databases/(default)/documents/shared/" + id,
    { headers: { Authorization: "Bearer " + token } }
  );
  if (!res.ok) return null;
  const data = await res.json();
  return firestoreFieldsToJson(data.fields || {});
}

async function getAccessToken(env) {
  const now = Math.floor(Date.now() / 1000);
  if (cachedToken && cachedToken.exp - 60 > now) return cachedToken.token;

  const header = { alg: "RS256", typ: "JWT" };
  const claim = {
    iss: env.GCP_SA_EMAIL,
    scope: "https://www.googleapis.com/auth/datastore.readonly",
    aud: "https://oauth2.googleapis.com/token",
    iat: now,
    exp: now + 3600
  };
  const jwt = await signJwt(header, claim, env.GCP_SA_PRIVATE_KEY);

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "grant_type=" + encodeURIComponent("urn:ietf:params:oauth:grant-type:jwt-bearer") + "&assertion=" + jwt
  });
  if (!res.ok) throw new Error("Token-Anfrage fehlgeschlagen: " + res.status);
  const json = await res.json();
  cachedToken = { token: json.access_token, exp: now + json.expires_in };
  return cachedToken.token;
}

function b64url(bytesOrObj) {
  const str = bytesOrObj instanceof Uint8Array
    ? String.fromCharCode(...bytesOrObj)
    : JSON.stringify(bytesOrObj);
  return btoa(str).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function signJwt(header, claim, pem) {
  const enc = new TextEncoder();
  const unsigned = b64url(header) + "." + b64url(claim);
  const key = await importPrivateKey(pem);
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key, enc.encode(unsigned));
  return unsigned + "." + b64url(new Uint8Array(sig));
}

async function importPrivateKey(pem) {
  const clean = pem.replace(/-----BEGIN PRIVATE KEY-----/, "").replace(/-----END PRIVATE KEY-----/, "").replace(/\s/g, "");
  const bytes = base64ToBytes(clean);
  return crypto.subtle.importKey("pkcs8", bytes, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
}

// Firestore liefert typisierte Werte ({stringValue:...}, {mapValue:{fields:{...}}}, ...) -
// og.t/og.img sind Strings, deshalb reicht eine schlanke, nicht vollstaendige Umwandlung.
function firestoreFieldsToJson(fields) {
  const out = {};
  for (const k in fields) out[k] = firestoreValueToJson(fields[k]);
  return out;
}
function firestoreValueToJson(v) {
  if (v.stringValue !== undefined) return v.stringValue;
  if (v.integerValue !== undefined) return Number(v.integerValue);
  if (v.doubleValue !== undefined) return v.doubleValue;
  if (v.booleanValue !== undefined) return v.booleanValue;
  if (v.mapValue !== undefined) return firestoreFieldsToJson(v.mapValue.fields || {});
  if (v.arrayValue !== undefined) return (v.arrayValue.values || []).map(firestoreValueToJson);
  return null;
}
