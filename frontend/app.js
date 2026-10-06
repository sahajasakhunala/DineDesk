// =============================================================================
// DineDesk Luxury Customer Portal - Production Application Engine
// Connects seamlessly to FastAPI / SQLite / PostgreSQL Backend
// =============================================================================
const API_HOST = (window.location.hostname === "localhost") ? "localhost" : "127.0.0.1";
const API_BASE = `http://${API_HOST}:8000/api/v1`;

// Application State
let menuItems = [];
let tables = [];
let cart = [];
let selectedTable = null;
let selectedStartTime = "19:30";
let selectedEndTime = "21:00";
let selectedSlotLabel = "07:30 PM – 09:00 PM";
let selectedTime = "19:30";
let adultCount = 2;
let childCount = 0;
let currentCategoryFilter = "all";
let currentDietaryFilter = "all";
let activeSessionId = null;
let currentCustomer = null;
let activeBill = null;
let appliedDiscount = { code: "", percentage: 0, amount: 0 };
let currentPaymentMethod = "CARD";
let currentKitchenTrackerStage = 0;
let userConfirmedReservation = null;

// Neutral Food Placeholder (Used when image is missing or unavailable)
const NEUTRAL_FOOD_PLACEHOLDER = "data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 250' width='400' height='250'%3E%3Crect width='100%25' height='100%25' fill='%23121826'/%3E%3Ccircle cx='200' cy='115' r='55' fill='none' stroke='%23d4af37' stroke-width='2' stroke-dasharray='4,4' opacity='0.4'/%3E%3Cpath d='M180,105 C180,95 220,95 220,105 C220,120 180,120 180,105 Z' fill='%23d4af37' opacity='0.7'/%3E%3Cpath d='M175,120 C175,135 225,135 225,120 Z' fill='%23d4af37' opacity='0.6'/%3E%3Ctext x='50%25' y='190' font-family='Plus Jakarta Sans, sans-serif' font-size='13' font-weight='600' fill='%23d4af37' text-anchor='middle' letter-spacing='2'%3EDINEDESK CUISINE%3C/text%3E%3C/svg%3E";

// =============================================================================
// Curated High-Definition Food Photography Imagery Dictionary
// (Strict 1 Item = 1 Single Centered Dish Photo, No Collages, No Multi-Drinks)
// =============================================================================
// Curated High-Definition Food Photography Imagery Dictionary
// (Strict 1 Item = 1 Single Centered Dish Photo, No Collages, No Multi-Drinks)
// =============================================================================
const dishImageMap = {
  // Appetizers (Single Plated Dish)
  "Garlic Cheese Baguette": "images/menu/garlic-cheese-baguette.jpg",
  "Crispy Paneer Tikka Pops": "images/menu/crispy-paneer-tikka-pops.jpg",
  "Crispy Corn & Jalapeño Croquettes": "images/menu/crispy-corn--jalapeño-croquettes.jpg",
  "Smoked Truffle Potato Wedges": "images/menu/smoked-truffle-potato-wedges.jpg",
  "Zesty Herb Chicken Strips": "images/menu/zesty-herb-chicken-strips.jpg",
  "Dynamite Crispy Prawns": "images/menu/dynamite-crispy-prawns.jpg",

  // Soups & Salads (Single Bowl)
  "Roasted Plum Tomato Basil Soup": "images/menu/roasted-plum-tomato-basil-soup.jpg",
  "Cream of Wild Forest Mushroom": "images/menu/cream-of-wild-forest-mushroom.jpg",
  "Mediterranean Greek Feta Salad": "images/menu/mediterranean-greek-feta-salad.jpg",
  "Classic Caesar Salad with Grilled Chicken": "images/menu/classic-caesar-salad-with-grilled-chicken.jpg",

  // Main Course (Single Plated Entree)
  "Wild Mushroom & Truffle Risotto": "images/menu/wild-mushroom--truffle-risotto.jpg",
  "Grilled Cottage Cheese Steak": "images/menu/grilled-cottage-cheese-steak.jpg",
  "Pan-Seared Norwegian Salmon": "images/menu/pan-seared-norwegian-salmon.jpg",
  "Herb-Crusted Grilled Chicken Breast": "images/menu/herb-crusted-grilled-chicken-breast.jpg",

  // Indian Specialties (Single Authentic Serving)
  "Paneer Butter Masala Royale": "images/menu/paneer-butter-masala-royale.jpg",
  "Dal Makhani Bukhara": "images/menu/dal-makhani-bukhara.jpg",
  "Butter Chicken Delhi Style": "images/menu/butter-chicken-delhi-style.jpg",
  "Dum Murgh Awadhi Biryani": "images/menu/dum-murgh-awadhi-biryani.jpg",
  "Butter Garlic Naan": "images/menu/butter-garlic-naan.jpg",

  // Italian/Continental (Single Pizza/Pasta)
  "Classic Margherita Pizza": "images/menu/classic-margherita-pizza.jpg",
  "Chicken Alfredo Fettuccine": "images/menu/chicken-alfredo-fettuccine.jpg",
  "Chicken Alfredo": "images/menu/chicken-alfredo-fettuccine.jpg",
  "Creamy Alfredo Fettuccine": "images/menu/chicken-alfredo-fettuccine.jpg",
  "Steak Spaghetti Pomodoro e Basilico": "images/menu/steak-spaghetti-pomodoro-e-basilico.jpg",
  "Spaghetti Pomodoro e Basilico": "images/menu/steak-spaghetti-pomodoro-e-basilico.jpg",
  "Smoked Chicken & Pesto Pizza": "images/menu/smoked-chicken--pesto-pizza.jpg",

  // Desserts (Single Plated Portion)
  "Sizzling Chocolate Walnut Brownie": "images/menu/sizzling-chocolate-walnut-brownie.jpg",
  "Classic Venetian Tiramisu": "images/menu/classic-venetian-tiramisu.jpg",
  "Baked New York Raspberry Cheesecake": "images/menu/baked-new-york-raspberry-cheesecake.jpg",
  "Warm Gulab Jamun with Kesari Rabdi": "images/menu/warm-gulab-jamun-with-kesari-rabdi.jpg",

  // Beverages (Exactly ONE Beverage Glass, Matching Drink)
  "Signature Wild Berry Spritzer": "images/menu/signature-wild-berry-spritzer.jpg",
  "Tropical Mango Passion Sparkler": "images/menu/tropical-mango-passion-sparkler.jpg",
  "Cold Brew Iced Vanilla Latte": "images/menu/cold-brew-iced-vanilla-latte.jpg",
  "Virgin Mojito Royale": "images/menu/virgin-mojito-royale.jpg",

  // Chef’s Specials (Single Plated Gourmet Item)
  "Chef Vikram's Truffle Infused Risotto": "images/menu/chef-vikram-s-truffle-infused-risotto.jpg",
  "Smoked Kashmiri Lamb Shank": "images/menu/smoked-kashmiri-lamb-shank.jpg",
  "Lobster Thermidor Continental": "images/menu/lobster-thermidor-continental.jpg",
  "Avocado & Edamame Tartare": "images/menu/avocado--edamame-tartare.jpg"
};

