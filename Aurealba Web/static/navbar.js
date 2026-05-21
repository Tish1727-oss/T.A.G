document.addEventListener("DOMContentLoaded", () => {

  // CATALOG DROPDOWN
  const dropdown = document.querySelector(".dropdown");
  if (dropdown) {
    const toggle = dropdown.querySelector("a");
    toggle.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      dropdown.classList.toggle("active");
    });
    document.addEventListener("click", e => {
      if (!dropdown.contains(e.target)) dropdown.classList.remove("active");
    });
  }

  // USER DROPDOWN
  const userDropdown = document.querySelector(".user-dropdown");
  if (userDropdown) {
    const icon = userDropdown.querySelector(".nav-user-icon");
    icon.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      userDropdown.classList.toggle("active");
    });
    document.addEventListener("click", e => {
      if (!userDropdown.contains(e.target)) userDropdown.classList.remove("active");
    });
  }

  // SEARCH
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");
  if (searchInput && searchResults) {
    searchInput.addEventListener("input", async () => {
      const q = searchInput.value.trim();
      if (!q) { searchResults.style.display = "none"; return; }
      const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      if (!data.length) { searchResults.style.display = "none"; return; }
      searchResults.innerHTML = data.map(r =>
        `<a class="sr-item" href="${r.url}">${r.name}</a>`
      ).join("");
      searchResults.style.display = "block";
    });
    document.addEventListener("click", e => {
      if (!searchInput.contains(e.target)) searchResults.style.display = "none";
    });
  }

  // FADE UP CARDS
  const fadeEls = document.querySelectorAll(".fade-up, .card");
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
  }, { threshold: 0.1 });
  fadeEls.forEach(el => observer.observe(el));

  // ── HAMBURGER MOBILE MENU ──
  const navbar = document.querySelector('.navbar');
  const header = document.querySelector('.wc-header');
  if (!navbar || !header) return;

  // Create hamburger button
  const ham = document.createElement('button');
  ham.className = 'hamburger';
  ham.setAttribute('aria-label', 'Menu');
  ham.innerHTML = '<span></span><span></span><span></span>';

  // Insert hamburger INSIDE header, after the logo
  header.appendChild(ham);

  // Create close button inside the navbar overlay
  const closeBtn = document.createElement('button');
  closeBtn.className = 'mobile-close-btn';
  closeBtn.textContent = '×';
  navbar.insertBefore(closeBtn, navbar.firstChild);

  function openMenu() {
    ham.classList.add('open');
    navbar.classList.add('mobile-open');
    document.body.style.overflow = 'hidden';
  }

  function closeMenu() {
    ham.classList.remove('open');
    navbar.classList.remove('mobile-open');
    document.body.style.overflow = '';
  }

  ham.addEventListener('click', openMenu);
  closeBtn.addEventListener('click', closeMenu);

  // Close when a nav link is clicked
  navbar.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMenu);
  });

});