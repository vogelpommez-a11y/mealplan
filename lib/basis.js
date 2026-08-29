/* basis.js - Paddy's Mealplan
 *
 * Die beiden Helfer, die sowohl der App-Kern als auch die ausgelagerten Module
 * brauchen. Sie liegen hier, damit es sie genau EINMAL gibt - eine zweite Fassung
 * von esc() waere der Anfang genau des Problems, das die Aufteilung loesen soll.
 *
 * Die Fassade heisst window.PM und folgt dem Vorbild, das die Firebase-Bruecke seit
 * jeher benutzt (window.CloudAuth, CloudSync, ...).
 */
(function (global) {
  "use strict";

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c])); }

  function el(html) { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; }

  global.PM = global.PM || {};
  global.PM.esc = esc;
  global.PM.el = el;
})(window);