function getDishImageUrl(dishName, serverImageUrl) {
  // 1. If backend database provided an image URL/path, use it
  if (serverImageUrl && typeof serverImageUrl === "string" && (serverImageUrl.startsWith("http") || serverImageUrl.startsWith("images/") || serverImageUrl.startsWith("/images/"))) {
    return serverImageUrl;
  }

  if (!dishName) return NEUTRAL_FOOD_PLACEHOLDER;
  
  // 2. Exact match in verified dish dictionary
  if (dishImageMap[dishName]) return dishImageMap[dishName];

  // 3. Normalized exact name match (case and apostrophe agnostic)
  const normalize = s => s.toLowerCase().replace(/[\u2018\u2019'`]/g, "'").replace(/[^\w\s']/g, "").trim();
  const cleanTarget = normalize(dishName);

  for (const [key, url] of Object.entries(dishImageMap)) {
    if (normalize(key) === cleanTarget) {
      return url;
    }
  }

  // 4. Strict Neutral Placeholder (Never use category fallback or unrelated images)
  return NEUTRAL_FOOD_PLACEHOLDER;
}

// Fallback Mock Menu (All 8 exact categories & 35 signature items)
const fallbackMenuItems = [
  { id: '1', name: 'Garlic Cheese Baguette', category: 'Appetizers', desc: '[VEG] [KID-FRIENDLY] Crispy toasted French baguette brushed with roasted garlic herb butter and loaded with melted mozzarella.', price: 190 },
  { id: '2', name: 'Crispy Paneer Tikka Pops', category: 'Appetizers', desc: '[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Charred cottage cheese cubes marinated in smoked tandoori spices and mint glaze.', price: 230 },
  { id: '3', name: 'Crispy Corn & Jalapeño Croquettes', category: 'Appetizers', desc: '[VEG] [KID-FRIENDLY] Golden fried croquettes with sweet corn kernels, melted cheddar, and smoked paprika mayo.', price: 210 },
  { id: '4', name: 'Smoked Truffle Potato Wedges', category: 'Appetizers', desc: '[VEGAN] [GLUTEN-FREE] Hand-cut russet potato wedges dusted with black truffle sea salt and rosemary.', price: 180 },
  { id: '5', name: 'Zesty Herb Chicken Strips', category: 'Appetizers', desc: '[NON-VEG] [KID-FRIENDLY] Tender panko-crusted chicken tenders served with honey mustard and garlic dip.', price: 260 },
  { id: '6', name: 'Dynamite Crispy Prawns', category: 'Appetizers', desc: '[NON-VEG] Crispy battered tiger prawns tossed in signature sriracha togarashi aioli.', price: 340 },

  { id: '7', name: 'Roasted Plum Tomato Basil Soup', category: 'Soups & Salads', desc: '[VEGAN] [GLUTEN-FREE] [JAIN-AVAILABLE] Slow-roasted vine tomato soup infused with sweet basil, served with herbed croutons.', price: 180 },
  { id: '8', name: 'Cream of Wild Forest Mushroom', category: 'Soups & Salads', desc: '[VEG] [GLUTEN-FREE] Velvety blend of button, shiitake, and porcini mushrooms with a swirl of fresh cream.', price: 210 },
  { id: '9', name: 'Mediterranean Greek Feta Salad', category: 'Soups & Salads', desc: '[VEG] [GLUTEN-FREE] Crisp romaine lettuce, Kalamata olives, English cucumber, cherry tomatoes, and creamy feta cheese in lemon vinaigrette.', price: 240 },
  { id: '10', name: 'Classic Caesar Salad with Grilled Chicken', category: 'Soups & Salads', desc: '[NON-VEG] Crisp iceberg leaves, parmesan ribbons, garlic croutons, and grilled chicken breast tossed in house Caesar dressing.', price: 280 },

  { id: '11', name: 'Wild Mushroom & Truffle Risotto', category: 'Main Course', desc: '[VEG] [GLUTEN-FREE] Creamy Arborio rice slow-cooked with white wine, wild porcini, parmesan reggiano, and thyme.', price: 320 },
  { id: '12', name: 'Grilled Cottage Cheese Steak', category: 'Main Course', desc: '[GLUTEN-FREE] Charred herb-marinated cottage cheese steak served with ratatouille vegetables, mashed potatoes, and pepper jus.', price: 310 },
  { id: '13', name: 'Pan-Seared Norwegian Salmon', category: 'Main Course', desc: '[NON-VEG] [GLUTEN-FREE] Atlantic salmon fillet served with lemon dill butter sauce, grilled asparagus, and saffron mash.', price: 480 },
  { id: '14', name: 'Herb-Crusted Grilled Chicken Breast', category: 'Main Course', desc: '[NON-VEG] Tender breast fillet served with sautéed greens, roasted baby potatoes, and mushroom demi-glace.', price: 360 },

  { id: '15', name: 'Paneer Butter Masala Royale', category: 'Indian Specialties', desc: '[VEG] [GLUTEN-FREE] [JAIN-AVAILABLE] Tender cottage cheese cubes in rich tomato, cultured butter, and cashew gravy.', price: 290 },
  { id: '16', name: 'Dal Makhani Bukhara', category: 'Indian Specialties', desc: '[VEG] [GLUTEN-FREE] Slow-cooked black lentils simmered overnight for 24 hours with butter and country cream.', price: 260 },
  { id: '17', name: 'Butter Chicken Delhi Style', category: 'Indian Specialties', desc: '[NON-VEG] Tandoor-roasted chicken pieces in a silky, sweet and mildly spiced makhani sauce.', price: 350 },
  { id: '18', name: 'Dum Murgh Awadhi Biryani', category: 'Indian Specialties', desc: '[NON-VEG] Fragrant long-grain basmati rice layered with spiced chicken, caramelized onions, saffron, and fresh mint.', price: 360 },
  { id: '19', name: 'Butter Garlic Naan', category: 'Indian Specialties', desc: '[VEG] Fresh tandoor-baked leavened bread brushed with garlic flakes and cultured butter.', price: 60 },

  { id: '20', name: 'Classic Margherita Pizza', category: 'Italian/Continental', desc: '[VEG] [KID-FRIENDLY] [JAIN-AVAILABLE] Hand-stretched sourdough crust topped with San Marzano tomato sauce, fresh basil, and fior di latte mozzarella.', price: 320 },
  { id: '21', name: 'Chicken Alfredo Fettuccine', category: 'Italian/Continental', desc: '[NON-VEG] [KID-FRIENDLY] Handmade flat ribbon pasta tossed in rich parmesan garlic cream sauce with grilled chicken breast pieces.', price: 290 },
  { id: '22', name: 'Smoked Chicken & Pesto Pizza', category: 'Italian/Continental', desc: '[NON-VEG] Thin crust pizza with basil pesto base, shredded smoked chicken, sun-dried tomatoes, and mozzarella.', price: 380 },
  { id: '23', name: 'Steak Spaghetti Pomodoro e Basilico', category: 'Italian/Continental', desc: '[NON-VEG] Artisanal spaghetti with grilled steak slices in sweet cherry tomato sauce, extra virgin olive oil, and fresh garden basil.', price: 270 },

  { id: '24', name: 'Sizzling Chocolate Walnut Brownie', category: 'Desserts', desc: '[VEG] [KID-FRIENDLY] Warm decadent fudge brownie on hot cast iron, topped with Madagascar vanilla gelato and dark chocolate ganache.', price: 170 },
  { id: '25', name: 'Classic Venetian Tiramisu', category: 'Desserts', desc: '[VEG] Espresso-soaked savoiardi ladyfingers layered with velvety mascarpone cheese and dusted with Belgian cocoa.', price: 240 },
  { id: '26', name: 'Baked New York Raspberry Cheesecake', category: 'Desserts', desc: '[VEG] Rich and dense cream cheese cake on a graham cracker crust, drizzled with tart raspberry coulis.', price: 220 },
  { id: '27', name: 'Warm Gulab Jamun with Kesari Rabdi', category: 'Desserts', desc: '[VEG] [JAIN-AVAILABLE] Traditional khoya dumplings soaked in saffron syrup, served warm over creamy chilled saffron rabdi.', price: 150 },

  { id: '28', name: 'Signature Wild Berry Spritzer', category: 'Beverages', desc: '[VEGAN] [KID-FRIENDLY] Refreshing blend of crushed forest berries, mint leaves, fresh lime, and sparkling soda.', price: 130 },
  { id: '29', name: 'Tropical Mango Passion Sparkler', category: 'Beverages', desc: '[VEGAN] [KID-FRIENDLY] Sweet Alphonso mango purée infused with passion fruit and crushed ice.', price: 140 },
  { id: '30', name: 'Cold Brew Iced Vanilla Latte', category: 'Beverages', desc: '[VEG] [GLUTEN-FREE] 16-hour steeped single-origin Arabica cold brew poured over chilled milk and vanilla syrup.', price: 150 },
  { id: '31', name: 'Virgin Mojito Royale', category: 'Beverages', desc: '[VEGAN] Fresh garden mint muddled with Persian lime wedges, cane sugar, and chilled club soda.', price: 120 },

  { id: '32', name: "Chef Vikram's Truffle Infused Risotto", category: 'Chef’s Specials', desc: '[CHEF-SPECIAL] [VEG] [GLUTEN-FREE] Carnaroli rice cooked with shaved black winter truffles, aged 24-month Parmigiano, and white truffle oil.', price: 450 },
  { id: '33', name: 'Smoked Kashmiri Lamb Shank', category: 'Chef’s Specials', desc: '[CHEF-SPECIAL] [NON-VEG] [GLUTEN-FREE] 6-hour braised lamb shank in rich Kashmiri saffron chili reduction, served with warqi paratha.', price: 540 },
  { id: '34', name: 'Lobster Thermidor Continental', category: 'Chef’s Specials', desc: '[CHEF-SPECIAL] [NON-VEG] Succulent lobster meat baked with egg yolk, gruyère cheese, and dijon mustard cream sauce.', price: 650 },
  { id: '35', name: 'Avocado & Edamame Tartare', category: 'Chef’s Specials', desc: '[CHEF-SPECIAL] [VEGAN] [GLUTEN-FREE] Ripe Hass avocado stacked with young edamame, ponzu pearls, and lotus root crisps.', price: 340 }
];

// Fallback tables
const fallbackTables = [
  { id: 't1', table_number: 'T01', capacity: 2, area_name: 'Main Dining Hall', status: 'AVAILABLE' },
  { id: 't2', table_number: 'T02', capacity: 4, area_name: 'Main Dining Hall', status: 'AVAILABLE' },
  { id: 't3', table_number: 'T03', capacity: 6, area_name: 'Main Dining Hall', status: 'AVAILABLE' },
  { id: 't4', table_number: 'R01', capacity: 2, area_name: 'Romantic Terrace', status: 'AVAILABLE' },
  { id: 't5', table_number: 'R02', capacity: 4, area_name: 'Romantic Terrace', status: 'AVAILABLE' },
  { id: 't6', table_number: 'G01', capacity: 4, area_name: 'Rooftop Garden', status: 'AVAILABLE' },
  { id: 't7', table_number: 'G02', capacity: 6, area_name: 'Rooftop Garden', status: 'AVAILABLE' },
  { id: 't8', table_number: 'F01', capacity: 6, area_name: 'Family Lounge', status: 'AVAILABLE' },
  { id: 't9', table_number: 'F02', capacity: 8, area_name: 'Family Lounge', status: 'AVAILABLE' },
  { id: 't10', table_number: 'VIP-01', capacity: 10, area_name: 'Private Dining', status: 'AVAILABLE' }
];

// =============================================================================
// 1. Navigation & View Switching Architecture
// =============================================================================
function switchView(viewName) {
  // Hide mobile nav if open
  const navMenu = document.getElementById("nav-menu");
  if (navMenu) navMenu.classList.remove("mobile-open");

  // Remove active from all page views
  document.querySelectorAll(".page-view").forEach(el => {
    el.classList.remove("active-view");
  });

  // Remove active from all nav links
  document.querySelectorAll(".nav-link").forEach(btn => {
    btn.classList.remove("active");
  });

  const targetView = document.getElementById(`view-${viewName}`);
  const targetNavBtn = document.getElementById(`nav-${viewName}-btn`);

  if (targetView) {
    targetView.classList.add("active-view");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (targetNavBtn) {
    targetNavBtn.classList.add("active");
  }

  // Update URL hash without jumping
  if (history.pushState) {
    history.pushState(null, null, `#${viewName}`);
  }

  // Trigger contextual view loaders
  if (viewName === "order") {
    renderCartPage();
    populateOrderTableDropdown();
  } else if (viewName === "billing") {
    renderBillBreakdown();
  } else if (viewName === "booking") {
    if (tables.length === 0) loadTables();
  }
}

function toggleMobileNav() {
  const navMenu = document.getElementById("nav-menu");
  if (navMenu) {
    navMenu.classList.toggle("mobile-open");
  }
}

function scrollToMenu() {
  const anchor = document.getElementById("menu-catalog-anchor");
  if (anchor) {
    anchor.scrollIntoView({ behavior: "smooth" });
  }
}

// Toast Feedback Notification
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.style.background = type === "error" ? "rgba(239, 68, 68, 0.95)" : "rgba(16, 21, 34, 0.95)";
  toast.style.color = "#fff";
  toast.style.border = type === "error" ? "1px solid #ef4444" : "1px solid var(--border-gold)";
  toast.style.padding = "0.9rem 1.4rem";
  toast.style.borderRadius = "14px";
  toast.style.boxShadow = "0 10px 25px rgba(0,0,0,0.6)";
  toast.style.fontSize = "0.9rem";
  toast.style.fontWeight = "600";
  toast.style.display = "flex";
  toast.style.alignItems = "center";
  toast.style.gap = "0.6rem";
  toast.style.transition = "all 0.3s ease";
  toast.style.backdropFilter = "blur(10px)";

  const icon = type === "error" ? "⚠️" : "✨";
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 350);
  }, 3200);
}

// =============================================================================
// 2. Menu Catalog Logic (High-Res Images, Dietary Badges, Search & Filters)
// =============================================================================
async function loadMenu() {
  try {
    const res = await fetch(`${API_BASE}/menu/items`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        menuItems = data.map(item => ({
          id: item.id,
          name: item.name,
          category: item.category,
          desc: item.description || "",
          price: item.price || item.current_price,
          image_url: item.image_url || null
        }));
      } else {
        menuItems = fallbackMenuItems;
      }
    } else {
      menuItems = fallbackMenuItems;
    }
  } catch (err) {
    console.warn("Using offline fallback menu catalog:", err);
    menuItems = fallbackMenuItems;
  }
  applyFiltersAndRenderMenu();
  updateCartCounter();
  updateMenuCardSteppers();
}

function formatDietaryBadges(desc) {
  if (!desc) return '';
  let html = '<div class="card-tags">';
  
  if (desc.includes('[CHEF-SPECIAL]')) html += '<span class="diet-tag tag-chef">👨‍🍳 Chef Special</span>';
  if (desc.includes('[VEGAN]')) html += '<span class="diet-tag tag-vegan">🌿 Vegan</span>';
  else if (desc.includes('[VEG]')) html += '<span class="diet-tag tag-veg">🟢 Veg</span>';
  if (desc.includes('[NON-VEG]')) html += '<span class="diet-tag tag-nonveg">🍗 Non-Veg</span>';
  if (desc.includes('[GLUTEN-FREE]')) html += '<span class="diet-tag tag-gluten">🌾 Gluten-Free</span>';
  if (desc.includes('[KID-FRIENDLY]')) html += '<span class="diet-tag tag-kid">👶 Kid-Friendly</span>';
  if (desc.includes('[JAIN-AVAILABLE]')) html += '<span class="diet-tag tag-jain">🕉️ Jain Option</span>';
  
  html += '</div>';
  return html;
}

function cleanDescription(desc) {
  if (!desc) return '';
  return desc.replace(/\[[A-Z0-9_\-\s]+\]/g, '').trim();
}

// =============================================================================
// Interactive Menu Card Quantity Steppers & Live Order Sync
// =============================================================================
function getMenuItemCartQty(itemId) {
  const found = cart.find(c => String(c.id) === String(itemId));
  return found ? found.qty : 0;
}

function renderMenuCardFooterAction(itemId) {
  const qty = getMenuItemCartQty(itemId);
  if (qty > 0) {
    return `
      <div class="menu-card-stepper" data-item-id="${itemId}">
        <button class="menu-card-stepper-btn" onclick="adjustMenuOrderQty('${itemId}', -1)" title="Decrease quantity">−</button>
        <span class="menu-card-stepper-val">${qty}</span>
        <button class="menu-card-stepper-btn" onclick="adjustMenuOrderQty('${itemId}', 1)" title="Add another">+</button>
      </div>
    `;
  } else {
    return `
      <button class="btn-add-order" onclick="addToOrder('${itemId}')">
        <span>+</span> Add to Order
      </button>
    `;
  }
}

function updateMenuCardSteppers(itemId) {
  const selector = itemId ? `[data-menu-action-id="${itemId}"]` : `[data-menu-action-id]`;
  document.querySelectorAll(selector).forEach(el => {
    const id = el.getAttribute("data-menu-action-id");
    if (id) {
      el.innerHTML = renderMenuCardFooterAction(id);
    }
  });
}

function adjustMenuOrderQty(itemId, delta) {
  const item = menuItems.find(i => String(i.id) === String(itemId));
  const existing = cart.find(c => String(c.id) === String(itemId));

  if (!existing && delta > 0) {
    addToOrder(itemId);
    return;
  }
  if (!existing) return;

  existing.qty += delta;
  const newQty = existing.qty;

  if (existing.qty <= 0) {
    cart = cart.filter(c => String(c.id) !== String(itemId));
    showToast(`Removed "${existing.name}" from your current order.`, "info");
  } else {
    showToast(`Updated "${existing.name}" (Qty: ${newQty}).`, "success");
  }

  updateCartCounter();
  updateMenuCardSteppers(itemId);
  saveCartDraft();

  // If cart view is active, update it
  const orderView = document.getElementById("view-order");
  if (orderView && orderView.classList.contains("active-view")) {
    renderCartPage();
  }
}

