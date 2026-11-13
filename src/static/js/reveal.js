/* Load and reveal motion (design.md, "Load and reveal motion").

   The page works without this file: everything then shows at once. With JavaScript, an
   IntersectionObserver, and when the visitor has not asked for less motion, the class "motion"
   on <html> turns on the rules of motion.css: the header fades in, each element with the class
   "reveal" rises into place when 12% of it is on screen, and photos in media slots zoom slowly. */
(function () {
  "use strict";

  var STEP = 0.12; // siblings start this many seconds apart
  var MAX_STEPS = 5; // the delay stops growing after five steps

  if (!window.matchMedia || !("IntersectionObserver" in window)) {
    return;
  }
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  var root = document.documentElement;
  var blocks = [].slice.call(document.querySelectorAll(".reveal"));

  function onScreen(element) {
    var box = element.getBoundingClientRect();
    return box.top < window.innerHeight && box.bottom > 0;
  }

  // A block on screen when the page opens shows at once, without its rise.
  function showNow(element) {
    element.classList.add("is-revealed-now", "is-revealed");
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  blocks.forEach(function (element) {
    var index = 0;
    var sibling = element.previousElementSibling;
    while (sibling) {
      if (sibling.classList.contains("reveal")) {
        index += 1;
      }
      sibling = sibling.previousElementSibling;
    }
    element.style.transitionDelay = Math.min(index, MAX_STEPS) * STEP + "s";
  });

  root.classList.add("motion");

  blocks.forEach(function (element) {
    if (onScreen(element)) {
      showNow(element);
    } else {
      observer.observe(element);
    }
  });

  // The jump to a chapter (/#faq) may land after this script ran: what is on screen then shows
  // at once too.
  window.addEventListener(
    "load",
    function () {
      blocks.forEach(function (element) {
        if (!element.classList.contains("is-revealed") && onScreen(element)) {
          showNow(element);
          observer.unobserve(element);
        }
      });
    },
    { once: true }
  );
})();
