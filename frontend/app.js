// Sample Menu Data
const menuItems = [
  { id: '1', name: 'Margherita Pizza', category: 'Main', desc: 'Fresh basil, mozzarella & classic tomato sauce', price: 300 },
  { id: '2', name: 'Creamy Alfredo Pasta', category: 'Main', desc: 'Fettuccine pasta in rich garlic parmesan cream sauce', price: 250 },
  { id: '3', name: 'Sizzling Chocolate Brownie', category: 'Dessert', desc: 'Warm chocolate fudge brownie with vanilla ice cream', price: 150 },
  { id: '4', name: 'Garlic Cheese Bread', category: 'Appetizers', desc: 'Crispy toasted baguette with herb garlic butter & melted cheese', price: 180 },
  { id: '5', name: 'Crispy Paneer Tikka', category: 'Appetizers', desc: 'Cottage cheese cubes marinated in tandoori spices', price: 220 },
  { id: '6', name: 'Signature Berry Mocktail', category: 'Dessert', desc: 'Refreshing blend of wild berries, mint, and soda', price: 120 }
];

let cart = [];
let selectedTable = { id: '1', number: 'T01', capacity: 2 };
let guestCount = 2;

// Render Menu Catalog
function renderMenu(filter = 'all') {
  const grid = document.getElementById('menu-grid');
  grid.innerHTML = '';

  const filtered = filter === 'all' 
    ? menuItems 
    : menuItems.filter(item => item.category === filter);

  filtered.forEach(item => {
    const card = document.createElement('div');
    card.className = 'menu-card';
    card.innerHTML = `
      <div>
        <span class="menu-item-tag">${item.category}</span>
        <h4 class="menu-item-title">${item.name}</h4>
        <p class="menu-item-desc">${item.desc}</p>
      </div>
      <div class="menu-item-footer">
        <span class="menu-item-price">₹${item.price}</span>
        <button class="btn btn-secondary" onclick="addToCart('${item.id}')">+ Add</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

function filterMenu(category) {
  document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  renderMenu(category);
}

// Table Selection Handling
document.querySelectorAll('.table-card').forEach(card => {
  card.addEventListener('click', () => {
    if (card.querySelector('.table-badge.reserved')) return; // Ignore reserved tables

    document.querySelectorAll('.table-card').forEach(c => c.classList.remove('active'));
    card.classList.add('active');

    selectedTable = {
      id: card.dataset.tableId,
      number: card.dataset.tableNum,
      capacity: parseInt(card.dataset.cap)
    };

    guestCount = selectedTable.capacity;
    document.getElementById('guest-count-val').innerText = guestCount;
    document.getElementById('selected-table-display').value = `Table ${selectedTable.number} (${selectedTable.capacity} Guests)`;
  });
});

function adjustGuests(delta) {
  guestCount = Math.max(1, guestCount + delta);
  document.getElementById('guest-count-val').innerText = guestCount;
}

// Cart Functions
function addToCart(itemId) {
  const item = menuItems.find(i => i.id === itemId);
  const existing = cart.find(c => c.id === itemId);

  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ ...item, qty: 1 });
  }

  updateCartUI();
  toggleCart(true);
}

function updateCartUI() {
  const itemsContainer = document.getElementById('cart-items');
  const countSpan = document.getElementById('cart-count');

  const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
  countSpan.innerText = totalQty;

  if (cart.length === 0) {
    itemsContainer.innerHTML = '<p class="empty-cart-msg">Your order cart is empty.</p>';
    document.getElementById('cart-subtotal').innerText = '₹0.00';
    document.getElementById('cart-tax').innerText = '₹0.00';
    document.getElementById('cart-total').innerText = '₹0.00';
    return;
  }

  itemsContainer.innerHTML = '';
  let subtotal = 0;

  cart.forEach(item => {
    const itemSub = item.price * item.qty;
    subtotal += itemSub;

    const row = document.createElement('div');
    row.className = 'cart-item-row';
    row.innerHTML = `
      <div>
        <strong>${item.name}</strong>
        <div style="font-size:0.8rem; color:var(--text-muted)">₹${item.price} × ${item.qty}</div>
      </div>
      <span style="font-weight:700">₹${itemSub}</span>
    `;
    itemsContainer.appendChild(row);
  });

  const tax = subtotal * 0.05;
  const total = subtotal + tax;

  document.getElementById('cart-subtotal').innerText = `₹${subtotal.toFixed(2)}`;
  document.getElementById('cart-tax').innerText = `₹${tax.toFixed(2)}`;
  document.getElementById('cart-total').innerText = `₹${total.toFixed(2)}`;
}

function toggleCart(openState) {
  const drawer = document.getElementById('cart-drawer');
  if (typeof openState === 'boolean') {
    if (openState) drawer.classList.add('open');
    else drawer.classList.remove('open');
  } else {
    drawer.classList.toggle('open');
  }
}

function checkoutOrder() {
  if (cart.length === 0) return;
  alert('Order submitted to kitchen! Your food is being prepared.');
  cart = [];
  updateCartUI();
  toggleCart(false);
}

// Reservation Form Submit
function handleReservationSubmit(e) {
  e.preventDefault();
  const name = document.getElementById('cust-name').value;
  const phone = document.getElementById('cust-phone').value;
  const date = document.getElementById('res-date').value;
  const time = document.getElementById('res-time').value;

  const msg = `Booking confirmed for ${name} at Table ${selectedTable.number} on ${date} at ${time} (${guestCount} guests). Phone: ${phone}.`;
  document.getElementById('modal-details').innerText = msg;
  document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
}

// Initialize
renderMenu();
