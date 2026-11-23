/* Click or tap a screenshot to open it larger; tap it again for 100%. Esc, backdrop or the button closes.
   Article charts (.art .fig svg) open the same way: a larger copy you can scroll, with a "tap to zoom" hint on each chart. */
(function () {
  var SEL = ".shot2 img,.shot img,.pbf img,.pside img,.guide-shot img,.mac img";
  var ov, im, full = false;
  function build() {
    ov = document.createElement("div"); ov.className = "zm"; ov.hidden = true;
    ov.setAttribute("role", "dialog"); ov.setAttribute("aria-modal", "true");
    im = document.createElement("img");
    var b = document.createElement("button"); b.type = "button"; b.className = "zx"; b.setAttribute("aria-label", "Close"); b.textContent = "×";
    ov.appendChild(im); ov.appendChild(b); document.body.appendChild(ov);
    ov.addEventListener("click", function (e) { if (e.target === im) { full = !full; ov.classList.toggle("full", full); } else close(); });
  }
  function open(src, alt) {
    if (!ov) build();
    full = false; ov.classList.remove("full"); im.src = src; im.alt = alt || "";
    ov.hidden = false; document.documentElement.classList.add("zm-on");
  }
  function close() { if (ov) { ov.hidden = true; im.removeAttribute("src"); document.documentElement.classList.remove("zm-on"); } }
  document.addEventListener("click", function (e) {
    var t = e.target; if (!t.matches || !t.matches(SEL)) return;
    var a = t.closest("a"); if (a) e.preventDefault();
    open(t.currentSrc || t.src, t.alt);
  });

  /* ---- charts ---- */
  var ES = (document.documentElement.lang || "").slice(0, 2) === "es";
  var HINT = ES ? "Toca para ampliar" : "Tap to zoom", HINT_ARIA = ES ? "Ampliar el gráfico" : "Zoom the chart";
  function openChart(svg) {
    if (!ov) build();
    full = false; ov.classList.remove("full"); ov.classList.add("chart"); im.removeAttribute("src");
    var old = ov.querySelector(".zchart"); if (old) old.remove();
    var wrap = document.createElement("div"); wrap.className = "art zchart";
    var c = svg.cloneNode(true); c.removeAttribute("width"); c.removeAttribute("height");
    var vb = svg.viewBox && svg.viewBox.baseVal, vw = window.innerWidth;
    var w = vb && vb.width ? (vw < 800 ? Math.max(vb.width * 1.5, 760) : Math.min(vb.width * 1.7, vw - 80)) : 900;
    c.style.width = Math.round(w) + "px"; c.style.maxWidth = "none"; c.style.minWidth = "0";
    wrap.appendChild(c); ov.insertBefore(wrap, im);
    ov.hidden = false; document.documentElement.classList.add("zm-on");
  }
  var _close = close;
  close = function () { if (ov) { ov.classList.remove("chart"); var z = ov.querySelector(".zchart"); if (z) z.remove(); } _close(); };
  document.addEventListener("click", function (e) {
    var t = e.target; if (!t.closest) return;
    var hint = t.closest(".zhint"), svg = hint ? hint.parentNode.querySelector("svg:not(.zi)") : (t.closest(".art .fig svg:not(.zi)"));
    if (svg && !t.closest(".zm")) { e.preventDefault(); openChart(svg); }
  });
  document.querySelectorAll(".art .fig").forEach(function (f) {
    var svg = f.querySelector("svg"); if (!svg) return;
    var b = document.createElement("button"); b.type = "button"; b.className = "zhint"; b.setAttribute("aria-label", HINT_ARIA);
    b.innerHTML = '<svg class="zi" viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><circle cx="6.5" cy="6.5" r="4.5"/><path d="M10 10l4 4M6.5 4.5v4M4.5 6.5h4"/></svg><span>' + HINT + "</span>";
    f.insertBefore(b, f.firstChild);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  var s = document.createElement("style");
  s.textContent = SEL.split(",").join("{cursor:zoom-in}") + "{cursor:zoom-in}.art .fig svg{cursor:zoom-in}";
  document.head.appendChild(s);
})();
