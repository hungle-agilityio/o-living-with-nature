/* The counter of the page (contact-counter spec AC9 to AC12).

   Sends one view to /count/ when the page loads, and one click when a contact button is pressed.
   Nothing is kept in the browser, the links are never stopped or delayed, and a count that fails
   is simply lost: the visitor sees nothing. The page works the same without this file. */
(function () {
  "use strict";

  var ADDRESS = "/count/";

  // True when the browser took the beacon; false when it has none, refuses it or throws.
  function beacon(body) {
    var taken = false;
    try {
      taken = !!(navigator.sendBeacon && navigator.sendBeacon(ADDRESS, body));
    } catch (error) {
      // Not taken: the fetch below sends it.
    }
    return taken;
  }

  function send(fields) {
    try {
      var body = new URLSearchParams(fields);
      // A beacon the browser does not take goes by the keepalive fetch instead.
      if (!beacon(body) && window.fetch) {
        fetch(ADDRESS, { method: "POST", keepalive: true, body: body }).catch(function () {});
      }
    } catch (error) {
      // A count that cannot be sent is lost.
    }
  }

  // A click, or a press with the middle button (auxclick), on any contact button.
  function press(event) {
    try {
      if (event.type === "auxclick" && event.button !== 1) {
        return;
      }
      // Another button than the main one is counted by its auxclick only, so once.
      if (event.type === "click" && event.button !== 0) {
        return;
      }
      var target = event.target;
      var link = target && target.closest ? target.closest("a[data-channel]") : null;
      if (link) {
        send({
          kind: "click",
          channel: link.getAttribute("data-channel") || "",
          place: link.getAttribute("data-place") || "",
        });
      }
    } catch (error) {
      // Never in the way of the link.
    }
  }

  function view() {
    send({ kind: "view" });
  }

  // A page the browser prerenders counts its view only once the visitor is shown it.
  if (document.prerendering) {
    document.addEventListener("prerenderingchange", view, { once: true });
  } else {
    view();
  }
  document.addEventListener("click", press);
  document.addEventListener("auxclick", press);
})();
