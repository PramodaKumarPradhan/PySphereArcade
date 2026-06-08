// Kraya Reseller Share & Earnings Manager
import { openModal, closeModal } from '../app.js';
import { db } from '../db.js';

export function triggerResellerModal(product) {
  const defaultCustomerPrice = Math.round(product.price * 1.25); // Set 25% default margin recommendation
  const initialProfit = defaultCustomerPrice - product.price;
  
  // Custom Gradient Image Check
  let imageHtml = '';
  if (product.image.startsWith('custom:')) {
    const gradientClass = `prod-image-gradient-${product.image.split(':')[1]}`;
    imageHtml = `<div class="procedural-placeholder ${gradientClass}" style="width: 80px; height: 80px; border-radius: 8px; position:relative;"><i data-lucide="shirt" style="width:24px; height:24px;"></i></div>`;
  } else {
    imageHtml = `<img src="${product.image}" alt="${product.name}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px;">`;
  }

  const modalHtml = `
    <div class="modal-header">
      <h3 class="d-flex align-center gap-1"><i data-lucide="hand-coins" style="color: var(--secondary-color);"></i> Reseller Margin Calculator</h3>
      <button id="reseller-close-modal" class="action-btn"><i data-lucide="x"></i></button>
    </div>
    <div class="modal-body">
      <div class="d-flex gap-2" style="margin-bottom: 20px; align-items: center; background-color: var(--bg-main); padding: 12px; border-radius: 8px;">
        ${imageHtml}
        <div>
          <h4 style="font-size: 14px; font-weight: 700; color: var(--text-dark);">${product.name}</h4>
          <div style="font-size: 13px; color: var(--text-muted);">Supplier Wholesale Price: <strong>₹${product.price}</strong></div>
        </div>
      </div>
      
      <div class="form-group">
        <label class="form-label">Customer Selling Price (Your Choice)</label>
        <div style="position: relative; display: flex; align-items: center;">
          <span style="position: absolute; left: 16px; font-weight: 700; color: var(--text-muted);">₹</span>
          <input type="number" id="reseller-customer-price" class="form-control" style="padding-left: 32px;" value="${defaultCustomerPrice}" min="${product.price}">
        </div>
        <p style="font-size: 11px; color: var(--text-light); margin-top: 6px;">We recommend selling at ₹${defaultCustomerPrice} to get high conversions.</p>
      </div>
      
      <div style="background-color: var(--success-bg); padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid rgba(3, 166, 133, 0.2);">
        <div class="d-flex justify-between align-center">
          <span style="font-size: 14px; font-weight: 600; color: var(--success);">Your Net Reseller Profit:</span>
          <span style="font-size: 24px; font-weight: 800; color: var(--success);" id="reseller-profit-value">₹${initialProfit}</span>
        </div>
        <p style="font-size: 11px; color: var(--text-muted); margin-top: 6px; line-height: 1.4;">When your customer purchases this item, the supplier ships it directly. Your margin of ₹<span id="reseller-profit-sub">${initialProfit}</span> will be credited directly to your supplier balance!</p>
      </div>

      <div class="form-group">
        <label class="form-label">Share Description Template</label>
        <textarea id="reseller-share-text" class="form-control" rows="6" readonly style="resize: none; font-size: 12px; background-color: #fafafa; font-family: monospace;"></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-large btn-cart-add" style="padding: 10px 20px;" id="reseller-copy-btn">
        <i data-lucide="copy"></i> Copy Details
      </button>
      <button class="btn-large btn-buy-now" style="padding: 10px 20px; background-color: #25d366; border-color: #25d366;" id="reseller-whatsapp-btn">
        <i data-lucide="message-square"></i> Share on WhatsApp
      </button>
    </div>
  `;
  
  openModal(modalHtml);
  
  const priceInput = document.getElementById("reseller-customer-price");
  const profitText = document.getElementById("reseller-profit-value");
  const profitSubText = document.getElementById("reseller-profit-sub");
  const shareTextarea = document.getElementById("reseller-share-text");
  
  // Format message text description
  const updateShareText = () => {
    const custPrice = Number(priceInput.value) || product.price;
    const profit = Math.max(0, custPrice - product.price);
    
    profitText.textContent = `₹${profit}`;
    profitSubText.textContent = profit;
    
    let text = `✨ *Dashing New Arrivals from Kraya!* ✨\n\n`;
    text += `*Product Name:* ${product.name}\n`;
    text += `*Special Price:* ₹${custPrice} only!\n`;
    text += `*Sizes Available:* ${product.sizes.join(', ')}\n`;
    text += `*Quality Guarantee:* 100% Premium Material\n`;
    text += `*Delivery Details:* Free Delivery & Cash on Delivery (COD) available nationwide.\n\n`;
    text += `*Description:* ${product.description}\n\n`;
    text += `👉 *To order or check designs, reply back to this message!*`;
    
    shareTextarea.value = text;
  };
  
  // Initial fill
  updateShareText();
  
  // Price change updates
  priceInput.addEventListener("input", updateShareText);
  
  // Close Modal
  document.getElementById("reseller-close-modal").addEventListener("click", closeModal);
  
  // Copy Details Clipboard
  document.getElementById("reseller-copy-btn").addEventListener("click", () => {
    shareTextarea.select();
    document.execCommand('copy');
    
    // Increment shared products count
    const user = db.getCurrentUser();
    user.sharedProductsCount += 1;
    db.updateCurrentUser(user);
    
    const copyBtn = document.getElementById("reseller-copy-btn");
    copyBtn.innerHTML = `<i data-lucide="check"></i> Copied!`;
    lucide.createIcons();
    
    setTimeout(() => {
      copyBtn.innerHTML = `<i data-lucide="copy"></i> Copy Details`;
      lucide.createIcons();
    }, 2000);
  });
  
  // WhatsApp Direct API
  document.getElementById("reseller-whatsapp-btn").addEventListener("click", () => {
    const message = encodeURIComponent(shareTextarea.value);
    const whatsappUrl = `https://api.whatsapp.com/send?text=${message}`;
    
    // Increment count
    const user = db.getCurrentUser();
    user.sharedProductsCount += 1;
    db.updateCurrentUser(user);
    
    window.open(whatsappUrl, '_blank');
  });
}
