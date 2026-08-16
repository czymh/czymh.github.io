/* Zhao Chen — personal site
 * Vanilla JS: mobile nav, scroll reveal, figure lightbox.
 * No dependencies. */

(function () {
  "use strict";

  // Progressive enhancement flag for CSS reveal rules.
  document.documentElement.classList.add("js");

  /* ---------- Mobile nav ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");

  function setNav(open) {
    if (!header || !toggle) return;
    header.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      setNav(!header.classList.contains("nav-open"));
    });
  }

  if (nav) {
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setNav(false);
  });

  /* ---------- Reveal on scroll ---------- */
  var revealables = document.querySelectorAll(
    ".about-grid, .pub-item, .project-card, .figure-card, .teaching-item, .section-title"
  );
  if ("IntersectionObserver" in window) {
    revealables.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Figure lightbox ---------- */
  var lightbox = document.getElementById("lightbox");
  var lbImg = lightbox ? lightbox.querySelector(".lightbox-img") : null;
  var lbCaption = lightbox ? lightbox.querySelector(".lightbox-caption") : null;
  var lbClose = lightbox ? lightbox.querySelector(".lightbox-close") : null;

  function openLightbox(src, caption) {
    if (!lightbox || !lbImg) return;
    lbImg.src = src;
    lbImg.alt = caption || "";
    if (lbCaption) lbCaption.textContent = caption || "";
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    if (!lightbox) return;
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  document.querySelectorAll(".figure-thumb[data-src]").forEach(function (thumb) {
    thumb.addEventListener("click", function () {
      openLightbox(thumb.getAttribute("data-src"), thumb.getAttribute("data-caption"));
    });
  });

  if (lightbox) {
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox || e.target === lbClose) closeLightbox();
    });
    if (lbClose) lbClose.addEventListener("click", closeLightbox);
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeLightbox();
  });

  /* ---------- Publications rendered from data/publications.json ---------- */
  // The static list in index.html is the no-JS fallback; this replaces it
  // when the (ADS-synced) JSON is available.
  var pubList = document.getElementById("pub-list");

  function escapeHtml(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // Up to five authors; bold "Zhao Chen"; append ", et al." when truncated.
  function authorNames(authors) {
    if (!authors || !authors.length) return "";
    var shown = authors.slice(0, 5);
    var names = shown.map(function (name) {
      name = escapeHtml(name.trim());
      return name === "Zhao Chen" ? "<strong>Zhao Chen</strong>" : name;
    });
    var more = authors.length > 5 ? ", et al." : "";
    return names.join(", ") + more;
  }

  function renderPublications(publications) {
    if (!pubList || !publications || !publications.length) return;
    var html = publications.map(function (p) {
      var link = p.doi
        ? "https://doi.org/" + p.doi
        : (p.bibcode
            ? "https://ui.adsabs.harvard.edu/abs/" + p.bibcode + "/abstract"
            : "#");
      var venue = authorNames(p.authors) + " · " + escapeHtml(p.venue);
      return '<li class="pub-item">' +
        '<span class="pub-year">' + escapeHtml(p.year) + "</span>" +
        '<div class="pub-main">' +
        '<h3 class="pub-title"><a href="' + link + '" target="_blank" rel="noopener">' + escapeHtml(p.title) + "</a></h3>" +
        '<p class="pub-venue">' + venue + "</p>" +
        "</div></li>";
    }).join("");
    pubList.innerHTML = html;
  }

  if (pubList && "fetch" in window) {
    fetch("data/publications.json", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status)); })
      .then(function (data) { renderPublications(data.publications); })
      .catch(function (err) {
        // Keep the static fallback list on failure.
        if (window.console) console.warn("Publications sync unavailable:", err);
      });
  }
})();
