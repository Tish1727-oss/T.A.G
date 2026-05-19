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
  const userIcon = document.querySelector(".nav-user-icon");
  if (userDropdown && userIcon) {
    userIcon.addEventListener("click", e => {
      e.preventDefault();
      e.stopPropagation();
      userDropdown.classList.toggle("active");
    });
    document.addEventListener("click", e => {
      if (!userDropdown.contains(e.target)) userDropdown.classList.remove("active");
    });
  }

  // LIVE SEARCH
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");
  if (searchInput && searchResults) {
    searchInput.addEventListener("input", async () => {
      const q = searchInput.value.trim();
      if (!q) {
        searchResults.innerHTML = "";
        searchResults.style.display = "none";
        return;
      }
      const res  = await fetch(`/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      searchResults.innerHTML = data.length
        ? data.map(d => `<a class='sr-item' href='${d.url}'>${d.name}</a>`).join("")
        : "<div class='sr-item'>No results found</div>";
      searchResults.style.display = "block";
    });
    document.addEventListener("click", e => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = "none";
      }
    });
  }

});