/* Home hero "Through the Ở": the flight through the letter (design.md, Components).

   The page works without this file: it then shows the still hero. With JavaScript, and when the
   visitor has not asked for less motion, the class "hero-flight" on <html> turns the hero into
   a tall stage. A canvas draws the loop (the poster photo until the video can play) through the
   shape of the letter, and scrolling grows the letter until the loop fills the screen. */
(function () {
  "use strict";

  var MAX_SCALE = 70; // the letter grows up to about 70 times
  var POWER = 2.4; // scale rises with scroll progress to this power
  var FOOT_END = 1 / 6; // the dictionary line is gone after the first sixth
  var TITLE_START = 0.8; // the heading rises in the last fifth
  var SAND = "#e9e2d3";
  var LETTER = "Ở";
  var FONT = '500 SIZEpx "Cormorant Garamond", Georgia, serif';

  var hero = document.getElementById("hero");
  var frame = hero && hero.querySelector(".hero__frame");
  var canvas = hero && hero.querySelector(".hero__canvas");
  var ctx = canvas && canvas.getContext && canvas.getContext("2d");
  if (!frame || !ctx || !window.requestAnimationFrame || !window.matchMedia) {
    return;
  }

  var root = document.documentElement;
  var header = document.querySelector(".site-header");
  var video = hero.querySelector(".hero__video");
  var lessMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var poster = null;
  var request = 0;
  var shown = {};
  // Set by measure(): the frame, the letter at rest, and the point the flight goes through.
  var ratio, width, height, size, originX, originY, anchorX, anchorY, maxScale;

  if (video && video.poster) {
    poster = new Image();
    poster.src = video.poster;
  }

  function clamp(value) {
    return Math.min(1, Math.max(0, value));
  }

  function font(pixels) {
    return FONT.replace("SIZE", String(pixels));
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
    var side = stroke();
    maxScale = MAX_SCALE;
    if (side) {
      anchorX = originX + side[0] * size;
      anchorY = originY - bowl / 2;
      // On a very wide screen 70 times is not enough for the stroke to cover it in time.
      var needed = (1.15 * width) / (side[1] * size);
      maxScale = Math.max(MAX_SCALE, 1 + (needed - 1) / Math.pow(TITLE_START, POWER));
    } else {
      anchorX = width / 2;
      anchorY = originY - bowl / 2;
    }
    shown = {};
  }

  /* The loop when it can play, else the poster photo, else Sand: covering the whole frame. */
  function paint() {
    var source = null;
    var w = 0;
    var h = 0;
    if (video && video.readyState >= 2 && video.videoWidth) {
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
        // A file the browser cannot draw: the Sand letter below.
      }
    }
    ctx.fillStyle = SAND;
    ctx.fillRect(0, 0, width, height);
  }

  function draw(progress) {
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.globalCompositeOperation = "source-over";
    ctx.clearRect(0, 0, width, height);
    paint();
    if (progress >= TITLE_START) {
      return; // the loop fills the screen
    }
    // Keep the picture only inside the letter, grown around the anchor, which moves to the
    // centre of the screen.
    var scale = 1 + (maxScale - 1) * Math.pow(progress, POWER);
    var move = 1 - Math.pow(1 - progress, 3);
    ctx.globalCompositeOperation = "destination-in";
    ctx.translate(anchorX + (width / 2 - anchorX) * move, anchorY + (height / 2 - anchorY) * move);
    ctx.scale(scale, scale);
    ctx.translate(-anchorX, -anchorY);
    ctx.font = font(size);
    ctx.fillText(LETTER, originX, originY);
  }

  /* Write a value to the page only when it changed. */
  function show(name, value, write) {
    if (shown[name] !== value) {
      shown[name] = value;
      write(value);
    }
  }

  function tick() {
    request = window.requestAnimationFrame(tick);
    var box = hero.getBoundingClientRect();
    var travel = box.height - height;
    var progress = travel > 0 ? clamp(-box.top / travel) : 0;
    var onScreen = box.bottom > 0 && box.top < height;

    show("foot", clamp(1 - progress / FOOT_END).toFixed(3), function (value) {
      hero.style.setProperty("--hero-foot", value);
    });
    show("title", clamp((progress - TITLE_START) / (1 - TITLE_START)).toFixed(3), function (value) {
      hero.style.setProperty("--hero-title", value);
    });
    // The header row turns Paper once the loop covers most of the screen.
    var scale = 1 + (maxScale - 1) * Math.pow(progress, POWER);
    // With no loop the screen fills with Sand, where Paper could not be read: the row keeps its ink.
    var covered = scale >= 0.55 * maxScale * Math.pow(TITLE_START, POWER);
    show("over", !!video && onScreen && covered, function (value) {
      root.classList.toggle("hero-over", value);
    });
    // The header row stays with the frame and leaves the screen with it.
    show("lift", Math.round(Math.min(0, box.bottom - height)), function (value) {
      if (header) {
        header.style.transform = value ? "translateY(" + value + "px)" : "";
      }
    });
    show("playing", onScreen, function (value) {
      if (!video) {
        return;
      }
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
      draw(progress);
    }
  }

  function start() {
    if (request) {
      return;
    }
    root.classList.add("hero-flight");
    measure();
    tick();
  }

  function stop() {
    window.cancelAnimationFrame(request);
    request = 0;
    root.classList.remove("hero-flight", "hero-over");
    hero.style.removeProperty("--hero-foot");
    hero.style.removeProperty("--hero-title");
    if (header) {
      header.style.transform = "";
    }
    if (video) {
      video.pause();
    }
  }

  function choose() {
    if (lessMotion.matches) {
      stop();
    } else {
      start();
    }
  }

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
