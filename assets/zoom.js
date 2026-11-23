/* Click or tap a screenshot to open it larger; tap it again for 100%. Esc, backdrop or the button closes. */
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
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
  var s = document.createElement("style");
  s.textContent = SEL.split(",").join("{cursor:zoom-in}") + "{cursor:zoom-in}";
  document.head.appendChild(s);
})();
