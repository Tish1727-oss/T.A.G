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
