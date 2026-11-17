/* The phone contact bar (one-page spec AC12).

   The page works without this file: the bar then always shows on phones (contact.css). With it,
   the bar stays out of view until the first check of the screen, and hides while the hero, the
   contact chapter or any other set of contact buttons is on screen. Without JavaScript it always
   shows. */
(function () {
  "use strict";

  var bar = document.querySelector(".contact-bar");
  if (!bar) {
    return;
  }
  // No observer: mark the page ready at once, so the bar shows as it does without the script.
  if (!window.IntersectionObserver) {
    document.documentElement.classList.add("contact-bar-ready");
    return;
  }
  // Away until the first check, so the bar never flashes in over the hero.
  bar.classList.add("contact-bar--away");

  var watched = [];
  var hero = document.getElementById("hero");
  var contact = document.getElementById("contact");
  if (hero) {
    watched.push(hero);
  }
  if (contact) {
    watched.push(contact);
  }
  Array.prototype.forEach.call(document.querySelectorAll(".contact-buttons"), function (el) {
    if (!bar.contains(el)) {
      watched.push(el);
    }
  });

  // Nothing to wait for: no callback would ever fire, so show the bar.
  if (watched.length === 0) {
    document.documentElement.classList.add("contact-bar-ready");
    bar.classList.remove("contact-bar--away");
    return;
  }

  var onScreen = new Map();
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      onScreen.set(entry.target, entry.isIntersecting);
    });
    var any = false;
    onScreen.forEach(function (visible) {
      if (visible) {
        any = true;
      }
    });
    bar.classList.toggle("contact-bar--away", any);
    // The first callback reports every watched element (all observed at once): the bar may show.
    document.documentElement.classList.add("contact-bar-ready");
  });
  watched.forEach(function (el) {
    observer.observe(el);
  });
})();
