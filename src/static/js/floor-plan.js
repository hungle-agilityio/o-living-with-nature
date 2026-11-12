/* Walk through the house (#floor-plan, one-page spec AC17): a room with a photo opens it in the
   dialog, with its "Illustrative photo" chip, its credit and a close button.

   The page works without this file: each room link then goes to the photo file. A browser
   without dialog support also follows the link. */
(function () {
  "use strict";

  var plan = document.getElementById("floor-plan");
  var dialog = document.querySelector("dialog.floor-plan__dialog");
  if (!plan || !dialog || typeof dialog.showModal !== "function") {
    return;
  }

  var box = dialog.querySelector(".floor-plan__box");
  var chip = box && box.querySelector(".media__chip");
  var credit = dialog.querySelector(".media__credit");
  if (!box || !chip || !credit) {
    return;
  }

  function open(link) {
    var old = box.querySelector("img");
    if (old) {
      box.removeChild(old);
    }
    var photo = document.createElement("img");
    photo.src = link.getAttribute("href");
    photo.alt = link.getAttribute("data-alt") || "";
    photo.width = Number(link.getAttribute("data-width")) || 0;
    photo.height = Number(link.getAttribute("data-height")) || 0;
    if (photo.width && photo.height) {
      box.style.aspectRatio = photo.width + " / " + photo.height;
      // The box keeps the photo's shape and stays short enough for the chip, credit and Close.
      box.style.setProperty("--photo-ratio", String(photo.width / photo.height));
    }
    box.insertBefore(photo, chip);

    var illustrative = link.hasAttribute("data-illustrative");
    chip.hidden = !illustrative;
    credit.textContent = illustrative ? link.getAttribute("data-credit") || "" : "";
    credit.hidden = !credit.textContent;
    dialog.setAttribute("aria-label", link.textContent);
    dialog.showModal();
  }

  plan.addEventListener("click", function (event) {
    // A new tab or window (a modifier key, or a button other than the main one) keeps the link.
    if (event.defaultPrevented || event.button !== 0) {
      return;
    }
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    var link = event.target.closest && event.target.closest("a.floor-plan__room");
    if (!link) {
      return;
    }
    event.preventDefault();
    open(link);
  });

  // A click on the backdrop, outside the photo and the button, closes the dialog too.
  dialog.addEventListener("click", function (event) {
    if (event.target !== dialog) {
      return;
    }
    var edge = dialog.getBoundingClientRect();
    var inside =
      event.clientX >= edge.left &&
      event.clientX <= edge.right &&
      event.clientY >= edge.top &&
      event.clientY <= edge.bottom;
    if (!inside) {
      dialog.close();
    }
  });
})();
