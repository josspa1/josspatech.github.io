/**
 * Product-page story phone — tap/click center glass through screenshot beats.
 * Works on desktop + touch. Respects prefers-reduced-motion.
 */
(function () {
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  ready(function () {
    var root = document.querySelector("[data-story-phone]");
    if (!root) return;

    var beats;
    try {
      var raw = root.getAttribute("data-beats");
      beats = raw ? JSON.parse(raw) : null;
    } catch (e) {
      beats = null;
    }
    if (!beats || !beats.length) return;

    var img = root.querySelector("[data-story-img]");
    var caption = root.querySelector("[data-story-caption]");
    var hint = root.querySelector("[data-story-hint]");
    var dots = root.querySelector("[data-story-dots]");
    var film = root.querySelector("[data-story-film]");
    var advance = root.querySelector("[data-story-advance]");
    var i = 0;
    var started = false;
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function paint(index, fromUser) {
      i = ((index % beats.length) + beats.length) % beats.length;
      var b = beats[i];
      if (img) {
        if (!reduce && fromUser) {
          img.classList.add("is-fading");
          window.setTimeout(function () {
            img.src = b.src;
            img.alt = b.alt || "";
            img.classList.remove("is-fading");
          }, 140);
        } else {
          img.src = b.src;
          img.alt = b.alt || "";
        }
      }
      if (caption) caption.textContent = b.caption || "";
      if (hint) {
        if (fromUser || started) {
          hint.hidden = true;
        }
      }
      if (dots) {
        Array.prototype.forEach.call(dots.querySelectorAll("[data-story-dot]"), function (dot, di) {
          var on = di === i;
          dot.setAttribute("aria-selected", on ? "true" : "false");
          dot.classList.toggle("is-active", on);
        });
      }
      if (film) {
        Array.prototype.forEach.call(film.querySelectorAll("[data-story-thumb]"), function (th, ti) {
          th.classList.toggle("is-active", ti === i);
          th.setAttribute("aria-current", ti === i ? "true" : "false");
        });
      }
    }

    function go(next, fromUser) {
      if (fromUser) started = true;
      paint(next, fromUser);
    }

    if (dots) {
      beats.forEach(function (b, di) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "story-dot";
        btn.setAttribute("data-story-dot", String(di));
        btn.setAttribute("role", "tab");
        btn.setAttribute("aria-label", b.caption || ("Screen " + (di + 1)));
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          go(di, true);
        });
        dots.appendChild(btn);
      });
    }

    if (film) {
      beats.forEach(function (b, di) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "story-thumb";
        btn.setAttribute("data-story-thumb", String(di));
        btn.setAttribute("aria-label", b.caption || ("Screen " + (di + 1)));
        var th = document.createElement("img");
        th.src = b.src;
        th.alt = "";
        th.loading = "lazy";
        btn.appendChild(th);
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          e.stopPropagation();
          go(di, true);
        });
        film.appendChild(btn);
      });
    }

    if (advance) {
      advance.addEventListener("click", function () {
        go(i + 1, true);
      });
      advance.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          go(i + 1, true);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          go(i + 1, true);
        } else if (e.key === "ArrowLeft") {
          e.preventDefault();
          go(i - 1, true);
        }
      });
    }

    paint(0, false);

    // One gentle peep that more exists (desktop + phone), then stop
    if (!reduce && beats.length > 1) {
      window.setTimeout(function () {
        if (started) return;
        root.classList.add("story-nudge");
        window.setTimeout(function () {
          root.classList.remove("story-nudge");
        }, 900);
      }, 1200);
    }
  });
})();
