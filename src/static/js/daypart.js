/* The time of day while the page is open (time-of-day-live, "Live theme").
   The server sends its time with the page (data-now on the header line). This file keeps the
   time in Đà Nẵng (UTC+7, no daylight saving) as that time plus the time since load, so a wrong
   device clock has no effect. On every minute it moves the header clock (the long line and
   the short phone line, .site-header__short); at 05:00, 08:00, 17:00
   and 19:00 it sets body[data-daypart] and tells the page with the event "daypart", unless the
   page is a preview (data-preview), which keeps its theme. Nothing is stored or sent. */
(function () {
  "use strict";

  // The hour each theme starts at, as theme_for in pages/daypart.py; before 05:00 it is night.
  var STARTS = [[5, "dawn"], [8, "day"], [17, "dusk"], [19, "night"]];
  var OFFSET = 7 * 3600e3; // Đà Nẵng is UTC+7 all year

  var line = document.querySelector(".site-header__time");
  var short = document.querySelector(".site-header__short"); // "14:52 · Day", on phones
  var sent = line && Number(line.getAttribute("data-now"));
  if (!sent || !document.body || !window.CustomEvent) {
    return; // without the time the page keeps what the server chose
  }
  var preview = line.hasAttribute("data-preview");
  var shift = sent - Date.now(); // the server's time minus the device's, at load
  var timer = 0;
  var labels = {}; // the theme names in the page language, from data-labels (JSON)
  try {
    labels = JSON.parse(line.getAttribute("data-labels") || "{}");
  } catch (error) {
    labels = {}; // the capitalised theme name stands in
  }

  function two(value) {
    return (value < 10 ? "0" : "") + value;
  }

  function themeAt(hour) {
    var theme = "night";
    STARTS.forEach(function (start) {
      if (hour >= start[0]) {
        theme = start[1];
      }
    });
    return theme;
  }

  function update() {
    var now = Date.now() + shift;
    var here = new Date(now + OFFSET);
    var body = document.body;
    var theme = body.getAttribute("data-daypart");
    if (!preview) {
      var real = themeAt(here.getUTCHours());
      if (real !== theme) {
        theme = real;
        body.setAttribute("data-daypart", theme);
        document.dispatchEvent(new CustomEvent("daypart", { detail: { theme: theme } }));
      }
    }
    var clock = two(here.getUTCHours()) + ":" + two(here.getUTCMinutes());
    var label = labels[theme] || (theme ? theme.charAt(0).toUpperCase() + theme.slice(1) : "");
    // Only the clock and the label change; the words in between stay as the server wrote them.
    var text = line.textContent
      .replace(/\d\d:\d\d/, clock)
      .replace(/· [^·]+$/, "· " + label);
    if (text !== line.textContent) {
      line.textContent = text;
    }
    var brief = clock + " · " + label;
    if (short && short.textContent !== brief) {
      short.textContent = brief;
    }
    // Wake just after the next minute starts.
    window.clearTimeout(timer);
    timer = window.setTimeout(update, 60000 - (now % 60000) + 250);
  }

  function again() {
    if (!document.hidden) {
      update(); // back from a hidden tab or the back-forward cache: catch up at once
    }
  }

  document.addEventListener("visibilitychange", again);
  window.addEventListener("pageshow", again);
  // After every deferred script has run, so hero.js already listens for "daypart".
  document.addEventListener("DOMContentLoaded", update);
})();
