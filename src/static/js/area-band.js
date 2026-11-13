/* The Hòa Xuân band (design-match design.md, "02 ở gần"): the area loop plays only while the
   band is on screen, and never when the visitor has asked for less motion.

   The page works without this file: the loop then plays on its own, as any muted loop. */
(function () {
  "use strict";

  var band = document.querySelector("#hoa-xuan .hoa-xuan__band");
  var video = band && band.querySelector("video");
  if (!video || !window.matchMedia || !("IntersectionObserver" in window)) {
    return;
  }

  var lessMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var onScreen = false;

  function update() {
    if (onScreen && !lessMotion.matches) {
      var playing = video.play();
      if (playing && playing.catch) {
        playing.catch(function () {}); // the poster stays
      }
    } else {
      video.pause();
    }
  }

  video.removeAttribute("autoplay");
  video.pause();

  new IntersectionObserver(function (entries) {
    onScreen = entries[entries.length - 1].isIntersecting;
    update();
  }).observe(band);

  if (lessMotion.addEventListener) {
    lessMotion.addEventListener("change", update);
  }
})();
