/* Home hero "Through the Ở": the intro that plays by itself (design-match design.md, "Hero").
   Without this file the still hero shows under a solid header. With hero files and motion, the
   class "hero-flight" makes the hero one screen; a canvas draws the loop through the letter,
   which grows on time until the loop fills the screen, then the heading rises line by line.
   Any input jumps to the end. Nothing is stored. */
(function () {
  "use strict";

  var MAX_SCALE = 70; // the letter grows up to about 70 times
  var GROW_START = 0.6; // seconds: the letter rests until here
  var GROW_END = 5.6; // the loop fills the screen here
  var INTRO_END = 7.0; // the shade and the heading are in by here
  var LINE_DELAY = 0.15; // each heading line starts this long after the one before
  var LINE_TIME = 1.0; // how long one line takes to rise
  var CUE_START = 6.9; // the cue fades in from here, in half a second
  var FOOT_END = 1 / 6; // the dictionary line is gone after the first sixth of the growth
  var SAND = "#e9e2d3";
  var OUTLINE = "rgba(233, 226, 211, "; // Paper: the outline of the letter at night
  var LETTER = "Ở";
  var FONT = '500 SIZEpx "Cormorant Garamond", Georgia, serif';

  var hero = document.getElementById("hero");
  var frame = hero && hero.querySelector(".hero__frame");
  var canvas = hero && hero.querySelector(".hero__canvas");
  var video = hero && hero.querySelector(".hero__video");
  var ctx = canvas && canvas.getContext && canvas.getContext("2d");
  // No hero files: the still hero stays.
  if (!frame || !video || !ctx || !window.requestAnimationFrame || !window.matchMedia) {
    return;
  }

  var root = document.documentElement;
  var header = document.querySelector(".site-header");
  var heading = hero.querySelector("h1");
  var lessMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var poster = null;
  var request = 0;
  var begun = 0; // the time the intro started
  var skipped = false;
  var lines = [];
  var shown = {};
  // Set by measure(): the frame, the letter at rest, and the point the letter grows around.
  var ratio, width, height, size, originX, originY, anchorX, anchorY, maxScale;

  if (video.poster) {
    poster = new Image();
    poster.src = video.poster;
  }

  function clamp(value) {
    return Math.min(1, Math.max(0, value));
  }

  /* The sine ease-in-out: with the size maxScale to this power, the zoom is even. */
  function easeInOut(t) {
    return -(Math.cos(Math.PI * t) - 1) / 2;
  }

  function font(pixels) {
    return FONT.replace("SIZE", String(pixels));
  }

  function now() {
    return window.performance && performance.now ? performance.now() : Date.now();
  }

  /* The left side of the bowl of the letter, where its stroke is thickest: [centre, width] in
     ems from the start of the letter, found on a small drawing so that any font works. */
  function stroke() {
    var probe = document.createElement("canvas");
    var pen = probe.getContext("2d");
    var em = 200;
    probe.width = 2 * em;
    probe.height = 2 * em;
    pen.font = font(em);
    var row = Math.round(1.5 * em - pen.measureText("O").actualBoundingBoxAscent / 2);
    pen.fillText(LETTER, em / 2, 1.5 * em);
    var alpha = pen.getImageData(0, row, probe.width, 1).data;
    var start = -1;
    for (var x = 0; x < probe.width; x += 1) {
      var inked = alpha[4 * x + 3] > 127;
      if (inked && start < 0) {
        start = x;
      } else if (!inked && start >= 0) {
        return [((start + x) / 2 - em / 2) / em, (x - start) / em];
      }
    }
    return null;
  }

  function measure() {
    ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = frame.clientWidth;
    height = frame.clientHeight;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    // The hero letter of the type scale: 70% of the screen height, at most 105% of its width.
    size = Math.min(0.7 * height, 1.05 * width);
    ctx.font = font(size);
    var box = ctx.measureText(LETTER);
    var bowl = ctx.measureText("O").actualBoundingBoxAscent;
    originX = width / 2 - (box.actualBoundingBoxRight - box.actualBoundingBoxLeft) / 2;
    originY = 0.47 * height + (box.actualBoundingBoxAscent - box.actualBoundingBoxDescent) / 2;
    anchorY = originY - bowl / 2;
    var side = stroke();
    anchorX = side ? originX + side[0] * size : width / 2;
    // On a very wide screen 70 times may not be enough for the stroke to cover it.
    maxScale = side ? Math.max(MAX_SCALE, (1.15 * width) / (side[1] * size)) : MAX_SCALE;
    shown = {};
  }

  /* The loop when it can play, else the poster photo, else Sand: covering the whole frame. */
  function paint() {
    var source = null;
    var w = 0;
    var h = 0;
    if (video.readyState >= 2 && video.videoWidth) {
      source = video;
      w = video.videoWidth;
      h = video.videoHeight;
    } else if (poster && poster.complete && poster.naturalWidth) {
      source = poster;
      w = poster.naturalWidth;
      h = poster.naturalHeight;
    }
    if (source) {
      var fit = Math.max(width / w, height / h);
      try {
        ctx.drawImage(source, (width - w * fit) / 2, (height - h * fit) / 2, w * fit, h * fit);
        return;
      } catch (error) {
        // A file the browser cannot draw: the Sand below.
      }
    }
    ctx.fillStyle = SAND;
    ctx.fillRect(0, 0, width, height);
  }

  /* e: the eased time of the growth; time: its plain time; night: the theme of this frame. */
  function draw(e, time, night) {
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.globalCompositeOperation = "source-over";
    ctx.clearRect(0, 0, width, height);
    paint();
    if (e >= 0.999) {
      return; // the loop fills the screen
    }
    // Keep the picture only inside the letter, grown around the anchor, which moves to the
    // centre of the screen by the same e; the size is multiplied by the same ratio every moment.
    var scale = Math.pow(maxScale, e);
    ctx.globalCompositeOperation = "destination-in";
    ctx.translate(anchorX + (width / 2 - anchorX) * e, anchorY + (height / 2 - anchorY) * e);
    ctx.scale(scale, scale);
    ctx.translate(-anchorX, -anchorY);
    ctx.font = font(size);
    ctx.fillText(LETTER, originX, originY);
    // At night a Paper outline keeps the dark top of the letter visible; 1.5px wide on screen,
    // it fades out over the first fifth of the growth.
    var alpha = 0.55 * clamp(1 - time / 0.2);
    if (night && alpha > 0) {
      ctx.globalCompositeOperation = "source-over";
      ctx.strokeStyle = OUTLINE + alpha.toFixed(3) + ")";
      ctx.lineWidth = 1.5 / scale;
      ctx.strokeText(LETTER, originX, originY);
    }
  }

  /* Write a value to the page only when it changed. */
  function show(name, value, write) {
    if (shown[name] !== value) {
      shown[name] = value;
      write(value);
    }
  }

  /* Two lines that rise, "Living" and "with nature"; the words stay as written. */
  function split() {
    if (!heading || lines.length) {
      return;
    }
    var first = document.createElement("span");
    var second = document.createElement("span");
    first.className = second.className = "hero__ln";
    first.appendChild(document.createElement("span"));
    second.appendChild(document.createElement("span"));
    var em = heading.querySelector("em");
    while (heading.firstChild && heading.firstChild !== em) {
      first.firstChild.appendChild(heading.firstChild);
    }
    while (heading.firstChild) {
      second.firstChild.appendChild(heading.firstChild);
    }
    heading.appendChild(first);
    heading.appendChild(second);
    lines = [first.firstChild, second.firstChild];
  }

  function tick() {
    request = window.requestAnimationFrame(tick);
    var seconds = skipped ? INTRO_END + 1 : (now() - begun) / 1000;
    if (seconds >= INTRO_END + 1) {
      skipped = true; // the intro is over; input no longer matters
    }
    var time = clamp((seconds - GROW_START) / (GROW_END - GROW_START));
    var e = easeInOut(time);
    var night = document.body.getAttribute("data-daypart") === "night";
    var box = hero.getBoundingClientRect();
    var onScreen = box.bottom > 0 && box.top < window.innerHeight;
    var past = !header || box.bottom < header.offsetHeight;

    show("foot", clamp(1 - time / FOOT_END).toFixed(3), function (value) {
      hero.style.setProperty("--hero-foot", value);
    });
    show("title", clamp((seconds - GROW_END) / (INTRO_END - GROW_END)).toFixed(3), function (value) {
      hero.style.setProperty("--hero-title", value);
    });
    show("cue", clamp((seconds - CUE_START) / 0.5).toFixed(3), function (value) {
      hero.style.setProperty("--hero-cue", value);
    });
    lines.forEach(function (line, index) {
      var rise = clamp((seconds - GROW_END - LINE_DELAY * index) / LINE_TIME);
      rise = 1 - Math.pow(1 - rise, 3);
      show("line" + index, rise.toFixed(3), function () {
        line.style.transform = rise < 1 ? "translateY(" + (105 * (1 - rise)).toFixed(1) + "%)" : "";
        line.style.opacity = rise < 1 ? rise.toFixed(3) : "";
      });
    });
    // Over the hero the header is clear, and its text turns Paper once the loop covers it;
    // once the hero has left the screen it is the solid bar again.
    show("past", past, function (value) {
      root.classList.toggle("hero-past", value);
    });
    show("over", !past && e > 0.75, function (value) {
      root.classList.toggle("hero-over", value);
    });
    show("playing", onScreen, function (value) {
      if (value) {
        var playing = video.play();
        if (playing && playing.catch) {
          playing.catch(function () {}); // the poster stays in the letter
        }
      } else {
        video.pause();
      }
    });
    if (onScreen) {
      draw(e, time, night);
    }
  }

  /* Any input during the intro jumps to its end; nothing is ever prevented. */
  function skip() {
    skipped = true;
  }

  function start() {
    if (request) {
      return;
    }
    root.classList.add("hero-flight");
    split();
    measure();
    // Opened lower down or at a chapter address: the end state at once, and the chapter kept
    // in view now that the hero is one screen high.
    var target = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
    skipped = window.pageYOffset > 40 || !!target;
    if (target && target.scrollIntoView) {
      target.scrollIntoView();
    }
    begun = now();
    tick();
  }

  function stop() {
    window.cancelAnimationFrame(request);
    request = 0;
    root.classList.remove("hero-flight", "hero-over", "hero-past");
    ["--hero-foot", "--hero-title", "--hero-cue"].forEach(function (name) {
      hero.style.removeProperty(name);
    });
    lines.forEach(function (line) {
      line.style.transform = "";
      line.style.opacity = "";
    });
    shown = {};
    video.pause();
  }

  function choose() {
    if (lessMotion.matches) {
      stop();
    } else {
      start();
    }
  }

  ["wheel", "touchstart", "keydown", "pointerdown", "scroll"].forEach(function (name) {
    window.addEventListener(name, skip, { passive: true });
  });
  window.addEventListener("resize", function () {
    // A phone's toolbar sliding away also fires this; measure only when the frame changed.
    if (request && (frame.clientWidth !== width || frame.clientHeight !== height)) {
      measure();
    }
  });
  if (lessMotion.addEventListener) {
    lessMotion.addEventListener("change", choose);
  }
  // The letter is drawn in the fallback font until Cormorant Garamond has loaded.
  if (document.fonts && document.fonts.load) {
    document.fonts.load(font(64), LETTER + "O").then(
      function () {
        if (request) {
          measure();
        }
      },
      function () {} // the fallback font stays
    );
  }
  choose();
})();
