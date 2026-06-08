// Kraya User Profile & Wishlist Component
import { db } from '../db.js';

let activeTab = 'orders'; // orders, wishlist, settings

export function render(container, params) {
  // If route specified a tab parameter e.g. #profile?tab=wishlist
  if (params.tab) {
    activeTab = params.tab;
  }
  
  const user = db.getCurrentUser();
  const wishlist = db.getWishlist();
  const orders = db.getOrders();
  const addresses = db.getAddresses();
  
  let html = `
    <div class="container">
      <div class="seller-layout">
        
        <!-- Left Sidebar Navigation Menu -->
        <aside class="seller-sidebar">
          <div style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border-light); margin-bottom: 15px;">
            <div style="background-color: rgba(244, 51, 151, 0.08); color: var(--primary-color); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; font-weight: 800; margin: 0 auto 10px auto;">
              ${user.name.charAt(0)}
            </div>
            <h4 style="font-size: 15px; font-weight: 700;">${user.name}</h4>
            <span style="font-size: 11px; color: var(--text-light); font-weight: 500;">Customer & Reseller</span>
          </div>
          
          <button class="seller-menu-item ${activeTab === 'orders' ? 'active' : ''}" data-tab="orders">
            <i data-lucide="package"></i> My Orders
          </button>
          
          <button class="seller-menu-item ${activeTab === 'wishlist' ? 'active' : ''}" data-tab="wishlist">
            <i data-lucide="heart"></i> My Wishlist (${wishlist.length})
          </button>
          
          <button class="seller-menu-item ${activeTab === 'settings' ? 'active' : ''}" data-tab="settings">
            <i data-lucide="settings"></i> Profile & Address
          </button>
        </aside>
        
        <!-- Right Main Panel -->
        <section style="display: flex; flex-direction: column; gap: 20px;">
          
          <!-- Tab Body Content -->
          <div id="profile-tab-content">
            ${renderTabContent(user, wishlist, orders, addresses)}
          </div>
        </section>
        
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  lucide.createIcons();
  
  wireUpProfileEvents(container);
}

function renderTabContent(user, wishlist, orders, addresses) {
  if (activeTab === 'orders') {
    return renderOrdersTab(orders);
  }
  
  if (activeTab === 'wishlist') {
    return renderWishlistTab(wishlist);
  }
  
  if (activeTab === 'settings') {
    return renderSettingsTab(user, addresses);
  }
  
  return '';
}

// Order History View with simulated Multi-stage progress tracking bars
function renderOrdersTab(orders) {
  if (orders.length === 0) {
    return `
      <div style="background-color:#fff; border-radius:12px; border: 1px solid var(--border-light); text-align: center; padding: 60px 20px; color: var(--text-light); display: flex; flex-direction: column; align-items: center; gap: 12px; box-shadow: var(--shadow-sm);">
        <i data-lucide="package" style="width: 48px; height: 48px; stroke-width: 1.5;"></i>
        <p style="font-size: 16px; font-weight: 600; color: var(--text-dark);">No Orders Placed Yet</p>
        <p style="font-size: 13px;">Browse products, select size and add checkout address to track your shipping deliveries here.</p>
        <a href="#catalog" class="supplier-btn" style="text-decoration: none; margin-top: 10px;">Go Shopping</a>
      </div>`;
  }
  
  return `
    <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">Order History & Tracking</h2>
    <div style="display: flex; flex-direction: column; gap: 24px;">
      ${orders.map(order => {
        // Multi-stage progress check
        const stages = ["Ordered", "Shipped", "Out for Delivery", "Delivered"];
        const currentIdx = stages.indexOf(order.status);
        
        return `
          <div style="background-color: #fff; border-radius: 12px; border: 1px solid var(--border-light); overflow: hidden; box-shadow: var(--shadow-sm);">
            
            <!-- Order summary head bar -->
            <div style="background-color: var(--bg-main); padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
              <div style="display: flex; gap: 24px;">
                <div>
                  <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700;">Order ID</span>
                  <strong style="font-size: 14px; display:block; color: var(--primary-color);">${order.orderId}</strong>
                </div>
                <div>
                  <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700;">Date Placed</span>
                  <span style="font-size: 13px; font-weight:600; display:block;">${order.date}</span>
                </div>
                <div>
                  <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700;">Payment Method</span>
                  <span style="font-size: 13px; font-weight:600; display:block;">${order.paymentMethod}</span>
                </div>
              </div>
              <div style="text-align: right;">
                <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700; display:block;">Total Price</span>
                <strong style="font-size: 18px; color: var(--text-dark);">₹${order.totals.finalAmount}</strong>
              </div>
            </div>
            
            <!-- Order Items & Progress details -->
            <div style="padding: 24px;">
              
              <!-- Item list -->
              <div style="display:flex; flex-direction:column; gap:16px; margin-bottom: 24px; border-bottom: 1px dashed var(--border-light); padding-bottom: 20px;">
                ${order.items.map(item => `
                  <div class="d-flex justify-between align-center" style="gap: 12px;">
                    <div class="d-flex align-center gap-2">
                      ${item.image.startsWith('custom:') ? `
                        <div class="procedural-placeholder prod-image-gradient-${item.image.split(':')[1]}" style="width: 50px; height: 50px; border-radius: 6px; position:relative; flex-shrink:0;">
                          <i data-lucide="shirt" style="width: 16px; height: 16px; color:#fff;"></i>
                        </div>
                      ` : `
                        <img src="${item.image}" alt="${item.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; flex-shrink:0;">
                      `}
                      <div>
                        <h4 style="font-size: 13px; font-weight: 700; line-height:1.4;">${item.name}</h4>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Size: <strong>${item.size}</strong> | Qty: <strong>${item.quantity}</strong></div>
                      </div>
                    </div>
                    <div style="font-weight: 700; font-size: 14px;">₹${item.price * item.quantity}</div>
                  </div>
                `).join('')}
              </div>
              
              <!-- Tracking Progress Flow Indicator -->
              <div>
                <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 16px; color: var(--text-muted);">Delivery Status Tracking</h4>
                
                <div class="d-flex justify-between" style="position: relative; margin: 0 40px 10px 40px; align-items: center;">
                  <!-- Connecting horizontal progress line -->
                  <div style="position: absolute; top: 50%; left: 0; transform: translateY(-50%); width: 100%; height: 4px; background-color: var(--border-color); z-index: 1;"></div>
                  <div style="position: absolute; top: 50%; left: 0; transform: translateY(-50%); width: ${(currentIdx / (stages.length - 1)) * 100}%; height: 4px; background-color: var(--success); z-index: 2; transition: width var(--transition-normal);"></div>
                  
                  ${stages.map((st, idx) => {
                    const active = idx <= currentIdx;
                    return `
                      <div class="d-flex flex-column align-center" style="position: relative; z-index: 5;">
                        <div style="background-color: ${active ? 'var(--success)' : '#fff'}; color: ${active ? '#fff' : 'var(--text-light)'}; border: 3px solid ${active ? 'var(--success)' : 'var(--border-color)'}; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700;">
                          ${active ? '✓' : ''}
                        </div>
                        <span style="font-size: 11px; font-weight: ${active ? '700' : '500'}; color: ${active ? 'var(--text-dark)' : 'var(--text-light)'}; margin-top: 6px; white-space: nowrap; position: absolute; top: 28px; transform: translateX(0);">${st}</span>
                      </div>
                    `;
                  }).join('')}
                </div>
                <div style="height: 35px;"></div> <!-- Spacer for absolute positioning labels -->
              </div>
              
              ${order.resellerMargin > 0 ? `
                <div style="background-color: rgba(63, 81, 181, 0.04); padding: 12px; border-radius: 8px; border: 1px solid rgba(63, 81, 181, 0.15); font-size: 12px; font-weight: 700; color: var(--secondary-color); margin-top: 15px;">
                  📈 Reseller Margin to Credit Balance: ₹${order.resellerMargin} (Credited once Order transitions to Delivered)
                </div>` : ''}
              
            </div>
            
          </div>
        `;
      }).join('')}
    </div>`;
}

// Wishlist Grid View
function renderWishlistTab(wishlist) {
  if (wishlist.length === 0) {
    return `
      <div style="background-color:#fff; border-radius:12px; border: 1px solid var(--border-light); text-align: center; padding: 60px 20px; color: var(--text-light); display: flex; flex-direction: column; align-items: center; gap: 12px; box-shadow: var(--shadow-sm);">
        <i data-lucide="heart" style="width: 48px; height: 48px; stroke-width: 1.5;"></i>
        <p style="font-size: 16px; font-weight: 600; color: var(--text-dark);">Your Wishlist is Empty</p>
        <p style="font-size: 13px;">Save your favorite fashion items here by tapping heart icons on catalog images.</p>
        <a href="#catalog" class="supplier-btn" style="text-decoration: none; margin-top: 10px;">Find Products</a>
      </div>`;
  }
  
  const allProducts = db.getProducts();
  const wishlistItems = allProducts.filter(p => wishlist.includes(p.id));
  
  return `
    <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">My Saved Wishlist</h2>
    <div class="product-grid">
      ${wishlistItems.map(p => {
        let imageElement = '';
        if (p.image.startsWith('custom:')) {
          imageElement = `<div class="product-card-img procedural-placeholder prod-image-gradient-${p.image.split(':')[1]}"><i data-lucide="shirt" style="width:36px; height:36px; stroke-width:1.2;"></i></div>`;
        } else {
          imageElement = `<img src="${p.image}" alt="${p.name}" class="product-card-img">`;
        }
        
        return `
          <div class="product-card" data-product-id="${p.id}">
            <div class="card-img-container" onclick="window.location.hash = '#product/${p.id}'">
              ${imageElement}
            </div>
            
            <button class="wishlist-icon-btn liked" data-product-id="${p.id}">
              <i data-lucide="heart" style="width: 18px; height: 18px; fill: currentColor;"></i>
            </button>
            
            <div class="card-info" onclick="window.location.hash = '#product/${p.id}'">
              <h3 class="product-card-title">${p.name}</h3>
              <div class="price-row">
                <span class="card-price">₹${p.price}</span>
                ${p.originalPrice > p.price ? `<span class="card-orig-price">₹${p.originalPrice}</span>` : ''}
              </div>
              <div class="card-rating-row">
                <span class="rating-pill">${p.rating} ★</span>
                <span class="reviews-cnt">${p.reviewsCount} Reviews</span>
              </div>
            </div>
          </div>`;
      }).join('')}
    </div>`;
}

// User Dashboard & Saved Addresses View
function renderSettingsTab(user, addresses) {
  return `
    <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">Profile Settings & Addresses</h2>
    
    <!-- Reseller earnings dashboard cards -->
    <div class="seller-dashboard-stats">
      <div class="stat-card">
        <div class="stat-icon pink"><i data-lucide="wallet"></i></div>
        <div class="stat-info">
          <h3>₹${user.resellerBalance}</h3>
          <p>Total Reseller Balance</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue"><i data-lucide="share-2"></i></div>
        <div class="stat-info">
          <h3>${user.sharedProductsCount}</h3>
          <p>Catalog Items Shared</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i data-lucide="user-check"></i></div>
        <div class="stat-info">
          <h3>Active</h3>
          <p>Reseller Account State</p>
        </div>
      </div>
    </div>
    
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 24px;">
      
      <!-- Profile Card form -->
      <div style="background-color: #fff; border-radius: 12px; border: 1px solid var(--border-light); padding: 24px; box-shadow: var(--shadow-sm); height:fit-content;">
        <h3 style="font-size:16px; font-weight:700; margin-bottom:15px; border-bottom:1px solid var(--border-light); padding-bottom:8px;">Basic Details</h3>
        <form id="profile-edit-form" style="display:flex; flex-direction:column; gap:12px;">
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Full Name</label>
            <input type="text" class="form-control" id="profile-name" value="${user.name}" required>
          </div>
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Email Address</label>
            <input type="email" class="form-control" id="profile-email" value="${user.email}" required>
          </div>
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Mobile Number</label>
            <input type="text" class="form-control" id="profile-phone" value="${user.phone}" maxlength="10" required>
          </div>
          <button type="submit" class="btn-large btn-buy-now" style="padding:10px 20px; font-size:14px; margin-top:10px;">Update Profile</button>
        </form>
      </div>
      
      <!-- Addresses Card list -->
      <div style="background-color: #fff; border-radius: 12px; border: 1px solid var(--border-light); padding: 24px; box-shadow: var(--shadow-sm);">
        <h3 style="font-size:16px; font-weight:700; margin-bottom:15px; border-bottom:1px solid var(--border-light); padding-bottom:8px;">Saved Shipping Addresses</h3>
        <div style="display:flex; flex-direction:column; gap:12px;">
          ${addresses.map((addr, idx) => `
            <div style="border: 1px solid var(--border-color); padding:12px; border-radius:8px; position:relative;">
              <div class="d-flex align-center gap-1">
                <strong style="font-size:13px;">${addr.name}</strong>
                ${addr.isDefault ? `<span style="font-size:9px; background-color:var(--bg-main); color:var(--text-muted); padding:1px 4px; border-radius:2px;">Default</span>` : ''}
              </div>
              <div style="font-size:11px; color: var(--text-muted); margin-top: 4px; line-height: 1.4;">
                ${addr.houseNo}, ${addr.roadName}<br>
                ${addr.city}, ${addr.state} - ${addr.pincode}
              </div>
              
              <button class="action-btn delete-profile-address" data-index="${idx}" style="position:absolute; top:12px; right:12px; color:var(--error);"><i data-lucide="trash-2" style="width:16px; height:16px;"></i></button>
            </div>
          `).join('')}
        </div>
      </div>
      
    </div>`;
}

function wireUpProfileEvents(container) {
  // Tab selector clicking switcher
  container.querySelectorAll(".seller-menu-item").forEach(btn => {
    btn.addEventListener("click", () => {
      container.querySelectorAll(".seller-menu-item").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeTab = btn.dataset.tab;
      
      // Update viewport content
      const contentPane = document.getElementById("profile-tab-content");
      if (contentPane) {
        contentPane.innerHTML = renderTabContent(
          db.getCurrentUser(),
          db.getWishlist(),
          db.getOrders(),
          db.getAddresses()
        );
        lucide.createIcons();
        wireUpTabSpecificEvents(contentPane);
      }
    });
  });
  
  // Setup events on initial tab load
  const contentPane = document.getElementById("profile-tab-content");
  if (contentPane) {
    wireUpTabSpecificEvents(contentPane);
  }
}

function wireUpTabSpecificEvents(contentPane) {
  // Wishlist liking toggle
  contentPane.querySelectorAll(".wishlist-icon-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const prodId = btn.dataset.productId;
      db.toggleWishlist(prodId); // remove since it's already liked
      
      // Update tab content
      const wishlist = db.getWishlist();
      const tabBtn = document.querySelector("[data-tab='wishlist']");
      if (tabBtn) {
        tabBtn.textContent = `My Wishlist (${wishlist.length})`;
      }
      
      contentPane.innerHTML = renderTabContent(
        db.getCurrentUser(),
        wishlist,
        db.getOrders(),
        db.getAddresses()
      );
      lucide.createIcons();
      wireUpTabSpecificEvents(contentPane);
    });
  });
  
  // Profile settings update form submit
  const profileForm = document.getElementById("profile-edit-form");
  if (profileForm) {
    profileForm.addEventListener("submit", (e) => {
      e.preventDefault();
      
      const user = db.getCurrentUser();
      user.name = document.getElementById("profile-name").value.trim();
      user.email = document.getElementById("profile-email").value.trim();
      user.phone = document.getElementById("profile-phone").value.trim();
      
      db.updateCurrentUser(user);
      alert("Profile updated successfully!");
      
      // Re-render header name if any, and current view
      window.location.reload();
    });
  }
  
  // Address deletion
  contentPane.querySelectorAll(".delete-profile-address").forEach(btn => {
    btn.addEventListener("click", () => {
      if (confirm("Are you sure you want to delete this address?")) {
        const idx = Number(btn.dataset.index);
        db.deleteAddress(idx);
        
        // Re-render settings view
        contentPane.innerHTML = renderTabContent(
          db.getCurrentUser(),
          db.getWishlist(),
          db.getOrders(),
          db.getAddresses()
        );
        lucide.createIcons();
        wireUpTabSpecificEvents(contentPane);
      }
    });
  });
}
