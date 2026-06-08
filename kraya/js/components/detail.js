// Kraya Product Detail Component
import { db } from '../db.js';
import { triggerResellerModal } from './reseller.js';
import { renderCartDrawerList } from '../app.js';

export function render(container, params) {
  const productId = Number(params.id);
  const product = db.getProductById(productId);
  
  if (!product) {
    container.innerHTML = `
      <div class="container" style="padding: 60px 0; text-align: center;">
        <i data-lucide="info" style="width: 48px; height: 48px; color: var(--text-light); stroke-width: 1.5; margin-bottom: 15px;"></i>
        <h2>Product Not Found</h2>
        <p style="color: var(--text-muted); margin-top: 10px;">The product you are trying to view does not exist or has been removed.</p>
        <a href="#catalog" class="supplier-btn" style="text-decoration: none; display: inline-block; margin-top: 20px;">Back to Catalog</a>
      </div>`;
    return;
  }
  
  let selectedSize = product.sizes.length > 0 ? product.sizes[0] : '';
  
  // Custom Gradient Image Check
  let mainImageHtml = '';
  if (product.image.startsWith('custom:')) {
    const gradientClass = `prod-image-gradient-${product.image.split(':')[1]}`;
    mainImageHtml = `<div class="detail-main-img procedural-placeholder ${gradientClass}" style="position: absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center;"><i data-lucide="shirt" style="width: 64px; height: 64px; stroke-width: 1.2;"></i></div>`;
  } else {
    mainImageHtml = `<img src="${product.image}" alt="${product.name}" class="detail-main-img" id="detail-main-img">`;
  }
  
  let html = `
    <div class="container">
      <!-- Breadcrumb -->
      <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 24px; display: flex; align-items: center; gap: 6px;">
        <a href="#catalog" style="hover: color: var(--primary-color);">Home</a>
        <i data-lucide="chevron-right" style="width: 14px; height: 14px;"></i>
        <a href="#catalog?category=${encodeURIComponent(product.category)}" style="hover: color: var(--primary-color);">${product.category}</a>
        <i data-lucide="chevron-right" style="width: 14px; height: 14px;"></i>
        <span style="color: var(--text-dark); font-weight: 500;">${product.name}</span>
      </div>
      
      <!-- Grid details -->
      <div class="detail-layout">
        
        <!-- Left Side Gallery & Action buttons -->
        <div class="detail-gallery">
          <div class="detail-main-img-box" id="detail-zoom-box">
            ${mainImageHtml}
          </div>
          
          ${product.images && product.images.length > 1 && !product.image.startsWith('custom:') ? `
            <div class="detail-thumbs">
              ${product.images.map((img, idx) => `
                <img src="${img}" class="detail-thumb-img ${idx === 0 ? 'active' : ''}" data-index="${idx}">
              `).join('')}
            </div>
          ` : ''}
          
          <div class="detail-actions">
            <button class="btn-large btn-cart-add" id="detail-add-cart-btn">
              <i data-lucide="shopping-cart"></i> Add to Cart
            </button>
            <button class="btn-large btn-buy-now" id="detail-buy-now-btn">
              <i data-lucide="zap"></i> Buy Now
            </button>
          </div>
        </div>
        
        <!-- Right Side details info panel -->
        <div class="detail-info-pane">
          
          <!-- Basic information card -->
          <div class="detail-card">
            <h1 class="detail-product-title">${product.name}</h1>
            
            <div class="detail-price-box">
              <span class="detail-price">₹${product.price}</span>
              ${product.originalPrice > product.price ? `
                <span class="detail-orig-price">₹${product.originalPrice}</span>
                <span class="detail-discount">${product.discount}% off</span>
              ` : ''}
            </div>
            
            <div class="rating-reviews-summary">
              <span class="rating-pill" style="padding: 4px 10px; font-size: 13px;">
                ${product.rating} <i data-lucide="star" style="width: 12px; height: 12px; fill: currentColor;"></i>
              </span>
              <span style="font-size: 13px; color: var(--text-muted); font-weight: 600;">${product.reviewsCount} Ratings, ${product.reviews.length} Reviews</span>
            </div>
            
            <div style="background-color: var(--bg-main); padding: 8px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; width: fit-content; margin-top: 15px; color: var(--text-muted);">
              ${product.freeDelivery ? 'Free Delivery' : '+ ₹40 Delivery charge'}
            </div>
          </div>
          
          <!-- Reseller Banner card -->
          <div class="detail-card share-earn-box">
            <div>
              <h4 style="color: var(--secondary-color); font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 6px;">
                <i data-lucide="hand-coins"></i> Earn Weekly Profit
              </h4>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px; max-width: 320px;">Share this product with custom margin on WhatsApp. We deliver it, you keep the margin!</p>
            </div>
            <button class="share-earn-btn" id="detail-reseller-share-btn">
              <i data-lucide="whatsapp"></i> Share & Earn
            </button>
          </div>
          
          <!-- Size Selector card -->
          <div class="detail-card size-selector-container">
            <h3 style="font-size: 15px; font-weight: 700;">Select Size</h3>
            <div class="size-options">
              ${product.sizes.map(sz => `
                <button class="size-option-btn ${sz === selectedSize ? 'selected' : ''}" data-size="${sz}">${sz}</button>
              `).join('')}
            </div>
          </div>
          
          <!-- Delivery Checker card -->
          <div class="detail-card">
            <h3 style="font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 8px;">
              <i data-lucide="map-pin" style="color: var(--primary-color);"></i> Delivery & Pincode Check
            </h3>
            <div class="pincode-input-box">
              <input type="text" class="pincode-input" id="detail-pincode-input" placeholder="Enter Pincode (e.g. 751001)" maxlength="6">
              <button class="pincode-btn" id="detail-pincode-btn">Check</button>
            </div>
            <div class="pincode-result" id="detail-pincode-result"></div>
          </div>
          
          <!-- Product Specification details card -->
          <div class="detail-card">
            <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 15px; border-bottom: 1px solid var(--border-light); padding-bottom: 8px;">Product Specifications</h3>
            
            <div style="display: grid; grid-template-columns: 150px 1fr; gap: 12px; font-size: 13px;">
              ${Object.entries(product.details).map(([key, val]) => `
                <span style="color: var(--text-muted); font-weight: 500;">${key}</span>
                <span style="color: var(--text-dark); font-weight: 600;">${val}</span>
              `).join('')}
            </div>
            
            <h4 style="font-size: 14px; font-weight: 700; margin-top: 24px; margin-bottom: 8px;">Description</h4>
            <p style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">${product.description}</p>
          </div>
          
          <!-- Seller Information card -->
          <div class="detail-card d-flex align-center justify-between" style="padding: 16px 24px;">
            <div>
              <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-light); font-weight: 700;">Seller / Shop</div>
              <h4 style="font-size: 16px; font-weight: 700; margin-top: 2px;">${product.seller.name}</h4>
              <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px; display:flex; align-items:center; gap: 10px;">
                <span class="rating-pill" style="font-size: 10px; padding: 1px 5px;">${product.seller.rating} ★</span>
                <span>${product.seller.followers} Followers</span>
                <span>${product.seller.productCount} Products</span>
              </div>
            </div>
            <button class="supplier-btn" style="padding: 6px 14px; font-size: 12px;" onclick="window.location.hash='#catalog?seller=${encodeURIComponent(product.seller.name)}'">Visit Shop</button>
          </div>
          
          <!-- Reviews list card -->
          <div class="detail-card">
            <h3 style="font-size: 15px; font-weight: 700; margin-bottom: 15px; border-bottom: 1px solid var(--border-light); padding-bottom: 8px;">Customer Reviews</h3>
            
            ${product.reviews.length === 0 ? `
              <p style="font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0;">No reviews yet for this product. Be the first to buy and write a review!</p>
            ` : `
              <div style="display: flex; flex-direction: column; gap: 20px;">
                ${product.reviews.map(rev => `
                  <div style="border-bottom: 1px solid var(--border-light); padding-bottom: 12px;">
                    <div class="d-flex align-center justify-between" style="margin-bottom: 6px;">
                      <div class="d-flex align-center gap-1">
                        <div class="rating-pill" style="font-size: 10px; padding: 1px 5px;">
                          ${rev.rating} <i data-lucide="star" style="width: 8px; height: 8px; fill: currentColor;"></i>
                        </div>
                        <span style="font-size: 13px; font-weight: 700; margin-left: 6px;">${rev.name}</span>
                      </div>
                      <span style="font-size: 11px; color: var(--text-light); font-weight: 500;">${rev.date}</span>
                    </div>
                    <p style="font-size: 13px; color: var(--text-muted); line-height: 1.5; padding-left: 36px;">${rev.comment}</p>
                  </div>
                `).join('')}
              </div>
            `}
          </div>
          
        </div>
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Gallery image switching click
  const mainImg = container.querySelector("#detail-main-img");
  const thumbs = container.querySelectorAll(".detail-thumb-img");
  
  thumbs.forEach(thumb => {
    thumb.addEventListener("click", () => {
      thumbs.forEach(t => t.classList.remove("active"));
      thumb.classList.add("active");
      const idx = Number(thumb.dataset.index);
      if (mainImg) {
        mainImg.src = product.images[idx];
      }
    });
  });
  
  // Image Hover Zoom effect
  const zoomBox = container.querySelector("#detail-zoom-box");
  if (zoomBox && mainImg) {
    zoomBox.addEventListener("mousemove", (e) => {
      const rect = zoomBox.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      mainImg.style.transformOrigin = `${x}px ${y}px`;
      mainImg.style.transform = "scale(2.2)";
    });
    
    zoomBox.addEventListener("mouseleave", () => {
      mainImg.style.transform = "scale(1)";
    });
  }
  
  // Size Button selection clicking
  container.querySelectorAll(".size-option-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      container.querySelectorAll(".size-option-btn").forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedSize = btn.dataset.size;
    });
  });
  
  // Add to Cart
  const addToCartBtn = container.querySelector("#detail-add-cart-btn");
  addToCartBtn.addEventListener("click", () => {
    if (!selectedSize) {
      alert("Please select a product size!");
      return;
    }
    
    db.addToCart(product.id, selectedSize, 1);
    
    // Animate Add to Cart feedback
    addToCartBtn.innerHTML = `<i data-lucide="check"></i> Added to Cart!`;
    lucide.createIcons();
    addToCartBtn.style.backgroundColor = "var(--success)";
    addToCartBtn.style.color = "#fff";
    addToCartBtn.style.borderColor = "var(--success)";
    
    // Automatically trigger slide-over list render inside app.js
    renderCartDrawerList();
    document.getElementById("cart-drawer-overlay").classList.add("active");
    
    setTimeout(() => {
      addToCartBtn.innerHTML = `<i data-lucide="shopping-cart"></i> Add to Cart`;
      lucide.createIcons();
      addToCartBtn.style.backgroundColor = "#fff";
      addToCartBtn.style.color = "var(--text-dark)";
      addToCartBtn.style.borderColor = "var(--text-dark)";
    }, 2500);
  });
  
  // Buy Now (Add to cart & redirect to checkout directly)
  container.querySelector("#detail-buy-now-btn").addEventListener("click", () => {
    if (!selectedSize) {
      alert("Please select a product size!");
      return;
    }
    db.addToCart(product.id, selectedSize, 1);
    window.location.hash = "#checkout";
  });
  
  // Share & Earn reseller popup trigger
  container.querySelector("#detail-reseller-share-btn").addEventListener("click", () => {
    triggerResellerModal(product);
  });
  
  // Pincode Estimation check
  const pinInput = container.querySelector("#detail-pincode-input");
  const pinBtn = container.querySelector("#detail-pincode-btn");
  const pinResult = container.querySelector("#detail-pincode-result");
  
  pinBtn.addEventListener("click", () => {
    const pin = pinInput.value.trim();
    if (pin.length !== 6 || isNaN(pin)) {
      pinResult.textContent = "Please enter a valid 6-digit pincode!";
      pinResult.className = "pincode-result error";
      return;
    }
    
    // Simulate API match
    const isExpress = pin.endsWith("1") || pin.endsWith("3") || pin.endsWith("7");
    if (isExpress) {
      pinResult.innerHTML = `<i data-lucide="truck" style="display:inline-block; vertical-align:middle; width:16px;"></i> Express Delivery: Delivered by tomorrow (Free Shipping)`;
      pinResult.className = "pincode-result success";
    } else {
      pinResult.innerHTML = `<i data-lucide="truck" style="display:inline-block; vertical-align:middle; width:16px;"></i> Standard Delivery: Delivered in 3-4 days (Free Shipping)`;
      pinResult.className = "pincode-result success";
    }
    lucide.createIcons();
  });
}
