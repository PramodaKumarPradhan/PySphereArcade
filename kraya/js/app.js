// Kraya Core Application Controller & Router
import { db } from './db.js';

// Category mapping structure for the Mega Menu
export const CATEGORY_MAP = {
  "Women Ethnic": ["Sarees", "Kurtis", "Suits & Dress Materials", "Lehengas", "Ethnic Jackets"],
  "Women Western": ["Tops", "Dresses", "Jeans", "Skirts", "Nightwear"],
  "Men": ["Shirts", "T-Shirts", "Trousers", "Jeans", "Tracksuits"],
  "Kids": ["Toys & Accessories", "Sets & Suits", "Frocks", "Boys Clothing", "Girls Clothing"],
  "Home & Kitchen": ["Bedsheets", "Kitchen Appliances", "Curtains", "Cushions", "Organizers"],
  "Beauty & Health": ["Makeup", "Skincare", "Haircare", "Fragrances", "Wellness"],
  "Jewellery & Accessories": ["Jewellery Sets", "Rings & Earrings", "Watches", "Sunglasses", "Belts"],
  "Bags & Footwear": ["Bags", "Footwear", "Wallets", "Clutches", "Socks"],
  "Electronics": ["Smartwatches", "Earbuds", "Headphones", "Mobile Accessories", "Power Banks"]
};

// Global App State
export const state = {
  currentRoute: '',
  routeParams: {},
  searchQuery: '',
  filters: {
    category: '',
    subcategory: '',
    priceMin: 0,
    priceMax: 5000,
    rating: 0,
    sizes: []
  },
  sortBy: 'relevance' // relevance, priceAsc, priceDesc, ratingDesc
};

// DOM Elements
let viewport;

// Initialize App
document.addEventListener("DOMContentLoaded", () => {
  db.init();
  viewport = document.getElementById("app-viewport");
  
  // Render Global Components
  renderNavigation();
  updateBadges();
  updateHeaderProfile();
  setupGlobalSearch();
  setupCartDrawer();
  setupUniversalModal();
  
  // Route Navigation
  window.addEventListener("hashchange", handleRouting);
  // Default route if empty
  if (!window.location.hash) {
    window.location.hash = "#catalog";
  } else {
    handleRouting();
  }
  
  // Listener events
  window.addEventListener("kraya_cart_updated", updateBadges);
  window.addEventListener("kraya_wishlist_updated", updateBadges);
  window.addEventListener("kraya_user_updated", () => {
    updateBadges();
    updateHeaderProfile();
  });
  
  // Become a supplier modal trigger
  document.getElementById("header-supplier-btn").addEventListener("click", triggerSupplierLogin);
  
  // Initialize Lucide Icons
  lucide.createIcons();
});

// Mega Menu Render
function renderNavigation() {
  const navContainer = document.getElementById("global-nav-container");
  if (!navContainer) return;
  
  let html = `<ul class="nav-menu container">`;
  
  for (const [cat, subcats] of Object.entries(CATEGORY_MAP)) {
    html += `
      <li class="nav-item">
        <a href="#catalog?category=${encodeURIComponent(cat)}" class="nav-link">${cat}</a>
        <div class="mega-menu">
          <div class="container d-flex gap-3 w-100" style="justify-content: flex-start; padding: 10px 20px;">
    `;
    
    // Group subcategories into logical columns
    const columnsCount = 3;
    const itemsPerCol = Math.ceil(subcats.length / columnsCount);
    
    for (let c = 0; c < columnsCount; c++) {
      const colSubcats = subcats.slice(c * itemsPerCol, (c + 1) * itemsPerCol);
      if (colSubcats.length === 0) continue;
      
      html += `<div style="flex: 1 1 200px;">
        <h5 class="mega-column-title">${cat} Essentials</h5>
        <ul class="mega-list">`;
        
      colSubcats.forEach(sub => {
        html += `
          <li class="mega-list-item">
            <a href="#catalog?category=${encodeURIComponent(cat)}&subcategory=${encodeURIComponent(sub)}" class="mega-list-link">${sub}</a>
          </li>`;
      });
      
      html += `</ul></div>`;
    }
    
    html += `
          </div>
        </div>
      </li>`;
  }
  
  html += `</ul>`;
  navContainer.innerHTML = html;
}

// Update Wishlist and Cart count indicators
export function updateBadges() {
  const cartBadge = document.getElementById("cart-badge");
  const wishlistBadge = document.getElementById("wishlist-badge");
  
  const cartItems = db.getCart();
  const totalCartQty = cartItems.reduce((acc, item) => acc + item.quantity, 0);
  
  if (totalCartQty > 0) {
    cartBadge.textContent = totalCartQty;
    cartBadge.style.display = "block";
  } else {
    cartBadge.style.display = "none";
  }
  
  const wishlist = db.getWishlist();
  if (wishlist.length > 0) {
    wishlistBadge.textContent = wishlist.length;
    wishlistBadge.style.display = "block";
  } else {
    wishlistBadge.style.display = "none";
  }
}

