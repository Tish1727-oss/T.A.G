// ── PRODUCT GRID ──
(function() {
  const grid = document.getElementById('products-grid');
  if (!grid || typeof PRODUCTS === 'undefined') return;

  grid.innerHTML = PRODUCTS.map((p, i) => `
    <div class="product-card fade-up" id="pc-${i}">
      <a href="/product/${COLLECTION_KEY}/${i}" style="text-decoration:none;display:block;">
        <div class="product-emoji">${p.emoji}</div>
        <div class="product-info">
          <div class="product-name">${p.name}</div>
          <div class="product-collection">${COLLECTION}</div>
          <div class="product-price">Rs ${p.price.toLocaleString()}</div>
          <div style="font-size:13px;color:#8C7E68;margin-bottom:12px;line-height:1.5;">${p.description ? p.description.substring(0,80)+'…' : ''}</div>
        </div>
      </a>
      <div style="padding:0 20px 22px;">
        <div class="size-row" id="sr-${i}">
          ${p.sizes.map(s => `<button class="size-btn" data-size="${s}" onclick="selectSize(${i}, '${s}')">${s}</button>`).join('')}
        </div>
        <button class="atc-btn" onclick="addToCart(${i})" id="atc-${i}">Add to Cart 🛒</button>
      </div>
    </div>
  `).join('');

  const observer = new IntersectionObserver(
    entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }),
    { threshold: 0.1 }
  );
  document.querySelectorAll('.product-card').forEach(el => observer.observe(el));
})();

const selectedSizes = {};

function selectSize(productIndex, size) {
  selectedSizes[productIndex] = size;
  const row = document.getElementById('sr-' + productIndex);
  row.querySelectorAll('.size-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.size === size);
  });
}

function addToCart(productIndex) {
  const product = PRODUCTS[productIndex];
  const size = selectedSizes[productIndex];
  if (!size) {
    const sizeRow = document.getElementById('sr-' + productIndex);
    sizeRow.classList.add('shake');
    setTimeout(() => sizeRow.classList.remove('shake'), 500);
    showCartToast('Please select a size first!', 'warn');
    return;
  }

  const cart = JSON.parse(localStorage.getItem('tag_cart') || '[]');
  const existing = cart.find(i => i.name === product.name && i.size === size);
  if (existing) { existing.qty++; }
  else { cart.push({ name: product.name, collection: COLLECTION, size, price: product.price, qty: 1 }); }
  localStorage.setItem('tag_cart', JSON.stringify(cart));

  const btn = document.getElementById('atc-' + productIndex);
  btn.textContent = '✓ Added!';
  btn.style.background = 'linear-gradient(135deg,#3a7a4a,#5BAD6F)';
  setTimeout(() => { btn.textContent = 'Add to Cart 🛒'; btn.style.background = ''; }, 1200);

  updateCartBadge();
  showCartToast(`${product.name} added to cart`);
}

function showCartToast(msg, type) {
  const existing = document.getElementById('cart-toast');
  if (existing) existing.remove();
  const t = document.createElement('div');
  t.id = 'cart-toast';
  t.style.cssText = `position:fixed;bottom:100px;right:30px;z-index:99999;background:${type==='warn'?'#E8A83A':'#1A1510'};color:white;padding:13px 22px;border-radius:30px;font-size:14px;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,0.2);animation:toastSlide 0.3s ease;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t && t.remove(), 2500);
}