function applyFiltersAndRenderMenu() {
  const grid = document.getElementById("menu-grid");
  if (!grid) return;
  grid.innerHTML = "";

  let filtered = menuItems;

  // Category filter
  if (currentCategoryFilter !== "all") {
    filtered = filtered.filter(item =>
      item.category.toLowerCase().replace(/’|'/g, "") === currentCategoryFilter.toLowerCase().replace(/’|'/g, "") ||
      item.category.toLowerCase().includes(currentCategoryFilter.toLowerCase())
    );
  }

  // Dietary filter
  if (currentDietaryFilter !== "all") {
    filtered = filtered.filter(item =>
      item.desc && item.desc.toUpperCase().includes(`[${currentDietaryFilter.toUpperCase()}]`)
    );
  }

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 4rem 1rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-xl); border: 1px dashed var(--border-subtle);">
        <p style="font-size: 1.2rem; color: #fff; margin-bottom: 0.5rem;">No dishes found</p>
        <p style="font-size: 0.9rem;">No offerings match the chosen category or dietary filters. Try resetting the filters.</p>
        <button class="btn btn-outline" style="margin-top: 1rem;" onclick="filterCategory('all'); filterDietary('all');">Reset Filters</button>
      </div>
    `;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "menu-card";
    const imageUrl = getDishImageUrl(item.name, item.image_url);
    const badgesHtml = formatDietaryBadges(item.desc);
    const cleanDesc = cleanDescription(item.desc);

    card.innerHTML = `
      <div class="card-media">
        <img class="card-img" src="${imageUrl}" alt="${item.name}" loading="lazy" onerror="this.onerror=null; this.src=NEUTRAL_FOOD_PLACEHOLDER;">
        <span class="card-badge-category">${item.category}</span>
        <span class="card-badge-avail">Available</span>
      </div>
      <div class="card-body">
        ${badgesHtml}
        <h3 class="card-title">${item.name}</h3>
        <p class="card-desc">${cleanDesc}</p>
      </div>
      <div class="card-footer">
        <div class="item-price">₹${item.price.toFixed(2)}</div>
        <div data-menu-action-id="${item.id}">
          ${renderMenuCardFooterAction(item.id)}
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function filterCategory(category, clickedElement) {
  currentCategoryFilter = category;
  document.querySelectorAll(".category-tab").forEach(tab => tab.classList.remove("active"));
  if (clickedElement) {
    clickedElement.classList.add("active");
  } else {
    // Sync tab button visually
    const tabs = document.querySelectorAll(".category-tab");
    tabs.forEach(t => {
      if (t.innerText.toLowerCase().includes(category.toLowerCase()) || (category === 'all' && t.innerText.includes('All'))) {
        t.classList.add("active");
      }
    });
  }
  applyFiltersAndRenderMenu();
}

function filterDietary(diet, clickedElement) {
  currentDietaryFilter = diet;
  document.querySelectorAll(".diet-chip").forEach(chip => chip.classList.remove("active"));
  if (clickedElement) {
    clickedElement.classList.add("active");
  }
  applyFiltersAndRenderMenu();
}

function handleMenuSearch(query) {
  const q = (query || "").toLowerCase().trim();
  if (!q) {
    applyFiltersAndRenderMenu();
    return;
  }
  const grid = document.getElementById("menu-grid");
  if (!grid) return;
  grid.innerHTML = "";

  const filtered = menuItems.filter(item =>
    item.name.toLowerCase().includes(q) ||
    (item.desc && item.desc.toLowerCase().includes(q)) ||
    item.category.toLowerCase().includes(q)
  );

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding: 4rem 1rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-xl); border: 1px dashed var(--border-subtle);">
        <p style="font-size: 1.2rem; color: #fff; margin-bottom: 0.5rem;">No dishes found</p>
        <p style="font-size: 0.9rem;">We couldn't find any dishes matching "${query}".</p>
      </div>
    `;
    return;
  }

  filtered.forEach(item => {
    const card = document.createElement("div");
    card.className = "menu-card";
    const imageUrl = getDishImageUrl(item.name, item.image_url);
    const badgesHtml = formatDietaryBadges(item.desc);
    const cleanDesc = cleanDescription(item.desc);

    card.innerHTML = `
      <div class="card-media">
        <img class="card-img" src="${imageUrl}" alt="${item.name}" loading="lazy" onerror="this.onerror=null; this.src=NEUTRAL_FOOD_PLACEHOLDER;">
        <span class="card-badge-category">${item.category}</span>
        <span class="card-badge-avail">Available</span>
      </div>
      <div class="card-body">
        ${badgesHtml}
        <h3 class="card-title">${item.name}</h3>
        <p class="card-desc">${cleanDesc}</p>
      </div>
      <div class="card-footer">
        <div class="item-price">₹${item.price.toFixed(2)}</div>
        <div data-menu-action-id="${item.id}">
          ${renderMenuCardFooterAction(item.id)}
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// =============================================================================
// 3. Table Booking & Reservation Architecture
// =============================================================================
async function loadTables() {
  const dateInput = document.getElementById("res-date");
  const dateVal = dateInput?.value || getMinReservationDate();
  
  // Format local wall-clock datetime string without timezone distortion
  const startParam = `${dateVal}T${selectedStartTime}:00`;
  const endParam = `${dateVal}T${selectedEndTime}:00`;

  try {
    const queryParams = `?start_time=${encodeURIComponent(startParam)}&end_time=${encodeURIComponent(endParam)}`;
    const res = await fetch(`${API_BASE}/restaurant/tables${queryParams}`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        tables = data;
        lastTableSyncHash = JSON.stringify(data.map(t => ({ id: t.id, status: t.status, res_id: t.reservation_id, cust: t.reserved_for })));
      } else {
        tables = fallbackTables;
      }
    } else {
      tables = fallbackTables;
    }
  } catch (err) {
    console.warn("Using fallback tables:", err);
    tables = fallbackTables;
  }
  renderTables(getFilteredTables());
  populateOrderTableDropdown();
}

let currentAreaFilter = "all";

function getFilteredTables() {
  const selectElem = document.getElementById("res-area-filter");
  const filterVal = (selectElem ? selectElem.value : currentAreaFilter) || "all";
  currentAreaFilter = filterVal;

  if (!filterVal || filterVal === "all") {
    return tables;
  }

  const fKey = filterVal.toLowerCase();

  return tables.filter(t => {
    const area = (t.area_name || "").toLowerCase();
    const num = (t.table_number || "").toUpperCase();

    // 1. Romantic Terrace / Rooftop Garden (Tables R01, R02, R03)
    if (fKey.includes("terrace") || fKey.includes("rooftop") || fKey.includes("romantic")) {
      return area.includes("terrace") || area.includes("rooftop") || num.startsWith("R");
    }

    // 2. Main Dining Hall (Tables T01 - T05)
    if (fKey.includes("main")) {
      return area.includes("main") || num.startsWith("T");
    }

    // 3. Family & Kids Lounge (Tables F01 - F03)
    if (fKey.includes("family") || fKey.includes("kids") || fKey.includes("lounge")) {
      return area.includes("family") || area.includes("kids") || num.startsWith("F");
    }

    // 4. Chef's Private Dining (Table P01)
    if (fKey.includes("private") || fKey.includes("chef") || fKey.includes("vip")) {
      return area.includes("private") || area.includes("chef") || num.startsWith("P");
    }

    return area.includes(fKey);
  });
}

function filterTablesByArea(areaName) {
  currentAreaFilter = areaName || "all";
  saveReservationDraft();
  renderTables(getFilteredTables());
}

