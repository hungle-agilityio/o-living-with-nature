/* The phone contact bar (one-page spec AC12).

   The page works without this file: the bar then always shows on phones (contact.css). With it,
   the bar hides while the hero or the contact chapter is on screen, so it shows only once the
   hero has scrolled away and goes again over the contact chapter, which has the same buttons. */
(function () {
  "use strict";

  var bar = document.querySelector(".contact-bar");
  var hero = document.getElementById("hero");
  var contact = document.getElementById("contact");
  if (!bar || !window.IntersectionObserver) {
    return;
  }

  // Hidden until the first look at the screen, so it does not flash in over the hero.
  var onScreen = { hero: !!hero, contact: false };
  update();

  function update() {
    bar.classList.toggle("contact-bar--away", onScreen.hero || onScreen.contact);
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      onScreen[entry.target === hero ? "hero" : "contact"] = entry.isIntersecting;
    });
    update();
  });
  if (hero) {
    observer.observe(hero);
  }
  if (contact) {
    observer.observe(contact);
  }
})();
