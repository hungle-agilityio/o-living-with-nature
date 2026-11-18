// The full-screen photo viewer of the home page (issue #156): a tap, a click, Enter or Space on a
// photo of the house, Hòa Xuân or rent chapter opens it on the photos of that chapter.
(function () {
  "use strict";
  var dialog = document.querySelector("dialog.viewer");
  if (!dialog) { return; }
  if (typeof dialog.showModal !== "function") { return; }

  var GROUPS = [".house__collage", ".hoa-xuan__photos", ".rent__photo"];
  var openLabel = dialog.getAttribute("data-open-label") || "";
  var track = dialog.querySelector(".viewer__track");
  var count = dialog.querySelector(".viewer__count");
  var steps = dialog.querySelectorAll(".viewer__step");
  var calm = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var slides = [], at = 0, opener = null, pushed = false, frame = 0, aim = -1;

  function build(photos) {
    track.innerHTML = "";
    slides = photos.map(function (img) {
      var figure = img.closest("figure");
      var chip = img.closest(".media__box").querySelector(".media__chip");
      var credit = figure && figure.querySelector(".media__credit");
      var slide = document.createElement("figure");
      var box = document.createElement("div");
      var big = document.createElement("img");
      slide.className = "viewer__slide";
      box.className = "viewer__frame";
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      box.appendChild(big);
      if (chip) { box.appendChild(chip.cloneNode(true)); }
      slide.appendChild(box);
      if (credit && credit.textContent.trim()) {
        var caption = document.createElement("figcaption");
        caption.className = "viewer__credit";
        caption.textContent = credit.textContent;
        slide.appendChild(caption);
      }
      track.appendChild(slide);
      return slide;
    });
    dialog.classList.toggle("viewer--single", slides.length < 2);
  }

  function mark() {
    count.textContent = (at + 1) + " / " + slides.length;
    steps[0].disabled = at === 0;
    steps[1].disabled = at === slides.length - 1;
    // A step button disabled under the focus would drop the focus out of the dialog.
    if (document.activeElement && document.activeElement.disabled) { dialog.querySelector(".viewer__close").focus(); }
  }

  function show(index, smooth) {
    at = Math.max(0, Math.min(slides.length - 1, index));
    mark();
    var left = at * track.clientWidth;
    if (smooth && !(calm && calm.matches) && track.scrollTo) {
      aim = at;
      track.scrollTo({ left: left, behavior: "smooth" });
    } else {
      track.scrollLeft = left;
    }
  }

  function open(photos, img) {
    opener = img.closest(".media__box");
    aim = -1;
    build(photos);
    dialog.showModal();
    show(photos.indexOf(img), false);
    try { history.pushState({ viewer: 1 }, ""); pushed = true; } catch (e) { pushed = false; }
  }

  function close() {
    if (dialog.open) { dialog.close(); }
  }

  // Esc is the dialog's own cancel, which then fires its "close" event like every other way out.
  dialog.addEventListener("close", function () {
    if (pushed && history.state && history.state.viewer) {
      try { history.back(); } catch (e) { /* the page stays as it is */ }
    }
    pushed = false;
    if (opener) { opener.focus(); }
  });
  // Back closes the viewer. A late popstate of our own history.back() that lands on a viewer
  // state (the viewer was opened again meanwhile) leaves it open.
  window.addEventListener("popstate", function () {
    if (history.state && history.state.viewer) { return; }
    pushed = false;
    close();
  });
  dialog.querySelector(".viewer__close").addEventListener("click", close);
  dialog.addEventListener("click", function (e) {
    var target = e.target;
    if (target === dialog || target === track || target.classList.contains("viewer__slide")) { close(); }
  });
  [].forEach.call(steps, function (button) {
    button.addEventListener("click", function () { show(at + Number(button.getAttribute("data-step")), true); });
  });
  dialog.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.repeat) { e.preventDefault(); }
    if (e.key === "ArrowRight") { e.preventDefault(); show(at + 1, true); }
    if (e.key === "ArrowLeft") { e.preventDefault(); show(at - 1, true); }
  });
  track.addEventListener("scroll", function () {
    if (frame) { return; }
    frame = requestAnimationFrame(function () {
      frame = 0;
      var k = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      // During a step's smooth scroll the count stays on its target until the track gets there.
      if (aim >= 0) { if (k === aim) { aim = -1; } return; }
      if (k !== at && slides[k]) { at = k; mark(); }
    });
  }, { passive: true });
  track.addEventListener("pointerdown", function () { aim = -1; }, { passive: true });

  GROUPS.forEach(function (selector) {
    var group = document.querySelector(selector);
    if (!group) { return; }
    var photos = [].slice.call(group.querySelectorAll(".media__box img"));
    photos.forEach(function (img) {
      var box = img.closest(".media__box");
      box.classList.add("photo-open");
      box.setAttribute("role", "button");
      box.setAttribute("tabindex", "0");
      box.setAttribute("aria-label", openLabel + img.alt);
      box.addEventListener("click", function () { open(photos, img); });
      // Enter opens on keydown; Space opens on keyup, so its keyup cannot press ✕ once open.
      box.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.repeat) { e.preventDefault(); open(photos, img); }
        if (e.key === " ") { e.preventDefault(); }
      });
      box.addEventListener("keyup", function (e) {
        if (e.key === " ") { e.preventDefault(); open(photos, img); }
      });
    });
  });
})();
