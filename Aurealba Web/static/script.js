// ── SPLASH SCREEN ──
window.addEventListener("load", () => {
  const splash = document.getElementById("splash");
  const main   = document.getElementById("main-content");
  if (splash && main) {
    setTimeout(() => {
      splash.classList.add("hide");
      main.classList.add("show");
    }, 2000);
  }
});


// ── SCROLL REVEAL ──
const observer = new IntersectionObserver(
  entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); }),
  { threshold: 0.25 }
);
document.querySelectorAll(".fade-up, .card, .catalog-card").forEach(el => observer.observe(el));


// ── HAMBURGER MENU (only if elements exist) ──
const menuToggle = document.getElementById("menuToggle");
const wcMenu     = document.getElementById("wcMenu");

if (menuToggle && wcMenu) {
  menuToggle.addEventListener("click", () => wcMenu.classList.toggle("show"));
  wcMenu.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => wcMenu.classList.remove("show"));
  });
  document.addEventListener("click", e => {
    if (!wcMenu.contains(e.target) && e.target !== menuToggle) {
      wcMenu.classList.remove("show");
    }
  });
}


// ── PAGE TRANSITION SHIMMER ──
const transitionScreen = document.getElementById("page-transition");

if (transitionScreen) {

  function triggerShimmer(href) {
    transitionScreen.classList.add("active");
    document.body.classList.add("page-loading");
    setTimeout(() => {
      window.location.href = href;
    }, 3000);
  }

  document.addEventListener("click", e => {
    const link = e.target.closest("a");
    if (!link) return;

    const href = link.getAttribute("href");
    if (!href) return;
    if (href === "#") return;
    if (href.startsWith("mailto:") || href.startsWith("tel:")) return;
    if (link.target === "_blank") return;

    try {
      const dest = new URL(href, window.location.origin);
      if (dest.href === window.location.href) return;
    } catch(e) { return; }

    e.preventDefault();
    triggerShimmer(href);
  });

  window.addEventListener("pageshow", () => {
    transitionScreen.classList.remove("active");
    document.body.classList.remove("page-loading");
  });
}