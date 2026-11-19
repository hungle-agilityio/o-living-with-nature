/* Walk through the house (#floor-plan, house-plan-2d T2): a room tapped on the plan opens alone,
   in the panel beside the drawing (a bottom sheet on a phone); ← → walk the rooms, Esc or ✕ closes.
   The page works without this file: the rooms then show as one list. */
(function () {
  "use strict";
  var plan = document.getElementById("floor-plan");
  var shut = plan && plan.querySelector(".plan__close");
  if (!plan || !shut) { return; }
  var rooms = [].slice.call(plan.querySelectorAll(".plan-room"));
  var links = [].slice.call(plan.querySelectorAll("a.plan__room"));
  var keys = rooms.map(function (r) { return r.getAttribute("data-room"); });
  var current = -1;
  if (!rooms.length) { return; }
  plan.classList.add("js");

  function sheet() { return window.matchMedia("(max-width: 860px)").matches; }
  function calm() { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; }
  // The room's link in the plan shown. open() ends the reveal motion, which would trap the sheet.
  function shown(key) {
    return links.filter(function (a) {
      return a.getAttribute("data-room") === key && a.getClientRects().length !== 0;
    })[0];
  }

  function open(n, focus, still) {
    current = (n + rooms.length) % rooms.length;
    var key = keys[current];
    rooms.forEach(function (r, k) { r.classList.toggle("is-on", k === current); });
    links.forEach(function (a) {
      var on = a.getAttribute("data-room") === key;
      a.classList.toggle("is-on", on);
      if (on) { a.setAttribute("aria-current", "true"); } else { a.removeAttribute("aria-current"); }
    });
    plan.classList.add("is-open", "is-revealed", "is-revealed-now");
    if (focus) { rooms[current].focus({ preventScroll: true }); }
    if (!still && sheet()) {
      var a = shown(key);
      var r = a && a.getBoundingClientRect();
      if (r) { window.scrollBy({ top: r.top - 84, behavior: calm() ? "auto" : "smooth" }); }
    }
  }

  function close() {
    if (current < 0) { return; }
    var a = shown(keys[current]);
    current = -1;
    plan.classList.remove("is-open", "is-instant");
    rooms.forEach(function (r) { r.classList.remove("is-on"); });
    links.forEach(function (l) { l.classList.remove("is-on"); l.removeAttribute("aria-current"); });
    if (a) { a.focus(); }
  }

  function pick(a) {
    var n = keys.indexOf(a.getAttribute("data-room"));
    if (n > -1) { open(n, !sheet()); }
  }

  links.forEach(function (a) {
    a.addEventListener("click", function (e) {
      // A modifier key or another button keeps the link's own behaviour.
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) { return; }
      e.preventDefault();
      pick(a);
    });
    // An SVG link has no click(): Space opens the room as a click does.
    a.addEventListener("keydown", function (e) {
      if (e.key === " ") { e.preventDefault(); pick(a); }
    });
  });
  [].forEach.call(plan.querySelectorAll(".plan__step"), function (b) {
    b.addEventListener("click", function () {
      open((current < 0 ? -1 : current) + Number(b.getAttribute("data-step")), true);
    });
  });
  shut.addEventListener("click", close);

  // Keys stay with a form field or with an open dialog (the photo viewer uses the same keys).
  document.addEventListener("keydown", function (e) {
    var t = e.target;
    if (current < 0 || document.querySelector("dialog[open]")) { return; }
    if (t && (t.isContentEditable || (t.closest && t.closest("input, textarea, select")))) { return; }
    if (e.key === "Escape") { close(); }
    else if (e.key === "ArrowRight") { open(current + 1, true); }
    else if (e.key === "ArrowLeft") { open(current - 1, true); }
  });

  // An address ending in #room-<key> opens that room at once: no focus, no scroll, no motion.
  var at = location.hash.indexOf("#room-") === 0 ? keys.indexOf(location.hash.slice(6)) : -1;
  if (at > -1) {
    plan.classList.add("is-instant");
    open(at, false, true);
  }
})();