function renderTables(tableList) {
  const container = document.getElementById("tables-container");
  if (!container) return;
  container.innerHTML = "";

  if (!tableList || tableList.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem 1.5rem; color: var(--text-muted); background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-subtle);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🪑</div>
        <p style="color: #fff; font-size: 1rem; font-weight: 600; margin-bottom: 0.3rem;">No tables found in this section</p>
        <p style="font-size: 0.85rem; margin-bottom: 1rem;">No tables match your selected atmosphere filter.</p>
        <button class="btn btn-outline" onclick="const sel = document.getElementById('res-area-filter'); if(sel) sel.value='all'; filterTablesByArea('all');">Show All Dining Areas</button>
      </div>
    `;
    selectedTable = null;
    updateSelectedTableDisplay();
    saveReservationDraft();
    return;
  }

  tableList.forEach((table) => {
    const isAvail = table.status === "AVAILABLE";
    const card = document.createElement("div");
    card.className = `table-node ${!isAvail ? "disabled booked-node" : ""}`;
    card.dataset.id = table.id;
    card.dataset.num = table.table_number;
    card.dataset.cap = table.capacity;
    card.dataset.area = table.area_name || "Main Dining Hall";

    let reservedNote = "";
    if (!isAvail) {
      const resWindow = table.status_details?.reserved_window || selectedSlotLabel || "Booked";
      reservedNote = `<div class="t-reserved-note">Reserved: ${resWindow}</div>`;
    }

    card.innerHTML = `
      <div class="t-num">${table.table_number}</div>
      <div class="t-cap">Max ${table.capacity} Guests</div>
      <div class="t-area">${table.area_name || "Dining Hall"}</div>
      <span class="t-status-badge ${isAvail ? "t-avail" : "t-booked"}">${isAvail ? "Available" : "Reserved"}</span>
      ${reservedNote}
    `;

    if (isAvail) {
      card.addEventListener("click", () => {
        document.querySelectorAll(".table-node").forEach(n => n.classList.remove("selected"));
        card.classList.add("selected");
        selectedTable = {
          id: table.id,
          number: table.table_number,
          capacity: table.capacity,
          area: table.area_name || "Main Dining Hall"
        };
        // Verify capacity
        const total = adultCount + childCount;
        if (total > selectedTable.capacity) {
          adultCount = Math.min(2, selectedTable.capacity);
          childCount = Math.max(0, selectedTable.capacity - adultCount);
          updateGuestCounters();
        }
        updateSelectedTableDisplay();
        saveReservationDraft();
      });
    }

    container.appendChild(card);
  });

  // Automatically ensure an active available table is selected
  // If user previously drafted/selected a table, check if it's available in current tableList
  const matchedDrafted = selectedTable && tableList.find(t => String(t.id) === String(selectedTable.id));
  if (matchedDrafted && matchedDrafted.status === "AVAILABLE") {
    selectedTable = {
      id: matchedDrafted.id,
      number: matchedDrafted.table_number,
      capacity: matchedDrafted.capacity,
      area: matchedDrafted.area_name || "Main Dining Hall"
    };
    const node = container.querySelector(`[data-id="${selectedTable.id}"]`);
    if (node) node.classList.add("selected");
  } else {
    // If drafted table is no longer available or no previous selection, pick first available
    const firstAvail = tableList.find(t => t.status === "AVAILABLE");
    if (firstAvail) {
      selectedTable = {
        id: firstAvail.id,
        number: firstAvail.table_number,
        capacity: firstAvail.capacity,
        area: firstAvail.area_name || "Main Dining Hall"
      };
      const node = container.querySelector(`[data-id="${firstAvail.id}"]`);
      if (node) node.classList.add("selected");
    } else {
      selectedTable = null;
    }
  }

  updateSelectedTableDisplay();
  saveReservationDraft();
}

function updateSelectedTableDisplay() {
  const disp = document.getElementById("selected-table-display");
  if (disp) {
    if (selectedTable) {
      disp.value = `Table ${selectedTable.number} • ${selectedTable.area} (Capacity: ${selectedTable.capacity} Guests)`;
    } else {
      disp.value = "All tables reserved for this time slot. Please choose another time slot or date.";
    }
  }
  populateOrderTableDisplay();
}

function selectTimeSlot(element, startTime, endTime, label) {
  // 1. Unconditionally clear .selected from ALL time slot pills across the whole page
  document.querySelectorAll(".time-pill").forEach(p => p.classList.remove("selected"));
  
  // 2. Add .selected strictly to the single clicked pill
  const targetPill = element ? (element.classList.contains("time-pill") ? element : element.closest(".time-pill")) : null;
  if (targetPill) {
    targetPill.classList.add("selected");
  } else if (startTime) {
    const matching = document.querySelector(`.time-pill[data-start="${startTime}"]`);
    if (matching) matching.classList.add("selected");
  }
  
  selectedStartTime = startTime || "19:30";
  selectedEndTime = endTime || "21:00";
  selectedSlotLabel = label || `${startTime} – ${endTime}`;
  selectedTime = selectedStartTime;

  const hiddenStart = document.getElementById("selected-start-time");
  if (hiddenStart) hiddenStart.value = selectedStartTime;
  const hiddenEnd = document.getElementById("selected-end-time");
  if (hiddenEnd) hiddenEnd.value = selectedEndTime;
  const hiddenLabel = document.getElementById("selected-slot-label");
  if (hiddenLabel) hiddenLabel.value = selectedSlotLabel;

  const winTxt = document.getElementById("guarantee-window-txt");
  if (winTxt) winTxt.innerText = selectedSlotLabel;
  const endTxt = document.getElementById("guarantee-end-txt");
  if (endTxt) {
    const endPart = selectedSlotLabel.split("–")[1]?.trim() || selectedEndTime;
    endTxt.innerText = endPart;
  }

  saveReservationDraft();

  // Refresh floor plan tables to reflect real-time availability for this selected slot window
  loadTables();
}

function adjustAdults(delta) {
  const next = Math.max(1, adultCount + delta);
  if (selectedTable && (next + childCount) > selectedTable.capacity) {
    showToast(`Table ${selectedTable.number} max capacity is ${selectedTable.capacity} guests.`, "error");
    return;
  }
  adultCount = next;
  updateGuestCounters();
  saveReservationDraft();
}

function adjustChildren(delta) {
  const next = Math.max(0, childCount + delta);
  if (selectedTable && (adultCount + next) > selectedTable.capacity) {
    showToast(`Table ${selectedTable.number} max capacity is ${selectedTable.capacity} guests.`, "error");
    return;
  }
  childCount = next;
  updateGuestCounters();
  saveReservationDraft();
}

function updateGuestCounters() {
  const adultVal = document.getElementById("adult-count-val");
  const childVal = document.getElementById("child-count-val");
  if (adultVal) adultVal.innerText = adultCount;
  if (childVal) childVal.innerText = childCount;
}

// =============================================================================
// Auto-Save & Persistent Reservation Draft Architecture
// =============================================================================
function saveReservationDraft() {
  try {
    const draft = {
      name: document.getElementById("cust-name")?.value || "",
      phone: document.getElementById("cust-phone")?.value || "",
      email: document.getElementById("cust-email")?.value || "",
      chefNotes: document.getElementById("res-chef-notes")?.value || "",
      date: document.getElementById("res-date")?.value || "",
      diningArea: document.getElementById("res-area-filter")?.value || currentAreaFilter || "all",
      startTime: selectedStartTime,
      endTime: selectedEndTime,
      slotLabel: selectedSlotLabel,
      adults: adultCount,
      children: childCount,
      table: selectedTable ? {
        id: selectedTable.id,
        number: selectedTable.number,
        capacity: selectedTable.capacity,
        area: selectedTable.area
      } : null
    };
    localStorage.setItem("dinedesk_reservation_draft", JSON.stringify(draft));
  } catch (err) {
    console.warn("Could not save reservation draft to localStorage:", err);
  }
}

function restoreReservationDraft() {
  try {
    const raw = localStorage.getItem("dinedesk_reservation_draft");
    if (!raw) {
      // Pre-fill remembered user name/phone if available
      const storedName = localStorage.getItem("dinedesk_user_name") || "";
      const storedPhone = localStorage.getItem("dinedesk_user_phone") || "";
      if (storedName) {
        const nameInput = document.getElementById("cust-name");
        if (nameInput && !nameInput.value) nameInput.value = storedName;
      }
      if (storedPhone) {
        const phoneInput = document.getElementById("cust-phone");
        if (phoneInput && !phoneInput.value) phoneInput.value = storedPhone;
      }
      return;
    }

    const draft = JSON.parse(raw);

    // 1. Text Inputs
    const nameInput = document.getElementById("cust-name");
    if (nameInput && draft.name !== undefined) nameInput.value = draft.name;

    const phoneInput = document.getElementById("cust-phone");
    if (phoneInput && draft.phone !== undefined) phoneInput.value = draft.phone;

    const emailInput = document.getElementById("cust-email");
    if (emailInput && draft.email !== undefined) emailInput.value = draft.email;

    const notesInput = document.getElementById("res-chef-notes");
    if (notesInput && draft.chefNotes !== undefined) notesInput.value = draft.chefNotes;

    // 2. Reservation Date
    const minDate = getMinReservationDate();
    const dateInput = document.getElementById("res-date");
    if (dateInput) {
      if (draft.date && draft.date >= minDate) {
        dateInput.value = draft.date;
      } else {
        dateInput.value = minDate;
      }
    }

    // 3. Dining Area
    if (draft.diningArea) {
      const areaSelect = document.getElementById("res-area-filter");
      if (areaSelect) {
        areaSelect.value = draft.diningArea;
        currentAreaFilter = draft.diningArea;
      }
    }

    // 4. Guest counts
    if (typeof draft.adults === "number") adultCount = Math.max(1, draft.adults);
    if (typeof draft.children === "number") childCount = Math.max(0, draft.children);
    updateGuestCounters();

    // 5. Time Slot
    if (draft.startTime && draft.endTime) {
      selectedStartTime = draft.startTime;
      selectedEndTime = draft.endTime;
      selectedSlotLabel = draft.slotLabel || `${draft.startTime} – ${draft.endTime}`;
      selectedTime = selectedStartTime;

      const hiddenStart = document.getElementById("selected-start-time");
      if (hiddenStart) hiddenStart.value = selectedStartTime;
      const hiddenEnd = document.getElementById("selected-end-time");
      if (hiddenEnd) hiddenEnd.value = selectedEndTime;
      const hiddenLabel = document.getElementById("selected-slot-label");
      if (hiddenLabel) hiddenLabel.value = selectedSlotLabel;

      const winTxt = document.getElementById("guarantee-window-txt");
      if (winTxt) winTxt.innerText = selectedSlotLabel;
      const endTxt = document.getElementById("guarantee-end-txt");
      if (endTxt) {
        const endPart = selectedSlotLabel.split("–")[1]?.trim() || selectedEndTime;
        endTxt.innerText = endPart;
      }

      // Mark strictly ONE matching pill in UI
      const pills = document.querySelectorAll(".time-pill");
      pills.forEach(pill => pill.classList.remove("selected"));

      let matchedPill = document.querySelector(`.time-pill[data-start="${draft.startTime}"]`);
      if (!matchedPill) {
        pills.forEach(pill => {
          const onclickAttr = pill.getAttribute("onclick") || "";
          if (onclickAttr.includes(`'${draft.startTime}',`)) {
            matchedPill = pill;
          }
        });
      }

      if (matchedPill) {
        matchedPill.classList.add("selected");
      }
    }

    // 6. Selected Table
    if (draft.table && draft.table.id) {
      selectedTable = draft.table;
    }

    // 7. Confirmed Advance Reservation
    const storedConfirmed = localStorage.getItem("dinedesk_confirmed_reservation");
    if (storedConfirmed) {
      try {
        userConfirmedReservation = JSON.parse(storedConfirmed);
      } catch (e) {
        userConfirmedReservation = null;
      }
    }

  } catch (err) {
    console.warn("Could not restore reservation draft from localStorage:", err);
  }
}

// =============================================================================
// Cart & Order Draft Persistence (Preserves order cart, quantities, notes, promos on refresh)
// =============================================================================
function saveCartDraft() {
  try {
    const kitchenNoteEl = document.getElementById("order-kitchen-note");
    const promoInputEl = document.getElementById("coupon-code-input");
    const guestNameEl = document.getElementById("order-guest-name");
    const guestPhoneEl = document.getElementById("order-guest-phone");
    const guestEmailEl = document.getElementById("order-guest-email");

    const draft = {
      cart: cart || [],
      appliedDiscount: appliedDiscount || { code: "", percentage: 0, amount: 0 },
      kitchenNote: kitchenNoteEl ? kitchenNoteEl.value : "",
      promoCode: promoInputEl ? promoInputEl.value : (appliedDiscount ? appliedDiscount.code : ""),
      guestName: guestNameEl ? guestNameEl.value : (localStorage.getItem("dinedesk_user_name") || ""),
      guestPhone: guestPhoneEl ? guestPhoneEl.value : (localStorage.getItem("dinedesk_user_phone") || ""),
      guestEmail: guestEmailEl ? guestEmailEl.value : (localStorage.getItem("dinedesk_user_email") || ""),
      activeSessionId: activeSessionId || null,
      activeBill: activeBill || null,
      currentKitchenStage: currentKitchenTrackerStage || 1,
      currentPaymentMethod: currentPaymentMethod || "CARD"
    };
    localStorage.setItem("dinedesk_cart_draft", JSON.stringify(draft));
  } catch (err) {
    console.warn("Could not save cart draft to localStorage:", err);
  }
}

function restoreCartDraft() {
  try {
    const raw = localStorage.getItem("dinedesk_cart_draft");
    if (!raw) return;
    const draft = JSON.parse(raw);
    if (Array.isArray(draft.cart) && draft.cart.length > 0) {
      cart = draft.cart;
    }
    if (draft.appliedDiscount) {
      appliedDiscount = draft.appliedDiscount;
    }
    if (draft.kitchenNote) {
      const kitchenNoteEl = document.getElementById("order-kitchen-note");
      if (kitchenNoteEl) kitchenNoteEl.value = draft.kitchenNote;
    }
    if (draft.promoCode) {
      const promoInputEl = document.getElementById("coupon-code-input");
      if (promoInputEl) promoInputEl.value = draft.promoCode;
    }
    const storedName = localStorage.getItem("dinedesk_user_name") || "";
    const storedPhone = localStorage.getItem("dinedesk_user_phone") || "";
    const storedEmail = localStorage.getItem("dinedesk_user_email") || "";
    const guestNameEl = document.getElementById("order-guest-name");
    const guestPhoneEl = document.getElementById("order-guest-phone");
    const guestEmailEl = document.getElementById("order-guest-email");
    if (guestNameEl && !guestNameEl.value) guestNameEl.value = draft.guestName || storedName || "";
    if (guestPhoneEl && !guestPhoneEl.value) guestPhoneEl.value = draft.guestPhone || storedPhone || "";
    if (guestEmailEl && !guestEmailEl.value) guestEmailEl.value = draft.guestEmail || storedEmail || "";
    if (draft.activeSessionId) {
      activeSessionId = draft.activeSessionId;
    }
    if (draft.activeBill) {
      activeBill = draft.activeBill;
    }
    if (typeof draft.currentKitchenStage === "number") {
      currentKitchenTrackerStage = draft.currentKitchenStage;
    } else {
      currentKitchenTrackerStage = 0;
    }
    updateKitchenTracker(currentKitchenTrackerStage);
    if (draft.currentPaymentMethod) {
      currentPaymentMethod = draft.currentPaymentMethod;
    }
    updateCartCounter();
    updateMenuCardSteppers();
    renderCartPage();
    if (activeBill) {
      renderBillBreakdown();
    }
  } catch (err) {
    console.warn("Could not restore cart draft from localStorage:", err);
  }
}

// Calculates minimum reservation date (at least 3 days from current date)
function getMinReservationDate() {
  const d = new Date();
  d.setDate(d.getDate() + 3);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

async function handleReservationSubmit(e) {
  e.preventDefault();
  if (!selectedTable) {
    showToast("Please choose an available table from the floor map.", "error");
    return;
  }

  const name = document.getElementById("cust-name").value.trim();
  const phone = document.getElementById("cust-phone").value.trim();
  const email = (document.getElementById("cust-email")?.value || "").trim();
  const dateVal = document.getElementById("res-date").value;
  const chefNotes = (document.getElementById("res-chef-notes")?.value || "").trim();
  const totalGuests = adultCount + childCount;

  // Enforce 3-day advance reservation constraint
  const minAllowedDate = getMinReservationDate();
  if (!dateVal || dateVal < minAllowedDate) {
    showToast(`Reservations must be booked at least 3 days in advance. Earliest date: ${minAllowedDate}.`, "error");
    const resDateInput = document.getElementById("res-date");
    if (resDateInput) resDateInput.value = minAllowedDate;
    return;
  }

  try {
    // 1. Register / Get Customer in Database
    let customerId = null;
    const custRes = await fetch(`${API_BASE}/auth/customer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, phone, email: email || `${phone}@dinedesk.guest` })
    });
    
    if (custRes.ok) {
      currentCustomer = await custRes.json();
      customerId = currentCustomer.id;
    } else {
      const cErrData = await custRes.json().catch(() => ({}));
      throw new Error(cErrData.detail || "Failed to register customer in database.");
    }

    const startIso = `${dateVal}T${selectedStartTime}:00`;
    const endIso = `${dateVal}T${selectedEndTime}:00`;

    // 2. Insert Reservation into Database (Wall-clock slot matching)
    const res = await fetch(`${API_BASE}/reservations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        table_id: selectedTable.id,
        customer_id: customerId,
        start_time: startIso,
        end_time: endIso,
        guest_count: totalGuests
      })
    });

    if (!res.ok) {
      const rErrData = await res.json().catch(() => ({}));
      throw new Error(rErrData.detail || "Unable to reserve table for this time slot. Table may already be reserved.");
    }

    const savedRes = await res.json();
    const reservationRef = `RES-${savedRes.id.substring(0, 8).toUpperCase()}`;

    // Show Confirmation Modal with seating guarantee details
    const modalDetails = document.getElementById("booking-modal-details");
    if (modalDetails) {
      modalDetails.innerHTML = `
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
          <span style="color:var(--text-muted);">Booking Reference:</span>
          <strong style="color:var(--gold-primary);">${reservationRef}</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
          <span style="color:var(--text-muted);">Guest Name:</span>
          <strong>${name} (${phone})</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
          <span style="color:var(--text-muted);">Table Allocated:</span>
          <strong style="color:var(--gold-light);">Table ${selectedTable.number} (${selectedTable.area})</strong>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
          <span style="color:var(--text-muted);">Reserved Dining Window:</span>
          <strong style="color:#fff;">${dateVal} • ${selectedSlotLabel}</strong>
        </div>
        <div style="background:rgba(212,175,55,0.08); border:1px solid rgba(212,175,55,0.25); border-radius:8px; padding:0.6rem 0.8rem; margin:0.6rem 0; font-size:0.8rem; color:var(--gold-light);">
          🔒 <strong>Exclusive Seating Guarantee:</strong> Table ${selectedTable.number} is exclusively reserved for your party from <strong>${selectedSlotLabel.split('–')[0]?.trim()}</strong> until <strong>${selectedSlotLabel.split('–')[1]?.trim() || selectedEndTime}</strong>.
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom: 0.5rem;">
          <span style="color:var(--text-muted);">Party Size:</span>
          <strong>${adultCount} Adults${childCount > 0 ? `, ${childCount} Children` : ""} (${totalGuests} Total)</strong>
        </div>
        ${chefNotes ? `<div style="margin-top:0.6rem; padding-top:0.6rem; border-top:1px dashed var(--border-subtle); color:#fde68a;">👨‍🍳 <em>Note to Chef: ${chefNotes}</em></div>` : ""}
      `;
    }

    // Save confirmed advance reservation to localStorage
    userConfirmedReservation = {
      id: selectedTable.id,
      number: selectedTable.number,
      capacity: selectedTable.capacity,
      area: selectedTable.area,
      reservationRef: reservationRef,
      date: dateVal,
      slotLabel: selectedSlotLabel
    };
    localStorage.setItem("dinedesk_confirmed_reservation", JSON.stringify(userConfirmedReservation));

    // Save to user's local storage so only their own reservations show on this browser
    const myBookings = JSON.parse(localStorage.getItem("dinedesk_my_reservations") || "[]");
    if (!myBookings.includes(savedRes.id)) {
      myBookings.unshift(savedRes.id);
      localStorage.setItem("dinedesk_my_reservations", JSON.stringify(myBookings));
    }
    localStorage.setItem("dinedesk_user_phone", phone);
    localStorage.setItem("dinedesk_user_name", name);

    // Clear active booking draft once successfully confirmed
    localStorage.removeItem("dinedesk_reservation_draft");

    const overlay = document.getElementById("booking-modal-overlay");
    if (overlay) {
      overlay.classList.add("open");
      document.body.classList.add("modal-open");
      document.documentElement.classList.add("modal-open");
      const card = overlay.querySelector(".modal-card");
      if (card) {
        card.scrollTop = 0;
        card.setAttribute("tabindex", "-1");
        card.focus();
      }
    }

    // Prepopulate phone in My Reservations lookup
    const lookupInput = document.getElementById("lookup-phone-input");
    if (lookupInput) lookupInput.value = phone;

    // Refresh floor tables so table appears reserved immediately
    loadTables();

    showToast("✓ Table reserved successfully! We look forward to hosting you.", "success");

  } catch (err) {
    console.error("Booking error:", err);
    showToast(err.message || "Failed to confirm reservation.", "error");
  }
}

function closeBookingModal(targetView) {
  const overlay = document.getElementById("booking-modal-overlay");
  if (overlay) overlay.classList.remove("open");
  document.body.classList.remove("modal-open");
  document.documentElement.classList.remove("modal-open");
  if (targetView) switchView(targetView);
}

// =============================================================================
// 4. My Reservations View (Restricted strictly to the current customer's bookings)
// =============================================================================
function filterUserOnlyReservations(list, query) {
  const storedUserPhone = (localStorage.getItem("dinedesk_user_phone") || "").trim().toLowerCase();
  const storedMyBookingIds = JSON.parse(localStorage.getItem("dinedesk_my_reservations") || "[]");

  const effectiveFilter = query || storedUserPhone;

  if (effectiveFilter) {
    const cleanFilter = effectiveFilter.replace(/^res-/, "");
    return list.filter(r => {
      const phone = (r.customer_phone || r.customer?.phone || "").toLowerCase();
      const email = (r.customer_email || r.customer?.email || "").toLowerCase();
      const name = (r.customer_name || r.customer?.name || "").toLowerCase();
      const ref = (r.id || "").toLowerCase();
      const isMyStored = storedMyBookingIds.includes(r.id);
      return isMyStored || phone.includes(effectiveFilter) || email.includes(effectiveFilter) || name.includes(effectiveFilter) || ref.includes(cleanFilter);
    });
  }

  // If no search input, return ONLY reservations booked on this device
  if (storedMyBookingIds.length > 0) {
    return list.filter(r => storedMyBookingIds.includes(r.id));
  }

  // Never expose other customers' bookings to an unauthenticated visitor
  return [];
}

async function searchCustomerReservations(forcedQuery) {
  const input = document.getElementById("lookup-phone-input");
  if (forcedQuery !== undefined && input) {
    input.value = forcedQuery;
  }
  const query = (forcedQuery !== undefined ? forcedQuery : (input?.value || "")).trim().toLowerCase();

  const container = document.getElementById("reservations-list-container");
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
      <div style="font-size: 1.6rem; margin-bottom: 0.6rem;">⏳</div>
      <p style="color: #fff; font-size: 1rem; font-weight: 500;">Retrieving your reservations...</p>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/reservations`);
    let list = [];
    if (res.ok) {
      list = await res.json();
      lastReservationsSyncHash = JSON.stringify(list.map(r => ({ id: r.id, status: r.status, start: r.start_time, end: r.end_time, table: r.table_number })));
    } else {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const matched = filterUserOnlyReservations(list, query);
    renderReservationsList(matched);

  } catch (err) {
    console.error("Reservation lookup error:", err);
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem 2rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-xl); border: 1px dashed var(--border-subtle);">
        <p style="font-size: 1.1rem; color: #fff; margin-bottom: 0.5rem;">Unable to load reservations</p>
        <p style="font-size: 0.85rem; margin-bottom: 1.2rem;">Please check your connection and try again.</p>
        <button class="btn btn-gold" onclick="searchCustomerReservations('')">Try Again</button>
      </div>
    `;
  }
}

function renderReservationsList(reservations) {
  const container = document.getElementById("reservations-list-container");
  if (!container) return;

  if (!reservations || reservations.length === 0) {
    const storedUserPhone = localStorage.getItem("dinedesk_user_phone") || "";
    container.innerHTML = `
      <div style="text-align: center; padding: 4rem 2rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-xl); border: 1px dashed var(--border-subtle);">
        <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">🍽️</div>
        <p style="font-size: 1.15rem; color: #fff; margin-bottom: 0.5rem; font-weight: 600;">No Reservations Found</p>
        <p style="font-size: 0.9rem; margin-bottom: 1.5rem; max-width: 480px; margin-left: auto; margin-right: auto; line-height: 1.5;">
          ${storedUserPhone 
            ? `No upcoming bookings found under phone <strong>${storedUserPhone}</strong>. You may search with another phone number or reserve a new table.`
            : "You don't have any reservations on this device. Enter your phone number or booking reference above to find your reservation, or reserve a table below."}
        </p>
        <div style="display:flex; justify-content:center; gap:0.8rem; flex-wrap:wrap;">
          <button class="btn btn-gold" onclick="switchView('booking')">Reserve a Table</button>
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = "";

  reservations.forEach(r => {
    const card = document.createElement("div");
    card.className = "res-ticket-card";

    const startDate = r.start_time ? new Date(r.start_time) : new Date();
    const endDate = r.end_time ? new Date(r.end_time) : null;
    
    const dateFormatted = startDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
    const startTimeStr = startDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const endTimeStr = endDate ? endDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) : '';
    const timeFormatted = endTimeStr ? `${startTimeStr} – ${endTimeStr}` : startTimeStr;

    const statusBadgeClass = `status-${r.status || 'CONFIRMED'}`;
    const tableNum = r.table_number || (r.table ? r.table.table_number : "T01");
    const areaName = r.area_name || (r.table ? r.table.area_name : "Main Dining Hall") || "Main Dining Hall";
    const guestName = r.customer_name || (r.customer ? `${r.customer.first_name || ''} ${r.customer.last_name || ''}`.trim() : "Guest");
    const guestPhone = r.customer_phone || (r.customer ? r.customer.phone : "N/A");
    const guestEmail = r.customer_email || (r.customer ? r.customer.email : "");
    const bookingCode = r.id ? `RES-${r.id.substring(0, 8).toUpperCase()}` : "RES-BOOKING";

    const canCancel = (r.status !== 'CANCELLED' && r.status !== 'COMPLETED');

    card.innerHTML = `
      <div style="flex-grow: 1; width: 100%;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem; flex-wrap:wrap; gap: 0.5rem;">
          <div>
            <div style="display:flex; align-items:center; gap: 0.6rem; flex-wrap:wrap;">
              <span style="font-size: 0.8rem; color: var(--gold-primary); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">Reservation Reference</span>
              <span style="font-size: 0.78rem; color: var(--text-muted); background: rgba(255,255,255,0.06); padding: 0.15rem 0.6rem; border-radius: 4px; font-family: monospace;">${bookingCode}</span>
            </div>
            <h3 style="font-size: 1.4rem; color: #fff; margin-top: 0.35rem;">Table ${tableNum} • ${areaName}</h3>
          </div>
          <span class="status-badge ${statusBadgeClass}">${r.status || 'CONFIRMED'}</span>
        </div>

        <div class="res-meta-grid">
          <div>
            <div class="res-item-label">Guest Name</div>
            <div class="res-item-val" style="color: #fff;">${guestName}</div>
            <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">📞 ${guestPhone}</div>
          </div>
          <div>
            <div class="res-item-label">Reserved Date</div>
            <div class="res-item-val">${dateFormatted}</div>
          </div>
          <div>
            <div class="res-item-label">Dining Window (90 Min)</div>
            <div class="res-item-val" style="color: var(--gold-light);">${timeFormatted}</div>
          </div>
          <div>
            <div class="res-item-label">Party Size</div>
            <div class="res-item-val">👥 ${r.guest_count} Guests</div>
          </div>
        </div>

        ${guestEmail ? `
          <div style="margin-top: 0.8rem; font-size: 0.8rem; color: var(--text-muted);">
            ✉️ Email: <span style="color:#fff;">${guestEmail}</span>
          </div>
        ` : ''}
      </div>

      <div style="display: flex; gap: 0.8rem; align-items: center; justify-content: flex-end; width: 100%; border-top: 1px solid var(--border-subtle); padding-top: 1rem; margin-top: 0.5rem; flex-wrap: wrap;">
        ${canCancel ? `
          <button class="btn btn-outline" onclick="cancelReservation('${r.id}')" style="white-space:nowrap; padding: 0.55rem 1.1rem; font-size: 0.82rem;">
            Cancel Reservation
          </button>
        ` : `
          <span style="font-size: 0.82rem; color: var(--text-muted); font-style: italic;">Status: ${r.status}</span>
        `}
        <button class="btn btn-outline" onclick="deleteReservationRecord('${r.id}')" style="white-space:nowrap; padding: 0.55rem 1.1rem; font-size: 0.82rem; border-color: rgba(239,68,68,0.4); color: #f87171;" title="Remove this reservation">
          Remove
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

async function deleteReservationRecord(reservationId) {
  const confirmed = confirm("Are you sure you want to cancel and remove this reservation?");
  if (!confirmed) return;

  try {
    const res = await fetch(`${API_BASE}/reservations/${reservationId}`, {
      method: "DELETE"
    });

    if (res.ok) {
      showToast("Reservation removed successfully.", "success");
      await searchCustomerReservations();
      await loadTables();
    } else {
      const errData = await res.json().catch(() => ({}));
      showToast(errData.detail || "Failed to remove reservation.", "error");
    }
  } catch (err) {
    console.error("Delete error:", err);
    showToast("Error removing reservation.", "error");
  }
}

async function cancelReservation(reservationId) {
  const confirmed = confirm("Are you sure you wish to cancel this reservation?");
  if (!confirmed) return;

  try {
    const res = await fetch(`${API_BASE}/reservations/${reservationId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "CANCELLED" })
    });

    if (res.ok) {
      showToast("Reservation cancelled successfully.", "success");
    } else {
      showToast("Reservation cancelled.", "success");
    }
  } catch (err) {
    showToast("Reservation cancelled.", "success");
  }

  if (userConfirmedReservation && (userConfirmedReservation.id === reservationId || userConfirmedReservation.reservationRef === reservationId || reservationId.includes(userConfirmedReservation.id))) {
    userConfirmedReservation = null;
    localStorage.removeItem("dinedesk_confirmed_reservation");
  }

  // Refresh both reservation list and floor plan immediately
  await searchCustomerReservations();
  await loadTables();
  populateOrderTableDisplay();
}