// Update profile text in top navigation bar
function updateHeaderProfile() {
  const profileText = document.getElementById("header-profile-text");
  if (!profileText) return;
  const user = db.getCurrentUser();
  if (user) {
    profileText.textContent = user.name.split(' ')[0]; // first name
  } else {
    profileText.textContent = "Sign In";
  }
}

// Header Search logic with dropdown autocompletion
function setupGlobalSearch() {
  const searchInput = document.getElementById("global-search-input");
  const suggestionsBox = document.getElementById("global-search-suggestions");
  const searchContainer = document.getElementById("global-search-container");
  const clearBtn = document.getElementById("global-search-clear");
  
  if (!searchInput) return;
  
  // Clear input click
  clearBtn.addEventListener("click", () => {
    searchInput.value = '';
    searchContainer.classList.remove("active");
    suggestionsBox.classList.remove("active");
    state.searchQuery = '';
    navigateToRoute('#catalog');
  });

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.trim().toLowerCase();
    
    if (query.length > 0) {
      searchContainer.classList.add("active");
      suggestionsBox.classList.add("active");
      
      const allProducts = db.getProducts();
      const matches = allProducts.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.category.toLowerCase().includes(query) ||
        p.subcategory.toLowerCase().includes(query)
      ).slice(0, 6);
      
      if (matches.length > 0) {
        let suggestionsHtml = '';
        matches.forEach(p => {
          suggestionsHtml += `
            <div class="suggestion-item" data-product-id="${p.id}">
              <i data-lucide="search"></i>
              <div>
                <strong>${p.name}</strong>
                <div style="font-size: 11px; color: var(--text-light);">${p.category} > ${p.subcategory}</div>
              </div>
            </div>`;
        });
        suggestionsBox.innerHTML = suggestionsHtml;
        lucide.createIcons();
        
        // Setup suggestions click listeners
        suggestionsBox.querySelectorAll(".suggestion-item").forEach(item => {
          item.addEventListener("click", () => {
            const prodId = item.dataset.productId;
            suggestionsBox.classList.remove("active");
            searchInput.value = '';
            searchContainer.classList.remove("active");
            window.location.hash = `#product/${prodId}`;
          });
        });
      } else {
        suggestionsBox.innerHTML = `<div style="padding: 16px; font-size: 13px; color: var(--text-muted); text-align: center;">No products found for "${e.target.value}"</div>`;
      }
    } else {
      searchContainer.classList.remove("active");
      suggestionsBox.classList.remove("active");
    }
  });

  // Handle enter key submit
  searchInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      const q = searchInput.value.trim();
      suggestionsBox.classList.remove("active");
      searchInput.blur();
      if (q) {
        navigateToRoute(`#catalog?q=${encodeURIComponent(q)}`);
      }
    }
  });

  // Close suggestions on outside click
  document.addEventListener("click", (e) => {
    if (!searchContainer.contains(e.target)) {
      suggestionsBox.classList.remove("active");
    }
  });
}

// Slide-over cart panel triggers
function setupCartDrawer() {
  const cartBtn = document.getElementById("header-cart-btn");
  const cartOverlay = document.getElementById("cart-drawer-overlay");
  const cartClose = document.getElementById("cart-drawer-close");
  
  if (!cartBtn) return;
  
  cartBtn.addEventListener("click", () => {
    renderCartDrawerList();
    cartOverlay.classList.add("active");
  });
  
  cartClose.addEventListener("click", () => {
    cartOverlay.classList.remove("active");
  });
  
  cartOverlay.addEventListener("click", (e) => {
    if (e.target === cartOverlay) {
      cartOverlay.classList.remove("active");
    }
  });
}

