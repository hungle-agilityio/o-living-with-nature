/* The language switch keeps the visitor's place. The link is "/vi/" (or "/") as sent; this file
   adds the hash of the last chapter whose top is above the middle of the screen, on scroll and
   just before the link is used. Over the hero there is no hash. Nothing is stored or sent. */
(function () {
  "use strict";

  var IDS = ["house", "hoa-xuan", "rent", "faq", "contact"];
  var link = document.querySelector(".lang-switch a");
  if (!link) {
    return;
  }
  var base = link.getAttribute("href");

  function update() {
    var hash = "";
    IDS.forEach(function (id) {
      var chapter = document.getElementById(id);
      if (chapter && chapter.getBoundingClientRect().top < window.innerHeight / 2) {
        hash = "#" + id;
      }
    });
    link.setAttribute("href", base + hash);
  }

  window.addEventListener("scroll", update, { passive: true });
  ["pointerdown", "focus", "click"].forEach(function (name) {
    link.addEventListener(name, update);
  });
  update();
})();