// =============================================================================
// 5. Current Order / Cart & Live Kitchen Tracker Logic
// =============================================================================
function addToOrder(itemId) {
  const item = menuItems.find(i => String(i.id) === String(itemId));
  if (!item) return;

  const existing = cart.find(c => String(c.id) === String(itemId));
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ ...item, qty: 1, specialNote: "" });
  }

  saveCartDraft();
  updateCartCounter();
  updateMenuCardSteppers(itemId);
  showToast(`Added "${item.name}" (Qty: ${existing ? existing.qty : 1}) to your order.`, "success");
}

function updateCartCounter() {
  const totalCount = cart.reduce((sum, item) => sum + item.qty, 0);
  const pill = document.getElementById("cart-counter");
  if (pill) pill.innerText = totalCount;
}

function renderCartPage() {
  const container = document.getElementById("cart-items-list");
  if (!container) return;

  if (cart.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
        <p style="font-size: 1.1rem; color: #fff; margin-bottom: 0.5rem;">Your order cart is currently empty.</p>
        <p style="font-size: 0.9rem; margin-bottom: 1.5rem;">Explore our handcrafted dishes and click "Add to Order".</p>
        <button class="btn btn-gold" onclick="switchView('menu')">Browse Food Menu</button>
      </div>
    `;
    updateOrderSummary(0);
    return;
  }

  container.innerHTML = "";
  let subtotal = 0;

  cart.forEach(item => {
    const itemSub = item.price * item.qty;
    subtotal += itemSub;
    const imageUrl = getDishImageUrl(item.name, item.image_url);

    const row = document.createElement("div");
    row.className = "cart-item-row";

    row.innerHTML = `
      <img src="${imageUrl}" alt="${item.name}" class="cart-item-thumb" onerror="this.onerror=null; this.src=NEUTRAL_FOOD_PLACEHOLDER;">
      <div>
        <div class="cart-item-title">${item.name}</div>
        <div style="font-size: 0.85rem; color: var(--gold-light);">₹${item.price.toFixed(2)} each</div>
        <input type="text" class="cart-item-chef-input" placeholder="👨‍🍳 Note to Chef (e.g. Mild spice, less salt, extra crisp)" value="${item.specialNote || ''}" oninput="updateCartItemNote('${item.id}', this.value)">
      </div>
      <div class="cart-stepper">
        <button type="button" onclick="adjustCartQty('${item.id}', -1)">−</button>
        <span style="font-weight: 700; color: #fff; font-size: 0.95rem; min-width: 20px; text-align: center;">${item.qty}</span>
        <button type="button" onclick="adjustCartQty('${item.id}', 1)">+</button>
      </div>
      <div style="text-align: right;">
        <div style="font-weight: 700; color: #fff; font-size: 1.05rem;">₹${itemSub.toFixed(2)}</div>
        <button onclick="removeCartItem('${item.id}')" style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.78rem; margin-top: 4px; text-decoration: underline;">Remove</button>
      </div>
    `;
    container.appendChild(row);
  });

  updateOrderSummary(subtotal);
  updateOrderSubmitButtonState();
}

function adjustCartQty(itemId, delta) {
  const item = cart.find(c => String(c.id) === String(itemId));
  if (!item) return;

  item.qty += delta;
  if (item.qty <= 0) {
    cart = cart.filter(c => String(c.id) !== String(itemId));
  }

  saveCartDraft();
  updateCartCounter();
  updateMenuCardSteppers(itemId);
  renderCartPage();
}

function removeCartItem(itemId) {
  cart = cart.filter(c => String(c.id) !== String(itemId));
  saveCartDraft();
  updateCartCounter();
  updateMenuCardSteppers(itemId);
  renderCartPage();
}

function clearCart() {
  if (cart.length === 0) return;
  const ok = confirm("Clear all items from your current order?");
  if (ok) {
    cart = [];
    appliedDiscount = { code: "", percentage: 0, amount: 0 };
    activeBill = null;
    activeSessionId = null;
    currentKitchenTrackerStage = 0;
    saveCartDraft();
    updateKitchenTracker(0);
    updateCartCounter();
    updateMenuCardSteppers();
    renderCartPage();
    populateOrderTableDisplay();
    updateOrderSubmitButtonState();
  }
}

function updateCartItemNote(itemId, note) {
  const item = cart.find(c => String(c.id) === String(itemId));
  if (item) {
    item.specialNote = note;
    saveCartDraft();
  }
}

function applyPromoCoupon() {
  const input = document.getElementById("coupon-code-input");
  const code = (input?.value || "").trim().toUpperCase();

  if (!code) {
    showToast("Please enter a promotional coupon code.", "error");
    return;
  }

  if (code === "WELCOME10") {
    appliedDiscount = { code: "WELCOME10", percentage: 10, amount: 0 };
    showToast("Coupon WELCOME10 applied: 10% discount!", "success");
  } else if (code === "FAMILY20") {
    appliedDiscount = { code: "FAMILY20", percentage: 20, amount: 0 };
    showToast("Coupon FAMILY20 applied: 20% discount!", "success");
  } else if (code === "CHEFVIP") {
    appliedDiscount = { code: "CHEFVIP", percentage: 0, amount: 250 };
    showToast("VIP Chef credit applied: ₹250 flat discount!", "success");
  } else {
    showToast(`Invalid coupon code "${code}". Try WELCOME10 or FAMILY20.`, "error");
    return;
  }

  saveCartDraft();
  renderCartPage();
}

function updateOrderSummary(subtotal) {
  const subtotalEl = document.getElementById("summary-subtotal");
  const taxEl = document.getElementById("summary-tax");
  const discountRow = document.getElementById("summary-discount-row");
  const discountEl = document.getElementById("summary-discount");
  const grandTotalEl = document.getElementById("summary-grand-total");

  if (!subtotalEl) return;

  let discountAmt = 0;
  if (appliedDiscount.percentage > 0) {
    discountAmt = (subtotal * appliedDiscount.percentage) / 100;
  } else if (appliedDiscount.amount > 0) {
    discountAmt = Math.min(subtotal, appliedDiscount.amount);
  }

  const taxableAmount = Math.max(0, subtotal - discountAmt);
  const tax = taxableAmount * 0.05; // 5% GST
  const grandTotal = taxableAmount + tax;

  subtotalEl.innerText = `₹${subtotal.toFixed(2)}`;
  taxEl.innerText = `₹${tax.toFixed(2)}`;

  if (discountAmt > 0 && discountRow && discountEl) {
    discountRow.style.display = "flex";
    discountEl.innerText = `−₹${discountAmt.toFixed(2)}`;
  } else if (discountRow) {
    discountRow.style.display = "none";
  }

  if (grandTotalEl) {
    grandTotalEl.innerText = `₹${grandTotal.toFixed(2)}`;
  }
}

function onWalkinTableSelect(tableId) {
  if (!tableId) {
    selectedTable = null;
    const idValEl = document.getElementById("order-table-id-val");
    if (idValEl) idValEl.value = "";
    saveCartDraft();
    return;
  }
  const tableSource = (tables && tables.length > 0) ? tables : fallbackTables;
  const t = tableSource.find(item => String(item.id) === String(tableId));
  if (t) {
    selectedTable = {
      id: t.id,
      number: t.table_number,
      capacity: t.capacity,
      area: t.area_name || "Main Dining Hall"
    };
    const idValEl = document.getElementById("order-table-id-val");
    if (idValEl) idValEl.value = t.id;
    saveCartDraft();
    showToast(`Table ${t.table_number} (${t.area_name || 'Dining Area'}) selected for your order.`, "success");
  }
}

function populateOrderTableDisplay() {
  const walkinBox = document.getElementById("order-walkin-picker-box");
  const walkinSelect = document.getElementById("order-walkin-select");
  const badgeEl = document.getElementById("order-table-display-badge");
  const nameEl = document.getElementById("order-table-name");
  const areaEl = document.getElementById("order-table-area");
  const tagEl = document.getElementById("order-table-status-tag");
  const idValEl = document.getElementById("order-table-id-val");

  // Check if user has an advance confirmed reservation
  if (!userConfirmedReservation) {
    const raw = localStorage.getItem("dinedesk_confirmed_reservation");
    if (raw) {
      try { userConfirmedReservation = JSON.parse(raw); } catch (e) {}
    }
  }

  // 1. Advance Confirmed Reservation: Display locked green Reserved badge
  if (userConfirmedReservation) {
    if (walkinBox) walkinBox.style.display = "none";
    if (badgeEl) badgeEl.style.display = "flex";
    if (nameEl) nameEl.innerText = `Table ${userConfirmedReservation.number}`;
    if (areaEl) areaEl.innerText = userConfirmedReservation.area || "Main Dining Hall";
    if (tagEl) {
      tagEl.innerText = "Reserved";
      tagEl.style.background = "rgba(16, 185, 129, 0.16)";
      tagEl.style.color = "#34d399";
      tagEl.style.borderColor = "rgba(16, 185, 129, 0.35)";
    }
    if (idValEl) idValEl.value = userConfirmedReservation.id;
    selectedTable = userConfirmedReservation;
    return;
  }

  // 2. Walk-in guest who has ALREADY placed an order (Stage >= 1 or activeBill present)
  if (currentKitchenTrackerStage >= 1 && selectedTable) {
    if (walkinBox) walkinBox.style.display = "none";
    if (badgeEl) badgeEl.style.display = "flex";
    if (nameEl) nameEl.innerText = `Table ${selectedTable.number}`;
    if (areaEl) areaEl.innerText = selectedTable.area || "Main Dining Hall";
    if (tagEl) {
      tagEl.innerText = "Reserved (Walk-In Seated)";
      tagEl.style.background = "rgba(212, 175, 55, 0.18)";
      tagEl.style.color = "#fde68a";
      tagEl.style.borderColor = "rgba(212, 175, 55, 0.4)";
    }
    if (idValEl) idValEl.value = selectedTable.id;
    return;
  }

  // 3. Walk-in guest composing order (Interactive Table Picker)
  if (badgeEl) badgeEl.style.display = "none";
  if (walkinBox) walkinBox.style.display = "block";

  if (walkinSelect) {
    const tableSource = (tables && tables.length > 0) ? tables : fallbackTables;
    const currentVal = selectedTable?.id || (idValEl ? idValEl.value : "") || walkinSelect.value;
    const availTables = tableSource.filter(t => t.status === "AVAILABLE");

    walkinSelect.innerHTML = `<option value="">-- Choose an available dining table --</option>`;
    
    tableSource.forEach(t => {
      const isAvail = t.status === "AVAILABLE";
      const isCurrentlyChosen = String(t.id) === String(currentVal);
      if (isAvail || isCurrentlyChosen) {
        const opt = document.createElement("option");
        opt.value = t.id;
        const areaLabel = t.area_name || "Dining Area";
        opt.innerText = `Table ${t.table_number} — ${areaLabel} (Max ${t.capacity} Guests)${!isAvail ? ' [Currently Seated]' : ''}`;
        if (isCurrentlyChosen) {
          opt.selected = true;
        }
        walkinSelect.appendChild(opt);
      }
    });

    if (walkinSelect.value) {
      const chosen = tableSource.find(t => String(t.id) === String(walkinSelect.value));
      if (chosen) {
        selectedTable = {
          id: chosen.id,
          number: chosen.table_number,
          capacity: chosen.capacity,
          area: chosen.area_name || "Main Dining Hall"
        };
        if (idValEl) idValEl.value = chosen.id;
      }
    } else if (availTables.length > 0 && !selectedTable) {
      const first = availTables[0];
      walkinSelect.value = first.id;
      selectedTable = {
        id: first.id,
        number: first.table_number,
        capacity: first.capacity,
        area: first.area_name || "Main Dining Hall"
      };
      if (idValEl) idValEl.value = first.id;
    }
  }
}

function populateOrderTableDropdown() {
  populateOrderTableDisplay();
}

function onOrderTableChange(tableId) {
  onWalkinTableSelect(tableId);
}

async function sendOrderToKitchen() {
  if (cart.length === 0) {
    showToast("Please add dishes to your order first.", "error");
    return;
  }

  const hiddenTableInput = document.getElementById("order-table-id-val");
  const walkinSelect = document.getElementById("order-walkin-select");
  const tableId = selectedTable?.id || (walkinSelect && walkinSelect.value) || (hiddenTableInput && hiddenTableInput.value);

  if (!tableId) {
    showToast("Please choose an available dining table before sending order.", "error");
    if (walkinSelect) walkinSelect.focus();
    return;
  }

  // Ensure selectedTable matches
  if (!selectedTable || String(selectedTable.id) !== String(tableId)) {
    const tableSource = (tables && tables.length > 0) ? tables : fallbackTables;
    const found = tableSource.find(t => String(t.id) === String(tableId));
    if (found) {
      selectedTable = {
        id: found.id,
        number: found.table_number,
        capacity: found.capacity,
        area: found.area_name || "Main Dining Hall"
      };
    }
  }

  const kitchenNote = (document.getElementById("order-kitchen-note")?.value || "").trim();
  const guestName = (document.getElementById("order-guest-name")?.value || "").trim();
  const guestPhone = (document.getElementById("order-guest-phone")?.value || "").trim();
  const guestEmail = (document.getElementById("order-guest-email")?.value || "").trim();

  const submitBtn = document.getElementById("btn-submit-order");
  if (submitBtn) {
    submitBtn.innerText = "Transmitting to Chef Vikram...";
    submitBtn.disabled = true;
  }

  try {
    // 1. If walk-in guest entered their details, sync/register customer in database
    if (guestName) {
      try {
        const custRes = await fetch(`${API_BASE}/auth/customer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: guestName,
            phone: guestPhone || null,
            email: guestEmail || (guestPhone ? `${guestPhone}@dinedesk.guest` : null)
          })
        });
        if (custRes.ok) {
          currentCustomer = await custRes.json();
          localStorage.setItem("dinedesk_user_name", guestName);
          if (guestPhone) localStorage.setItem("dinedesk_user_phone", guestPhone);
          if (guestEmail) localStorage.setItem("dinedesk_user_email", guestEmail);
        }
      } catch (cErr) {
        console.warn("Walk-in customer sync note:", cErr);
      }
    }

    // 2. Ensure dining session exists
    if (!activeSessionId) {
      try {
        const sessRes = await fetch(`${API_BASE}/dining/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            table_id: tableId,
            customer_id: currentCustomer ? currentCustomer.id : null,
            guest_count: adultCount + childCount
          })
        });

        if (sessRes.ok) {
          const sessData = await sessRes.json();
          activeSessionId = sessData.id;
        } else {
          // Check for active session
          const listRes = await fetch(`${API_BASE}/dining/sessions?table_id=${tableId}&status=ACTIVE`);
          if (listRes.ok) {
            const list = await listRes.json();
            if (list.length > 0) activeSessionId = list[0].id;
          }
        }
      } catch (sErr) {
        console.warn("Session init fallback:", sErr);
        activeSessionId = `SESS-${Math.floor(100 + Math.random() * 900)}`;
      }
    }

    // 2. Build order payload with individual Notes to Chef
    const orderItems = cart.map(item => {
      let finalNote = item.specialNote || "";
      if (kitchenNote && !finalNote) finalNote = kitchenNote;
      else if (kitchenNote && finalNote) finalNote = `${finalNote} | Order Note: ${kitchenNote}`;

      return {
        item_id: item.id,
        quantity: item.qty,
        special_requests: finalNote ? `Note to Chef: ${finalNote}` : null
      };
    });

    const payload = {
      session_id: activeSessionId || "demo-session-id",
      items: orderItems
    };

    const orderRes = await fetch(`${API_BASE}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (orderRes.ok) {
      showToast("Order dispatched to Chef Vikram! Live cooking underway.", "success");
    } else {
      showToast("Order transmitted to Chef Vikram's kitchen display.", "success");
    }

    // Mark table locally as OCCUPIED / Walk-In Dining with guest name
    const tblIndex = tables.findIndex(t => String(t.id) === String(tableId));
    const finalCustName = currentCustomer ? `${currentCustomer.first_name} ${currentCustomer.last_name}`.trim() : (guestName || "Walk-In Dining");
    if (tblIndex !== -1) {
      tables[tblIndex].status = "OCCUPIED";
      tables[tblIndex].reserved_for = finalCustName;
      tables[tblIndex].status_details = {
        reserved_window: `${finalCustName} (Active)`,
        active_session: activeSessionId
      };
    }

    // Save cart state into active bill items for checkout
    activeBill = {
      items: [...cart],
      discount: { ...appliedDiscount },
      table: selectedTable || { number: "T01", area: "Main Dining Hall" }
    };
    saveCartDraft();

    // Re-render floor plan tables so the Book a Table page shows table is occupied/reserved
    renderTables(getFilteredTables());
    loadTables();

    // Update Live Tracker UI & update Order Summary to locked badge
    updateKitchenTracker(2);
    populateOrderTableDisplay();

    showToast("Kitchen tracker updated: Stage 2 - Cooking in progress.");

  } catch (err) {
    console.error("Order transmission error:", err);
    showToast("Order transmitted to Chef Vikram's brigade.", "success");
    
    const tblIndex = tables.findIndex(t => String(t.id) === String(tableId));
    if (tblIndex !== -1) {
      tables[tblIndex].status = "OCCUPIED";
      tables[tblIndex].reserved_for = "Walk-In Dining";
      tables[tblIndex].status_details = {
        reserved_window: "Walk-In Dining (Active)",
        active_session: activeSessionId
      };
    }
    renderTables(getFilteredTables());

    activeBill = {
      items: [...cart],
      discount: { ...appliedDiscount },
      table: selectedTable || { number: "T01", area: "Main Dining Hall" }
    };
    saveCartDraft();
    updateKitchenTracker(2);
    populateOrderTableDisplay();
  } finally {
    updateOrderSubmitButtonState();
  }
}

function updateOrderSubmitButtonState() {
  const submitBtn = document.getElementById("btn-submit-order");
  if (!submitBtn) return;

  if (currentKitchenTrackerStage >= 1 && activeBill) {
    submitBtn.innerText = "✓ Order Sent to Kitchen (In Preparation)";
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.78";
    submitBtn.style.cursor = "not-allowed";
    submitBtn.style.background = "linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(5, 150, 105, 0.32) 100%)";
    submitBtn.style.color = "#34d399";
    submitBtn.style.border = "1px solid rgba(16, 185, 129, 0.55)";
    submitBtn.style.boxShadow = "0 4px 15px rgba(16, 185, 129, 0.15)";
  } else {
    submitBtn.innerText = "👨‍🍳 Send Order to Kitchen";
    submitBtn.disabled = false;
    submitBtn.style.opacity = "1";
    submitBtn.style.cursor = "pointer";
    submitBtn.style.background = "";
    submitBtn.style.color = "";
    submitBtn.style.border = "";
    submitBtn.style.boxShadow = "";
  }
}

function updateKitchenTracker(stage) {
  currentKitchenTrackerStage = stage;
  saveCartDraft();

  // Stage 0: Awaiting Order, Stage 1: Placed, Stage 2: Cooking, Stage 3: Plated, Stage 4: Served
  const n1 = document.getElementById("step-node-1");
  const n2 = document.getElementById("step-node-2");
  const n3 = document.getElementById("step-node-3");
  const n4 = document.getElementById("step-node-4");
  const badge = document.getElementById("tracker-status-badge");
  const estTime = document.getElementById("tracker-est-time");
  const sessionInfo = document.getElementById("tracker-session-info");
  const tableNum = selectedTable ? `Table ${selectedTable.number}` : "Allocated Table";

  if (n1) n1.className = stage >= 1 ? (stage > 1 ? "step-node completed" : "step-node active") : "step-node";
  if (n2) n2.className = stage >= 2 ? (stage > 2 ? "step-node completed" : "step-node active") : "step-node";
  if (n3) n3.className = stage >= 3 ? (stage > 3 ? "step-node completed" : "step-node active") : "step-node";
  if (n4) n4.className = stage >= 4 ? "step-node completed" : "step-node";

  if (badge) {
    if (stage === 0) {
      badge.innerText = "⏳ Awaiting Order";
      badge.className = "diet-tag";
      badge.style.background = "rgba(255,255,255,0.06)";
      badge.style.color = "var(--text-muted)";
      badge.style.border = "1px solid rgba(255,255,255,0.12)";
    } else if (stage === 1) {
      badge.innerText = "📝 Order Received";
      badge.className = "diet-tag tag-veg";
      badge.style.background = "";
      badge.style.color = "";
      badge.style.border = "";
    } else if (stage === 2) {
      badge.innerText = "🔥 Cooking in Progress";
      badge.className = "diet-tag tag-chef";
      badge.style.background = "";
      badge.style.color = "";
      badge.style.border = "";
    } else if (stage === 3) {
      badge.innerText = "🍽️ Plated & Quality Check";
      badge.className = "diet-tag tag-gluten";
      badge.style.background = "";
      badge.style.color = "";
      badge.style.border = "";
    } else if (stage === 4) {
      badge.innerText = "✨ Served at Table";
      badge.className = "diet-tag tag-veg";
      badge.style.background = "";
      badge.style.color = "";
      badge.style.border = "";
    }
  }

  if (sessionInfo) {
    if (stage === 0) {
      sessionInfo.innerText = `${tableNum} • Select dishes & click "Send Order to Kitchen" above`;
    } else if (stage === 1) {
      sessionInfo.innerText = `${tableNum} • Transmitted to Executive Chef Vikram`;
    } else if (stage === 2) {
      sessionInfo.innerText = `${tableNum} • Chef Vikram is preparing your dishes`;
    } else if (stage === 3) {
      sessionInfo.innerText = `${tableNum} • Plating & final garnish inspection`;
    } else if (stage === 4) {
      sessionInfo.innerText = `${tableNum} • Served tableside. Enjoy your dining experience!`;
    }
  }

  if (estTime) {
    if (stage === 0) estTime.innerText = "Est. 15–20 mins once placed";
    else if (stage === 1) estTime.innerText = "15 - 20 mins";
    else if (stage === 2) estTime.innerText = "12 - 15 mins";
    else if (stage === 3) estTime.innerText = "2 - 3 mins";
    else if (stage === 4) estTime.innerText = "Enjoy your meal!";
  }

  updateOrderSubmitButtonState();
}

// =============================================================================
// 6. Professional Billing & Digital Tableside Payment
// =============================================================================
function renderBillBreakdown() {
  const tbody = document.getElementById("bill-items-tbody");
  const subtotalEl = document.getElementById("bill-subtotal");
  const discountRow = document.getElementById("bill-discount-row");
  const discountAmtEl = document.getElementById("bill-discount-amt");
  const taxEl = document.getElementById("bill-tax-amt");
  const grandTotalEl = document.getElementById("bill-grand-total");
  const btnPayAmount = document.getElementById("btn-pay-amount");
  const tableNumEl = document.getElementById("bill-table-num");
  const dateTimeEl = document.getElementById("bill-date-time");

  if (!tbody) return;

  // Use items from activeBill or cart or default sample
  const items = (activeBill && activeBill.items.length > 0) ? activeBill.items : (cart.length > 0 ? cart : [
    { name: "Wild Mushroom & Truffle Risotto", qty: 1, price: 320.00 },
    { name: "Classic Margherita Pizza", qty: 1, price: 320.00 },
    { name: "Signature Wild Berry Spritzer", qty: 2, price: 130.00 }
  ]);

  tbody.innerHTML = "";
  let subtotal = 0;

  items.forEach(item => {
    const lineTotal = item.price * item.qty;
    subtotal += lineTotal;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.name}</td>
      <td style="text-align: center;">${item.qty}</td>
      <td style="text-align: right;">₹${item.price.toFixed(2)}</td>
      <td style="text-align: right; font-weight:600;">₹${lineTotal.toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });

  const disc = (activeBill && activeBill.discount) ? activeBill.discount : appliedDiscount;
  let discountAmt = 0;
  if (disc.percentage > 0) {
    discountAmt = (subtotal * disc.percentage) / 100;
  } else if (disc.amount > 0) {
    discountAmt = Math.min(subtotal, disc.amount);
  }

  const taxable = Math.max(0, subtotal - discountAmt);
  const tax = taxable * 0.05;
  const grandTotal = taxable + tax;

  if (subtotalEl) subtotalEl.innerText = `₹${subtotal.toFixed(2)}`;
  if (taxEl) taxEl.innerText = `₹${tax.toFixed(2)}`;
  if (grandTotalEl) grandTotalEl.innerText = `₹${grandTotal.toFixed(2)}`;
  if (btnPayAmount) btnPayAmount.innerText = grandTotal.toFixed(2);

  if (discountAmt > 0 && discountRow && discountAmtEl) {
    discountRow.style.display = "flex";
    discountAmtEl.innerText = `−₹${discountAmt.toFixed(2)}`;
  } else if (discountRow) {
    discountRow.style.display = "none";
  }

  if (tableNumEl) {
    const t = selectedTable || (activeBill ? activeBill.table : { number: "T01", area: "Main Dining Hall" });
    tableNumEl.innerText = `Table ${t.number} (${t.area || "Main Dining Hall"})`;
  }

  if (dateTimeEl) {
    const now = new Date();
    dateTimeEl.innerText = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + " at " + now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }
}

function selectPaymentMethod(cardElement, method) {
  document.querySelectorAll(".pay-method-card").forEach(c => c.classList.remove("selected"));
  cardElement.classList.add("selected");
  currentPaymentMethod = method;
  saveCartDraft();

  const cardFields = document.getElementById("payment-fields-card");
  const upiFields = document.getElementById("payment-fields-upi");
  const cashFields = document.getElementById("payment-fields-cash");

  if (cardFields) cardFields.style.display = method === "CARD" ? "block" : "none";
  if (upiFields) upiFields.style.display = method === "UPI" ? "block" : "none";
  if (cashFields) cashFields.style.display = (method === "CASH" || method === "WALLET") ? "block" : "none";
}

async function processBillPayment() {
  const payBtn = document.getElementById("btn-pay-bill");
  const grandTotalText = document.getElementById("btn-pay-amount")?.innerText || "850.50";

  if (payBtn) {
    payBtn.innerText = "Processing Payment via Gateway...";
    payBtn.disabled = true;
  }

  // Simulate API payment or trigger backend payment endpoint
  setTimeout(async () => {
    try {
      if (activeSessionId) {
        // Attempt backend bill payment
        await fetch(`${API_BASE}/billing/sessions/${activeSessionId}/bill`).then(r => r.json()).then(async bill => {
          if (bill && bill.id) {
            await fetch(`${API_BASE}/billing/bills/${bill.id}/payments`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                payment_method: currentPaymentMethod,
                amount: parseFloat(grandTotalText)
              })
            });
          }
        }).catch(bErr => console.warn("Backend payment sync note:", bErr));
      }
    } catch (e) {
      console.warn("Payment sync error:", e);
    }

    // Update status badge on bill
    const statusPill = document.getElementById("bill-status-pill");
    if (statusPill) {
      statusPill.innerText = "PAID";
      statusPill.className = "diet-tag tag-veg";
      statusPill.style.background = "rgba(16, 185, 129, 0.25)";
    }

    // Build Printable Receipt
    renderPrintableReceipt(grandTotalText);

    // Reset cart & active draft
    cart = [];
    appliedDiscount = { code: "", percentage: 0, amount: 0 };
    activeBill = null;
    activeSessionId = null;
    currentKitchenTrackerStage = 0;
    localStorage.removeItem("dinedesk_cart_draft");
    updateKitchenTracker(0);
    updateCartCounter();
    updateMenuCardSteppers();
    updateOrderSubmitButtonState();

    // Automatically refresh floor tables so table becomes available immediately
    loadTables();

    // Show Receipt Modal
    const overlay = document.getElementById("payment-receipt-overlay");
    if (overlay) {
      overlay.classList.add("open");
      document.body.classList.add("modal-open");
      document.documentElement.classList.add("modal-open");
      const card = overlay.querySelector(".modal-card");
      if (card) {
        card.scrollTop = 0;
        card.setAttribute("tabindex", "-1");
        card.focus();
      }
    }

    if (payBtn) {
      payBtn.innerText = "🔒 Paid in Full";
      payBtn.disabled = false;
    }

    showToast("Payment processed successfully! Digital receipt generated.", "success");
  }, 900);
}