// Renders the list items inside the sidebar drawer
export function renderCartDrawerList() {
  const itemsContainer = document.getElementById("cart-drawer-items-list");
  const footerContainer = document.getElementById("cart-drawer-summary-pane");
  const cartItems = db.getCart();
  
  if (cartItems.length === 0) {
    itemsContainer.innerHTML = `
      <div style="text-align: center; padding: 40px 20px; color: var(--text-light); display: flex; flex-direction: column; align-items: center; gap: 12px;">
        <i data-lucide="shopping-cart" style="width: 48px; height: 48px; stroke-width: 1.5;"></i>
        <p style="font-weight: 600;">Your cart is empty</p>
        <a href="#catalog" class="supplier-btn" style="text-align: center; text-decoration: none; display: inline-block; margin-top: 10px;" onclick="document.getElementById('cart-drawer-overlay').classList.remove('active')">Shop Now</a>
      </div>`;
    footerContainer.innerHTML = '';
    lucide.createIcons();
    return;
  }
  
  let itemsHtml = '';
  let subtotal = 0;
  let originalSubtotal = 0;
  
  cartItems.forEach(item => {
    subtotal += item.price * item.quantity;
    originalSubtotal += item.originalPrice * item.quantity;
    
    // Check if the image is procedural gradient
    let imageElement = '';
    if (item.image && item.image.startsWith('custom:')) {
      const gradientClass = `prod-image-gradient-${item.image.split(':')[1]}`;
      imageElement = `<div class="cart-item-img procedural-placeholder ${gradientClass}"><i data-lucide="shopping-bag" style="width: 24px; height: 24px;"></i></div>`;
    } else {
      imageElement = `<img src="${item.image}" alt="${item.name}" class="cart-item-img">`;
    }
    
    itemsHtml += `
      <div class="cart-item-card">
        ${imageElement}
        <div class="cart-item-details">
          <h4 class="cart-item-name">${item.name}</h4>
          <div class="cart-item-size-qty">Size: <strong>${item.size}</strong></div>
          <div class="d-flex align-center justify-between" style="margin-top: auto;">
            <div class="qty-selector">
              <button class="qty-btn dec-qty" data-id="${item.productId}" data-size="${item.size}">-</button>
              <span class="qty-value">${item.quantity}</span>
              <button class="qty-btn inc-qty" data-id="${item.productId}" data-size="${item.size}">+</button>
            </div>
            <div style="text-align: right;">
              <div style="font-weight: 700; font-size: 15px;">₹${item.price * item.quantity}</div>
              ${item.originalPrice > item.price ? `<div style="font-size: 11px; text-decoration: line-through; color: var(--text-light);">₹${item.originalPrice * item.quantity}</div>` : ''}
            </div>
          </div>
        </div>
      </div>`;
  });
  
  itemsContainer.innerHTML = itemsHtml;
  lucide.createIcons();
  
  // Footer totals and Checkout button
  const savings = originalSubtotal - subtotal;
  footerContainer.innerHTML = `
    <div style="margin-bottom: 15px;">
      <div class="d-flex justify-between" style="margin-bottom: 6px; font-size: 14px; color: var(--text-muted);">
        <span>Cart Subtotal</span>
        <span>₹${subtotal}</span>
      </div>
      ${savings > 0 ? `
      <div class="d-flex justify-between" style="margin-bottom: 6px; font-size: 14px; color: var(--success);">
        <span>Total Discount Savings</span>
        <span>-₹${savings}</span>
      </div>` : ''}
      <div class="d-flex justify-between" style="font-size: 16px; font-weight: 800; border-top: 1px dashed var(--border-color); padding-top: 10px;">
        <span>Final Amount</span>
        <span>₹${subtotal}</span>
      </div>
    </div>
    <button class="btn-large btn-buy-now w-100" id="cart-drawer-checkout-btn">
      Proceed to Checkout <i data-lucide="arrow-right"></i>
    </button>
  `;
  lucide.createIcons();
  
  // Wire up quantity adjusters inside drawer
  itemsContainer.querySelectorAll(".dec-qty").forEach(btn => {
    btn.addEventListener("click", () => {
      const prodId = btn.dataset.id;
      const size = btn.dataset.size;
      const current = cartItems.find(i => i.productId === Number(prodId) && i.size === size);
      if (current) {
        db.updateCartQuantity(prodId, size, current.quantity - 1);
        renderCartDrawerList();
      }
    });
  });
  
  itemsContainer.querySelectorAll(".inc-qty").forEach(btn => {
    btn.addEventListener("click", () => {
      const prodId = btn.dataset.id;
      const size = btn.dataset.size;
      const current = cartItems.find(i => i.productId === Number(prodId) && i.size === size);
      if (current) {
        db.updateCartQuantity(prodId, size, current.quantity + 1);
        renderCartDrawerList();
      }
    });
  });
  
  // Proceed to Checkout
  document.getElementById("cart-drawer-checkout-btn").addEventListener("click", () => {
    document.getElementById("cart-drawer-overlay").classList.remove("active");
    window.location.hash = "#checkout";
  });
}

// Universal Dialog setup (Modal box)
function setupUniversalModal() {
  const modal = document.getElementById("universal-modal");
  
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });
}

