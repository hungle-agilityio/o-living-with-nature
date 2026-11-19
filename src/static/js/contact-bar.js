/* The phone contact bar (contact-one-place spec).

   The page works without this file: the bar then always shows on phones (contact.css). With it,
   the bar stays out of view until chapter 02 (Hòa Xuân) reaches the screen, stays shown from
   there down to the footer, and steps away while a field of the enquiry form has focus. */
(function () {
  "use strict";

  var bar = document.querySelector(".contact-bar");
  if (!bar) {
    return;
  }
  var chapter = document.getElementById("hoa-xuan");
  var form = document.querySelector("form.enquiry-form");
  var below = false;
  var typing = false;

  function update() {
    bar.classList.toggle("contact-bar--away", below || typing);
  }

  if (form) {
    form.addEventListener("focusin", function () {
      typing = true;
      update();
    });
    form.addEventListener("focusout", function () {
      // Wait one tick: focus moving between two fields is not leaving the form.
      setTimeout(function () {
        typing = form.contains(document.activeElement);
        update();
      }, 0);
    });
    // A page restored from the back-forward cache may keep focus in the form with no focusout.
    window.addEventListener("pageshow", function () {
      typing = form.contains(document.activeElement);
      update();
    });
  }

  // No observer: mark the page ready at once, so the bar shows as it does without the script.
  if (!window.IntersectionObserver) {
    document.documentElement.classList.add("contact-bar-ready");
    return;
  }
  // No chapter 02 on the page: nothing to wait for, the bar shows.
  if (!chapter) {
    document.documentElement.classList.add("contact-bar-ready");
    return;
  }
  // Away until the first check, so the bar never flashes in over the hero.
  bar.classList.add("contact-bar--away");

  // The root reaches far above the screen: chapter 02 counts as reached once its top is on the
  // screen, however far the visitor has scrolled past it, and a jump from the menu still calls back.
  new IntersectionObserver(function (entries) {
    // The top check also holds where rootMargin is ignored (a cross-origin frame).
    var entry = entries[entries.length - 1];
    below = !entry.isIntersecting && entry.boundingClientRect.top > 0;
    update();
    document.documentElement.classList.add("contact-bar-ready");
  }, { rootMargin: "100000px 0px 0px 0px" }).observe(chapter);
})();