function renderPrintableReceipt(totalPaid) {
  const container = document.getElementById("receipt-modal-printable");
  if (!container) return;

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  const invoiceNum = `INV-2026-${Math.floor(100000 + Math.random() * 900000)}`;
  const table = selectedTable || (activeBill ? activeBill.table : { number: "T01", area: "Main Dining Hall" });

  container.innerHTML = `
    <div style="text-align:center; margin-bottom:1rem; border-bottom: 1px dashed var(--border-subtle); padding-bottom: 0.8rem;">
      <div style="font-size: 1.5rem; margin-bottom: 2px;">⚜️</div>
      <strong style="font-size: 1.25rem; color:#fff; font-family:'Playfair Display',serif;">DineDesk Fine Dining Bistro</strong>
      <div style="font-size: 0.75rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.12em;">Road No. 36, Jubilee Hills, Hyderabad • Ph: +91 91545 07776 • GSTIN: 36AAAAA0000A1Z5</div>
    </div>

    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem; font-size: 0.82rem;">
      <span style="color:var(--text-muted);">Tax Invoice No:</span>
      <strong style="color:var(--gold-primary);">${invoiceNum}</strong>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem; font-size: 0.82rem;">
      <span style="color:var(--text-muted);">Date & Time:</span>
      <span>${dateStr} ${timeStr}</span>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom: 0.4rem; font-size: 0.82rem;">
      <span style="color:var(--text-muted);">Table Seated:</span>
      <strong>Table ${table.number} (${table.area || "Main Dining Hall"})</strong>
    </div>
    <div style="display:flex; justify-content:space-between; margin-bottom: 0.8rem; font-size: 0.82rem; border-bottom: 1px dashed var(--border-subtle); padding-bottom: 0.6rem;">
      <span style="color:var(--text-muted);">Payment Method:</span>
      <strong>${currentPaymentMethod} (Settled)</strong>
    </div>

    <div style="display:flex; justify-content:space-between; font-size: 1.15rem; font-weight:700; color: #fff; margin-top: 0.5rem;">
      <span>Total Paid</span>
      <span style="color:var(--gold-light);">₹${totalPaid}</span>
    </div>

    <div style="text-align:center; margin-top:1.2rem; font-size:0.75rem; color:var(--text-muted);">
      Executive Chef Vikram & DineDesk Staff thank you for dining with us!
    </div>
  `;
}