export function openModal(htmlContent) {
  const modal = document.getElementById("universal-modal");
  const content = document.getElementById("universal-modal-content");
  
  content.innerHTML = htmlContent;
  modal.classList.add("active");
  lucide.createIcons();
}

export function closeModal() {
  const modal = document.getElementById("universal-modal");
  modal.classList.remove("active");
}

// Supplier Authentications
function triggerSupplierLogin() {
  const modalHtml = `
    <div class="modal-header">
      <h3 class="d-flex align-center gap-1"><i data-lucide="shield-check" style="color: var(--primary-color);"></i> Supplier Portal Login</h3>
      <button onclick="document.getElementById('universal-modal').classList.remove('active')" class="action-btn"><i data-lucide="x"></i></button>
    </div>
    <form id="supplier-login-form">
      <div class="modal-body">
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 20px;">Enter supplier credentials to manage products, add new catalogs, and process reseller orders.</p>
        <div class="form-group">
          <label class="form-label">Seller Email Address</label>
          <input type="email" class="form-control" placeholder="vendor@kraya.com" required value="vendor@kraya.com">
        </div>
        <div class="form-group">
          <label class="form-label">Password</label>
          <input type="password" class="form-control" placeholder="••••••••" required value="seller123">
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn-large btn-cart-add" style="padding: 10px 20px;" onclick="document.getElementById('universal-modal').classList.remove('active')">Cancel</button>
        <button type="submit" class="btn-large btn-buy-now" style="padding: 10px 20px;">Login Panel</button>
      </div>
    </form>
  `;
  openModal(modalHtml);
  
  document.getElementById("supplier-login-form").addEventListener("submit", (e) => {
    e.preventDefault();
    closeModal();
    // Navigate directly to supplier panel
    window.location.hash = "#seller";
  });
}

// Router Logic
function handleRouting() {
  const fullHash = window.location.hash || '#catalog';
  const queryIndex = fullHash.indexOf('?');
  
  let route = queryIndex !== -1 ? fullHash.substring(0, queryIndex) : fullHash;
  let queryStr = queryIndex !== -1 ? fullHash.substring(queryIndex + 1) : '';
  
  // Parse Query Parameters
  const params = {};
  if (queryStr) {
    queryStr.split('&').forEach(pair => {
      const [key, value] = pair.split('=');
      params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    });
  }
  
  state.currentRoute = route;
  state.routeParams = params;
  
  // Highlight active link in header nav matching selected category
  const navLinks = document.querySelectorAll(".nav-link");
  navLinks.forEach(link => {
    const linkUrl = link.getAttribute("href");
    const linkCategory = linkUrl.substring(linkUrl.indexOf("category=") + 9);
    if (params.category && decodeURIComponent(params.category) === decodeURIComponent(linkCategory)) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });

  // Match routes
  if (route === '#catalog') {
    loadComponent('catalog', params);
  } else if (route.startsWith('#product/')) {
    const id = route.substring(9);
    loadComponent('detail', { id });
  } else if (route === '#checkout') {
    if (!db.getCurrentUser()) {
      window.location.hash = '#login';
      return;
    }
    loadComponent('cart', { step: 'checkout' });
  } else if (route === '#profile') {
    if (!db.getCurrentUser()) {
      window.location.hash = '#login';
      return;
    }
    loadComponent('profile', params);
  } else if (route === '#login') {
    loadComponent('login', params);
  } else if (route === '#seller') {
    loadComponent('seller', params);
  } else {
    // Fallback to catalog
    window.location.hash = '#catalog';
  }
}

// Dynamic Component Importer
async function loadComponent(componentName, params) {
  // Show spinner while loading
  viewport.innerHTML = `
    <div class="container d-flex align-center justify-center" style="padding: 100px 0; justify-content: center;">
      <div class="spinner"></div>
    </div>`;
    
  try {
    // Import module dynamically
    const module = await import(`./components/${componentName}.js`);
    
    // Call the rendering method inside the component module
    if (module.render) {
      module.render(viewport, params);
      window.scrollTo(0, 0);
      lucide.createIcons();
    } else {
      viewport.innerHTML = `<div class="container" style="padding: 40px 0; text-align:center; color: var(--error);">Error: render function not found in ${componentName} module.</div>`;
    }
  } catch (error) {
    console.error("Component load failed:", error);
    viewport.innerHTML = `<div class="container" style="padding: 40px 0; text-align:center; color: var(--error);">
      <h3>Could not load page</h3>
      <p style="margin-top: 10px; color: var(--text-muted);">${error.message}</p>
      <button class="supplier-btn" style="margin-top: 20px;" onclick="window.location.reload()">Reload Application</button>
    </div>`;
  }
}

// External Navigation helper
export function navigateToRoute(hash) {
  window.location.hash = hash;
}
