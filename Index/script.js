// THEME TOGGLE
const toggleBtn = document.getElementById("themeToggle");

function applyTheme(theme) {
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add(theme);
  localStorage.setItem("theme", theme);
  toggleBtn.textContent = theme === "light-theme" ? "Dark" : "Light";
}

toggleBtn.addEventListener("click", () => {
  applyTheme(
    document.body.classList.contains("light-theme")
      ? "dark-theme"
      : "light-theme"
  );
});

// Load theme from localStorage
applyTheme(localStorage.getItem("theme") || "dark-theme");


// SPLASH SCREEN
window.addEventListener("load", () => {
  const splash = document.getElementById("splash");
  const main = document.getElementById("main-content");

  setTimeout(() => {
    splash.classList.add("hide");
    main.classList.add("show");
  }, 2000);
});


// SCROLL REVEAL ANIMATIONS
const observer = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) entry.target.classList.add("visible");
    });
  },
  { threshold: 0.25 }
);

document.querySelectorAll(".fade-up, .card").forEach(el =>
  observer.observe(el)
);


// HAMBURGER MENU
const menuToggle = document.getElementById("menuToggle");
const wcMenu = document.getElementById("wcMenu");

menuToggle.addEventListener("click", () => {
  wcMenu.classList.toggle("show");
});

// Close menu when clicking a link
wcMenu.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", () => {
    wcMenu.classList.remove("show");
  });
});

// Close menu if clicking outside
document.addEventListener("click", (e) => {
  if (!wcMenu.contains(e.target) && e.target !== menuToggle) {
    wcMenu.classList.remove("show");
  }
});


// ----------------------------------------------------
// PAGE TRANSITION (BLACK SCREEN + SHIMMERING T.A.G)
// ----------------------------------------------------

const transitionScreen = document.getElementById("page-transition");

document.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", (e) => {
    if (!link.href || link.href === window.location.href) return;

    e.preventDefault();

    // Show black transition screen
    transitionScreen.classList.add("active");
    document.body.classList.add("page-loading");

    setTimeout(() => {
      window.location.href = link.href;
    }, 3000); // 3 seconds shimmer
  });
});