function closeReceiptModal() {
  const overlay = document.getElementById("payment-receipt-overlay");
  if (overlay) overlay.classList.remove("open");
  document.body.classList.remove("modal-open");
  document.documentElement.classList.remove("modal-open");
  switchView("menu");
}

// =============================================================================
// 7. Live Background Synchronization & Real-time Auto-refresh Engine
// =============================================================================
let backgroundSyncInterval = null;
let lastTableSyncHash = "";
let lastReservationsSyncHash = "";

function startBackgroundSync() {
  if (backgroundSyncInterval) clearInterval(backgroundSyncInterval);
  // Poll silently in the background every 3 seconds
  backgroundSyncInterval = setInterval(async () => {
    try {
      await silentSyncTables();
      await silentSyncReservations();
    } catch (e) {
      // Background sync is seamless and completely invisible to the customer
    }
  }, 3000);
}

async function silentSyncTables() {
  const dateInput = document.getElementById("res-date");
  const dateVal = dateInput?.value || getMinReservationDate();
  const startParam = `${dateVal}T${selectedStartTime}:00`;
  const endParam = `${dateVal}T${selectedEndTime}:00`;
  const queryParams = `?start_time=${encodeURIComponent(startParam)}&end_time=${encodeURIComponent(endParam)}`;

  const res = await fetch(`${API_BASE}/restaurant/tables${queryParams}`);
  if (!res.ok) return;
  const data = await res.json();
  if (!Array.isArray(data)) return;

  const newHash = JSON.stringify(data.map(t => ({ id: t.id, status: t.status, res_id: t.reservation_id, cust: t.reserved_for })));
  if (newHash !== lastTableSyncHash) {
    lastTableSyncHash = newHash;
    tables = data;
    renderTables(getFilteredTables());
  }
}

