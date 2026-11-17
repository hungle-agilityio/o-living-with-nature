(function () {
  /* Chapter 01 phone carousel (mobile-smoothness): the pager under the room row, "n / 5" and
     one dot per card. The CSS hides it on a desktop. Without this file the row still snaps. */
  "use strict";

  var list = document.querySelector("ul.house__collage");
  if (!list) {
    return;
  }

  var cards = Array.prototype.filter.call(list.children, function (child) {
    return child.tagName === "LI";
  });
  var total = cards.length;
  if (!total) {
    return;
  }

  var word = document.documentElement.lang === "vi" ? "Ảnh " : "Photo ";
  var lessMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");

  var pager = document.createElement("div");
  pager.className = "house__pager";
  var count = document.createElement("p");
  count.className = "house__count label muted";
  count.setAttribute("aria-live", "polite");
  var dots = document.createElement("ul");
  dots.className = "house__dots";

  var buttons = cards.map(function (card, index) {
    var item = document.createElement("li");
    var button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-label", word + (index + 1));
    button.addEventListener("click", function () {
      list.scrollTo({
        left: offset(card),
        behavior: lessMotion && lessMotion.matches ? "auto" : "smooth",
      });
    });
    item.appendChild(button);
    dots.appendChild(item);
    return button;
  });

  pager.appendChild(count);
  pager.appendChild(dots);
  list.parentNode.insertBefore(pager, list.nextSibling);

  // The scroll that centres the card.
  function offset(card) {
    var box = list.getBoundingClientRect();
    var rect = card.getBoundingClientRect();
    return list.scrollLeft + rect.left - box.left - (box.width - rect.width) / 2;
  }

  var shown = -1;

  function show(index) {
    if (index === shown) {
      return;
    }
    shown = index;
    count.textContent = index + 1 + " / " + total;
    buttons.forEach(function (button, at) {
      button.setAttribute("aria-current", at === index ? "true" : "false");
    });
  }

  function nearest() {
    var box = list.getBoundingClientRect();
    var middle = box.left + box.width / 2;
    var best = 0;
    var bestDistance = Infinity;
    cards.forEach(function (card, index) {
      var rect = card.getBoundingClientRect();
      var distance = Math.abs(rect.left + rect.width / 2 - middle);
      if (distance < bestDistance) {
        bestDistance = distance;
        best = index;
      }
    });
    return best;
  }

  var waiting = false;

  list.addEventListener(
    "scroll",
    function () {
      if (waiting) {
        return;
      }
      waiting = true;
      window.requestAnimationFrame(function () {
        waiting = false;
        show(nearest());
      });
    },
    { passive: true }
  );

  show(0);
})();
