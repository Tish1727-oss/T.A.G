// ── FLOATING CART ──
function getCart() { return JSON.parse(localStorage.getItem('tag_cart') || '[]'); }
function saveCart(c) { localStorage.setItem('tag_cart', JSON.stringify(c)); }

function updateCartBadge() {
  const cart = getCart();
  const count = cart.reduce((s, i) => s + i.qty, 0);
  const badge = document.getElementById('cart-badge');
  if (badge) {
    badge.textContent = count;
    badge.style.display = count > 0 ? 'flex' : 'none';
  }
}

function toggleCart() {
  const panel = document.getElementById('cart-panel');
  const overlay = document.getElementById('cart-overlay');
  const isOpen = panel.classList.contains('open');
  if (isOpen) {
    panel.classList.remove('open');
    overlay.classList.remove('open');
  } else {
    renderCartPanel();
    panel.classList.add('open');
    overlay.classList.add('open');
  }
}

function renderCartPanel() {
  const cart = getCart();
  const itemsEl = document.getElementById('cart-panel-items');
  const footerEl = document.getElementById('cart-panel-footer');

  if (!cart.length) {
    itemsEl.innerHTML = '<div style="text-align:center;padding:60px 20px;color:#8C7E68;"><img src="/static/images/cart.png" style="width:52px;opacity:0.4;margin-bottom:12px"><p style="font-size:15px">Your cart is empty</p></div>';
    footerEl.style.display = 'none';
    return;
  }

  footerEl.style.display = 'block';
  itemsEl.innerHTML = cart.map((item, i) => `
    <div class="cp-item">
      <div class="cp-item-emoji">${getEmoji(item.collection)}</div>
      <div class="cp-item-info">
        <div class="cp-item-name">${item.name}</div>
        <div class="cp-item-meta">${item.collection} · Size ${item.size}</div>
        <div class="cp-qty">
          <button class="cp-qty-btn" onclick="cartChangeQty(${i},-1)">−</button>
          <span>${item.qty}</span>
          <button class="cp-qty-btn" onclick="cartChangeQty(${i},1)">+</button>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">
        <div class="cp-item-price">Rs ${(item.price * item.qty).toLocaleString()}</div>
        <span onclick="cartRemove(${i})" style="color:#C45A5A;cursor:pointer;font-size:16px;" title="Remove">✕</span>
      </div>
    </div>
  `).join('');

  const total = cart.reduce((s, i) => s + i.price * i.qty, 0);
  document.getElementById('cart-total').textContent = 'Rs ' + total.toLocaleString();
}

function cartChangeQty(i, delta) {
  const cart = getCart();
  cart[i].qty = Math.max(1, cart[i].qty + delta);
  saveCart(cart); renderCartPanel(); updateCartBadge();
}

function cartRemove(i) {
  const cart = getCart();
  cart.splice(i, 1);
  saveCart(cart); renderCartPanel(); updateCartBadge();
}

function getEmoji(collection) {
  const map = { 'Casual Wear':'👗', 'Party Wear':'✨', 'Office Wear':'💼', 'Traditional Wear':'👘' };
  return map[collection] || '👗';
}

// Init on page load
document.addEventListener('DOMContentLoaded', updateCartBadge);