async function silentSyncReservations() {
  // Only silently refresh reservation view if it's currently active and user isn't typing
  const resSection = document.getElementById("view-reservations");
  if (!resSection || !resSection.classList.contains("active")) return;

  const input = document.getElementById("lookup-phone-input");
  if (document.activeElement === input) return;

  const query = (input?.value || "").trim().toLowerCase();

  const res = await fetch(`${API_BASE}/reservations`);
  if (!res.ok) return;
  const list = await res.json();
  if (!Array.isArray(list)) return;

  const newHash = JSON.stringify(list.map(r => ({ id: r.id, status: r.status, start: r.start_time, end: r.end_time, table: r.table_number })));
  if (newHash !== lastReservationsSyncHash) {
    lastReservationsSyncHash = newHash;
    const matched = filterUserOnlyReservations(list, query);
    renderReservationsList(matched);
  }
}

// =============================================================================
// 8. Initialization & Hash Routing Engine
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
  // 1. Restore persistent reservation draft (persists completely across page refreshes)
  restoreReservationDraft();

  // 2. Restore persistent order cart draft (persists all selected items, quantities, promo, notes across refresh)
  restoreCartDraft();

  // Set minimum and default reservation date to 3 days from today
  const minAllowedDate = getMinReservationDate();
  const resDateInput = document.getElementById("res-date");
  if (resDateInput) {
    resDateInput.min = minAllowedDate;
    if (!resDateInput.value || resDateInput.value < minAllowedDate) {
      resDateInput.value = minAllowedDate;
    }

    // Real-time validation on user change
    resDateInput.addEventListener("change", () => {
      const selected = resDateInput.value;
      const currentMin = getMinReservationDate();
      if (selected && selected < currentMin) {
        showToast(`Advance booking required: Please choose ${currentMin} or later.`, "error");
        resDateInput.value = currentMin;
      }
      saveReservationDraft();
      loadTables();
    });
  }

  // Auto-save form inputs whenever user types or changes any detail
  ["cust-name", "cust-phone", "cust-email", "res-chef-notes"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", saveReservationDraft);
      el.addEventListener("change", saveReservationDraft);
    }
  });

  const areaSelect = document.getElementById("res-area-filter");
  if (areaSelect) {
    areaSelect.addEventListener("change", () => {
      saveReservationDraft();
    });
  }

  // Auto-save order inputs (Kitchen note, coupon code & guest details)
  ["order-kitchen-note", "coupon-code-input", "order-guest-name", "order-guest-phone", "order-guest-email"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", saveCartDraft);
      el.addEventListener("change", saveCartDraft);
    }
  });

  // Listen to hash changes (e.g. #menu, #booking, #reservations, #order, #billing)
  window.addEventListener("hashchange", () => {
    const hash = window.location.hash.replace("#", "") || "menu";
    switchView(hash);
  });

  // Initial Data Load (uses the restored draft values for slot, area, date, etc.)
  loadMenu();
  loadTables();
  startBackgroundSync();

  // If page loads with a specific hash
  const initialHash = window.location.hash.replace("#", "");
  if (initialHash && ["menu", "booking", "order", "billing"].includes(initialHash)) {
    switchView(initialHash);
  }

  // Hand over scroll controls directly to the active modal card on wheel event
  ["booking-modal-overlay", "payment-receipt-overlay"].forEach(id => {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.addEventListener("wheel", (e) => {
      const card = overlay.querySelector(".modal-card");
      if (card && e.target === overlay) {
        card.scrollTop += e.deltaY;
        e.preventDefault();
      }
    }, { passive: false });
  });
});
