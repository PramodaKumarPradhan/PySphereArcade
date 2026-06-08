// Kraya Shopping Cart & Checkout Steps Manager
import { db } from '../db.js';
import { navigateToRoute } from '../app.js';

let activeStep = 1; // Step 1: Summary, Step 2: Address, Step 3: Payment
let selectedAddressIndex = 0;
let paymentMethod = 'cod'; // cod, upi, card
let appliedDiscount = 0;
let promoCodeText = '';
let isResellerOrder = false;
let redeemCoinsChecked = false;

export function render(container, params) {
  const cartItems = db.getCart();
  
  if (cartItems.length === 0 && activeStep !== 4) {
    container.innerHTML = `
      <div class="container" style="padding: 60px 0; text-align: center;">
        <i data-lucide="shopping-cart" style="width: 56px; height: 56px; color: var(--text-light); stroke-width: 1.5; margin-bottom: 15px;"></i>
        <h2>Your Shopping Cart is Empty</h2>
        <p style="color: var(--text-muted); margin-top: 10px;">Add products to your cart from our home page catalogue to place an order.</p>
        <a href="#catalog" class="btn-large btn-buy-now" style="text-decoration: none; display: inline-block; margin-top: 20px; max-width: 200px; margin-left: auto; margin-right: auto;">Shop Now</a>
      </div>`;
    return;
  }
  
  recalcTotals(cartItems);
}

// Calculate totals including discounts and reseller options
function recalcTotals(cartItems) {
  let itemTotal = 0;
  let originalTotal = 0;
  
  cartItems.forEach(item => {
    itemTotal += item.price * item.quantity;
    originalTotal += item.originalPrice * item.quantity;
  });
  
  const user = db.getCurrentUser();
  const coinsBalance = user ? user.superCoins : 0;
  
  // Redeem SuperCoins rule: 1 Coin = 1 rupee. Max 50 coins or 10% of cart value
  const maxRedeemableCoins = Math.min(coinsBalance, 50, Math.floor(itemTotal * 0.1));
  const coinsRedeemed = redeemCoinsChecked ? maxRedeemableCoins : 0;
  
  const discountSavings = originalTotal - itemTotal;
  const onlineDiscount = (paymentMethod !== 'cod') ? 15 : 0; // ₹15 discount on UPI/Card payments
  const finalAmount = Math.max(0, itemTotal - appliedDiscount - onlineDiscount - coinsRedeemed);
  
  const totals = {
    itemTotal,
    originalTotal,
    discountSavings,
    couponDiscount: appliedDiscount,
    onlineDiscount,
    coinsRedeemed,
    maxRedeemableCoins,
    coinsBalance,
    finalAmount
  };
  
  renderCheckoutShell(totals, cartItems);
}

function renderCheckoutShell(totals, cartItems) {
  const container = document.getElementById("app-viewport");
  if (!container) return;
  
  if (activeStep === 4) {
    // If confirmation view
    return;
  }
  
  let html = `
    <div class="container">
      <h1 style="font-size: 24px; font-weight: 800; margin-bottom: 24px; display: flex; align-items: center; gap: 8px;">
        <i data-lucide="shield-check" style="color: var(--success); width: 28px; height: 28px;"></i> Secure Checkout Flow
      </h1>
      
      <div class="checkout-layout">
        
        <!-- Left Steps -->
        <div class="checkout-steps">
          
          <!-- Step 1: Order Summary -->
          <div class="step-card ${activeStep === 1 ? 'active' : ''}">
            <div class="step-header">
              <span class="step-title">
                <span class="step-number">1</span>
                Order Summary (${cartItems.length} items)
              </span>
              ${activeStep > 1 ? `<button class="clear-filters-btn" id="edit-step-1">Edit</button>` : ''}
            </div>
            <div class="step-body">
              <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px;">
                ${cartItems.map(item => {
                  let imageHtml = '';
                  if (item.image.startsWith('custom:')) {
                    const gradientClass = `prod-image-gradient-${item.image.split(':')[1]}`;
                    imageHtml = `<div class="cart-item-img procedural-placeholder ${gradientClass}" style="width: 70px; height: 70px;"><i data-lucide="shirt" style="width: 20px; height: 20px;"></i></div>`;
                  } else {
                    imageHtml = `<img src="${item.image}" alt="${item.name}" class="cart-item-img" style="width: 70px; height: 70px;">`;
                  }
                  
                  return `
                    <div class="d-flex gap-2" style="border-bottom: 1px solid var(--border-light); padding-bottom: 12px;">
                      ${imageHtml}
                      <div style="flex-grow: 1;">
                        <h4 style="font-size: 13px; font-weight: 700;">${item.name}</h4>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Size: <strong>${item.size}</strong> | Qty: <strong>${item.quantity}</strong></div>
                        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">Seller: ${item.sellerName}</div>
                      </div>
                      <div style="text-align: right;">
                        <div style="font-weight: 800; font-size: 15px;">₹${item.price * item.quantity}</div>
                        ${item.originalPrice > item.price ? `<div style="font-size: 11px; text-decoration: line-through; color: var(--text-light);">₹${item.originalPrice * item.quantity}</div>` : ''}
                      </div>
                    </div>`;
                }).join('')}
              </div>
              <button class="btn-large btn-buy-now" id="checkout-continue-step1" style="max-width: 250px;">Continue to Address</button>
            </div>
          </div>
          
          <!-- Step 2: Delivery Address -->
          <div class="step-card ${activeStep === 2 ? 'active' : ''}">
            <div class="step-header">
              <span class="step-title">
                <span class="step-number">2</span>
                Delivery Address
              </span>
              ${activeStep > 2 ? `<button class="clear-filters-btn" id="edit-step-2">Edit</button>` : ''}
            </div>
            <div class="step-body">
              <div id="checkout-address-list" style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                ${renderAddressList()}
              </div>
              
              <div class="d-flex gap-2" style="margin-bottom: 24px;">
                <button class="btn-large btn-buy-now" id="checkout-continue-step2" style="max-width: 250px;">Deliver to selected address</button>
              </div>
            </div>
          </div>
          
          <!-- Step 3: Payment Options -->
          <div class="step-card ${activeStep === 3 ? 'active' : ''}">
            <div class="step-header">
              <span class="step-title">
                <span class="step-number">3</span>
                Payment Options
              </span>
            </div>
            <div class="step-body">
              
              <!-- Reseller order options toggle (Meesho specialty) -->
              <div style="background-color: rgba(63, 81, 181, 0.04); border: 1.5px dashed var(--secondary-color); padding: 18px; border-radius: 8px; margin-bottom: 24px;">
                <label class="d-flex align-center gap-2" style="cursor: pointer; font-weight: 700; font-size: 14px; color: var(--secondary-color);">
                  <input type="checkbox" id="checkout-reseller-toggle" style="width: 18px; height: 18px; accent-color: var(--secondary-color);" ${isResellerOrder ? 'checked' : ''}>
                  Is this a Reseller Order? (Deliver to customer)
                </label>
                <div id="checkout-reseller-pane" style="display: ${isResellerOrder ? 'block' : 'none'}; margin-top: 15px; border-top: 1px solid rgba(63, 81, 181, 0.15); padding-top: 15px;">
                  <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 12px; line-height: 1.4;">Supplier details and Kraya logo will be hidden. Package will display you as the sender, with customer price listed as the total value.</p>
                  <div class="form-group" style="margin-bottom: 0;">
                    <label class="form-label">Customer Cash/Invoice Price (including your margin)</label>
                    <div style="position: relative; display: flex; align-items: center; width: 200px;">
                      <span style="position: absolute; left: 16px; font-weight: 700; color: var(--text-muted);">₹</span>
                      <input type="number" id="checkout-reseller-final-price" class="form-control" style="padding-left: 32px;" value="${Math.round(totals.finalAmount * 1.25)}" min="${totals.finalAmount}">
                    </div>
                    <div style="font-size: 12px; font-weight: 700; color: var(--success); margin-top: 8px;">Estimated margin to credit your balance: ₹<span id="checkout-reseller-margin-label">${Math.round(totals.finalAmount * 0.25)}</span></div>
                  </div>
                </div>
              </div>
              
              <!-- Payment Selector List -->
              <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;">
                <label class="d-flex align-center gap-2" style="cursor: pointer; border: 1px solid var(--border-color); padding: 14px 20px; border-radius: 8px; font-weight: 600;">
                  <input type="radio" name="payment" value="cod" ${paymentMethod === 'cod' ? 'checked' : ''} style="width: 18px; height: 18px; accent-color: var(--primary-color);">
                  <span>Cash on Delivery (COD)</span>
                </label>
                
                <label class="d-flex align-center gap-2" style="cursor: pointer; border: 1px solid var(--border-color); padding: 14px 20px; border-radius: 8px; font-weight: 600; justify-content: space-between;">
                  <div class="d-flex align-center gap-2">
                    <input type="radio" name="payment" value="upi" ${paymentMethod === 'upi' ? 'checked' : ''} style="width: 18px; height: 18px; accent-color: var(--primary-color);">
                    <span>UPI / QR Codes</span>
                  </div>
                  <span style="font-size: 11px; font-weight: 700; color: var(--success); background-color: var(--success-bg); padding: 2px 6px; border-radius: 4px;">Save ₹15 Extra</span>
                </label>
                
                <label class="d-flex align-center gap-2" style="cursor: pointer; border: 1px solid var(--border-color); padding: 14px 20px; border-radius: 8px; font-weight: 600; justify-content: space-between;">
                  <div class="d-flex align-center gap-2">
                    <input type="radio" name="payment" value="card" ${paymentMethod === 'card' ? 'checked' : ''} style="width: 18px; height: 18px; accent-color: var(--primary-color);">
                    <span>Credit / Debit Card</span>
                  </div>
                  <span style="font-size: 11px; font-weight: 700; color: var(--success); background-color: var(--success-bg); padding: 2px 6px; border-radius: 4px;">Save ₹15 Extra</span>
                </label>
              </div>
              
              <!-- Conditional payment fields -->
              <div id="checkout-gateway-fields" style="margin-bottom: 24px; border-top: 1px solid var(--border-light); padding-top: 15px;">
                ${renderPaymentFields()}
              </div>
              
              <button class="btn-large btn-buy-now w-100" id="checkout-place-order-btn">
                Place Order (Pay ₹${totals.finalAmount})
              </button>
            </div>
          </div>
          
        </div>
        
        <!-- Right Price details -->
        <aside class="price-summary-card">
          <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 18px; border-bottom: 1px solid var(--border-light); padding-bottom: 8px;">Price Details</h3>
          
          <div class="price-row-detail">
            <span>Product List Price</span>
            <span>₹${totals.originalTotal}</span>
          </div>
          <div class="price-row-detail" style="color: var(--success); font-weight: 600;">
            <span>Catalog Discounts</span>
            <span>-₹${totals.discountSavings}</span>
          </div>
          
          <!-- SuperCoins redemption slider (Flipkart specialty) -->
          ${totals.coinsBalance > 0 ? `
            <div style="border-top: 1px dashed var(--border-light); border-bottom: 1px dashed var(--border-light); padding: 12px 0; margin-bottom: 12px; margin-top: 12px;">
              <label class="d-flex align-center gap-1" style="cursor: pointer; font-size: 13px; font-weight: 700; color: var(--secondary-color);">
                <input type="checkbox" id="checkout-coins-checkbox" style="width: 16px; height: 16px; accent-color: var(--secondary-color);" ${redeemCoinsChecked ? 'checked' : ''}>
                Redeem up to ${totals.maxRedeemableCoins} SuperCoins (Save ₹${totals.maxRedeemableCoins})
              </label>
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px; display:flex; align-items:center; gap:4px;">
                <i data-lucide="coins" style="width:14px; color: gold; fill: gold;"></i> Wallet Balance: <strong>${totals.coinsBalance} Coins</strong>
              </div>
            </div>
          ` : ''}
          
          <!-- Coupon Application Form -->
          <div style="border-bottom: 1px solid var(--border-light); padding-bottom: 15px; margin-bottom: 15px;">
            <div style="font-size: 12px; font-weight: 700; margin-bottom: 8px;">Apply Discount Coupon</div>
            <div class="d-flex gap-1">
              <input type="text" class="form-control" id="checkout-coupon-input" placeholder="e.g. KRAYANEW10" style="padding: 8px 12px; font-size: 13px;" value="${promoCodeText}">
              <button class="supplier-btn" id="checkout-coupon-btn" style="padding: 8px 16px; font-size: 13px;">Apply</button>
            </div>
            <div id="checkout-coupon-msg" style="font-size: 11px; margin-top: 6px; font-weight: 600;"></div>
          </div>
          
          ${totals.couponDiscount > 0 ? `
            <div class="price-row-detail" style="color: var(--success); font-weight: 600;">
              <span>Promo Code Offer</span>
              <span>-₹${totals.couponDiscount}</span>
            </div>` : ''}
            
          ${totals.onlineDiscount > 0 ? `
            <div class="price-row-detail" style="color: var(--success); font-weight: 600;">
              <span>Prepaid Online Offer</span>
              <span>-₹${totals.onlineDiscount}</span>
            </div>` : ''}
            
          ${totals.coinsRedeemed > 0 ? `
            <div class="price-row-detail" style="color: var(--success); font-weight: 600;">
              <span>SuperCoins Discount</span>
              <span>-₹${totals.coinsRedeemed}</span>
            </div>` : ''}
            
          <div class="price-row-detail">
            <span>Delivery Charges</span>
            <span style="color: var(--success); font-weight: 700;">FREE</span>
          </div>
          
          <div class="price-row-detail total">
            <span>Order Total</span>
            <span>₹${totals.finalAmount}</span>
          </div>
          
          <div style="background-color: var(--success-bg); color: var(--success); text-align: center; padding: 10px; border-radius: 6px; font-size: 12px; font-weight: 700; margin-top: 20px;">
            🎉 You save ₹${totals.discountSavings + totals.couponDiscount + totals.onlineDiscount + totals.coinsRedeemed} on this order!
          </div>
        </aside>
        
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  lucide.createIcons();
  
  wireUpCheckoutEvents(totals, cartItems);
}

// Renders the addresses list
function renderAddressList() {
  const addresses = db.getAddresses();
  
  if (addresses.length === 0) {
    return `<div style="font-size: 13px; color: var(--text-muted); text-align: center; padding: 20px 0;">No addresses added yet! Click the button below to add your delivery details.</div>`;
  }
  
  return addresses.map((addr, idx) => `
    <label class="d-flex gap-2" style="cursor: pointer; border: 1.5px solid ${selectedAddressIndex === idx ? 'var(--primary-color)' : 'var(--border-color)'}; padding: 16px; border-radius: 8px; background-color: ${selectedAddressIndex === idx ? 'rgba(244, 51, 151, 0.02)' : '#fff'};">
      <input type="radio" name="address" class="address-radio" value="${idx}" ${selectedAddressIndex === idx ? 'checked' : ''} style="margin-top: 4px; accent-color: var(--primary-color);">
      <div>
        <div class="d-flex align-center gap-1">
          <strong style="font-size: 14px;">${addr.name}</strong>
          ${addr.isDefault ? `<span style="font-size: 10px; background-color: var(--bg-main); color: var(--text-muted); padding: 1px 4px; border-radius: 2px;">Default</span>` : ''}
        </div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px; line-height: 1.5;">
          ${addr.houseNo}, ${addr.roadName}<br>
          ${addr.city}, ${addr.state} - <strong>${addr.pincode}</strong>
        </div>
        <div style="font-size: 12px; color: var(--text-dark); font-weight: 600; margin-top: 6px;">Phone: ${addr.phone}</div>
      </div>
    </label>
  `).join('') + `
    <button class="supplier-btn" id="checkout-add-address-btn" style="border-style: dashed; width: 100%; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 12px;">
      <i data-lucide="plus" style="width: 16px;"></i> Add New Shipping Address
    </button>
  `;
}

// Payment method extra input fields
function renderPaymentFields() {
  if (paymentMethod === 'cod') {
    return `<div style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">Pay in cash when product reaches your home. Ensure correct change during delivery.</div>`;
  }
  
  if (paymentMethod === 'upi') {
    return `
      <div>
        <div style="display: flex; gap: 20px; align-items: center; background-color: var(--bg-main); padding: 12px; border-radius: 8px; margin-bottom: 15px;">
          <!-- Mock QR image -->
          <div style="background-color:#fff; padding: 6px; border:1px solid #ccc; border-radius: 4px; display:flex; align-items:center; justify-content:center; width:80px; height:80px;">
            <i data-lucide="qr-code" style="width: 60px; height: 60px; color: #333;"></i>
          </div>
          <div>
            <div style="font-size: 13px; font-weight: 700;">Scan QR Code to pay</div>
            <p style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">Open any UPI App (GPay, PhonePe, Paytm) and scan QR code to transfer payment securely.</p>
          </div>
        </div>
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Or Pay via UPI Virtual Address (VPA)</label>
          <div class="d-flex gap-1">
            <input type="text" class="form-control" placeholder="username@upi" style="font-size: 13px; padding: 8px 12px;">
            <button class="supplier-btn" style="font-size: 13px; padding: 8px 16px;">Verify VPA</button>
          </div>
        </div>
      </div>`;
  }
  
  if (paymentMethod === 'card') {
    return `
      <div style="display: flex; flex-direction: column; gap: 12px;">
        <div class="form-group" style="margin-bottom: 0;">
          <label class="form-label">Credit / Debit Card Number</label>
          <input type="text" class="form-control" placeholder="4321 5678 9012 3456" maxlength="19" style="font-size: 13px;">
        </div>
        <div class="d-flex gap-2">
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label class="form-label">Expiry Date</label>
            <input type="text" class="form-control" placeholder="MM/YY" maxlength="5" style="font-size: 13px;">
          </div>
          <div class="form-group" style="flex:1; margin-bottom:0;">
            <label class="form-label">Card CVV</label>
            <input type="password" class="form-control" placeholder="•••" maxlength="3" style="font-size: 13px;">
          </div>
        </div>
      </div>`;
  }
  return '';
}

// Event bindings
function wireUpCheckoutEvents(totals, cartItems) {
  // Edit Step 1 summary click
  const editStep1 = document.getElementById("edit-step-1");
  if (editStep1) {
    editStep1.addEventListener("click", () => {
      activeStep = 1;
      recalcTotals(cartItems);
    });
  }
  
  // Continue step 1 button
  const continue1 = document.getElementById("checkout-continue-step1");
  if (continue1) {
    continue1.addEventListener("click", () => {
      activeStep = 2;
      recalcTotals(cartItems);
    });
  }
  
  // Edit Step 2 address click
  const editStep2 = document.getElementById("edit-step-2");
  if (editStep2) {
    editStep2.addEventListener("click", () => {
      activeStep = 2;
      recalcTotals(cartItems);
    });
  }
  
  // Radio Address change select
  document.querySelectorAll(".address-radio").forEach(radio => {
    radio.addEventListener("change", (e) => {
      selectedAddressIndex = Number(e.target.value);
      recalcTotals(cartItems);
    });
  });
  
  // Continue step 2 button
  const continue2 = document.getElementById("checkout-continue-step2");
  if (continue2) {
    continue2.addEventListener("click", () => {
      const addresses = db.getAddresses();
      if (addresses.length === 0) {
        alert("Please add a shipping address first!");
        return;
      }
      activeStep = 3;
      recalcTotals(cartItems);
    });
  }
  
  // Add new address form drawer overlay click
  const addAddressBtn = document.getElementById("checkout-add-address-btn");
  if (addAddressBtn) {
    addAddressBtn.addEventListener("click", () => {
      import('../app.js').then(app => {
        const modalHtml = `
          <div class="modal-header">
            <h3><i data-lucide="map-pin"></i> Add New Delivery Address</h3>
            <button onclick="document.getElementById('universal-modal').classList.remove('active')" class="action-btn"><i data-lucide="x"></i></button>
          </div>
          <form id="checkout-new-address-form">
            <div class="modal-body" style="display:flex; flex-direction:column; gap: 14px;">
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Full Customer Name</label>
                <input type="text" class="form-control" id="new-addr-name" placeholder="Pramoda Kumar Pradhan" required>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Mobile Contact Number (10 digit)</label>
                <input type="text" class="form-control" id="new-addr-phone" placeholder="9876543210" maxlength="10" required>
              </div>
              <div class="d-flex gap-2">
                <div class="form-group" style="flex:2; margin-bottom:0;">
                  <label class="form-label">House No / Flat / Building Name</label>
                  <input type="text" class="form-control" id="new-addr-house" placeholder="Flat No. 102, Royal Residency" required>
                </div>
                <div class="form-group" style="flex:1; margin-bottom:0;">
                  <label class="form-label">Pincode (6 digit)</label>
                  <input type="text" class="form-control" id="new-addr-pincode" placeholder="751001" maxlength="6" required>
                </div>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Road Name / Area / Colony</label>
                <input type="text" class="form-control" id="new-addr-road" placeholder="Sanjay Nagar Lane 2" required>
              </div>
              <div class="d-flex gap-2">
                <div class="form-group" style="flex:1; margin-bottom:0;">
                  <label class="form-label">City Name</label>
                  <input type="text" class="form-control" id="new-addr-city" placeholder="Bhubaneswar" required>
                </div>
                <div class="form-group" style="flex:1; margin-bottom:0;">
                  <label class="form-label">State Name</label>
                  <input type="text" class="form-control" id="new-addr-state" placeholder="Odisha" required>
                </div>
              </div>
              <label class="d-flex align-center gap-1" style="font-size: 13px; cursor:pointer;">
                <input type="checkbox" id="new-addr-default" style="width: 16px; height: 16px;"> Set as Default Address
              </label>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn-large btn-cart-add" onclick="document.getElementById('universal-modal').classList.remove('active')" style="padding:10px 20px;">Cancel</button>
              <button type="submit" class="btn-large btn-buy-now" style="padding:10px 20px;">Save Address</button>
            </div>
          </form>`;
        app.openModal(modalHtml);
        
        // Wire up address saving
        document.getElementById("checkout-new-address-form").addEventListener("submit", (e) => {
          e.preventDefault();
          
          const newAddress = {
            name: document.getElementById("new-addr-name").value.trim(),
            phone: document.getElementById("new-addr-phone").value.trim(),
            houseNo: document.getElementById("new-addr-house").value.trim(),
            roadName: document.getElementById("new-addr-road").value.trim(),
            pincode: document.getElementById("new-addr-pincode").value.trim(),
            city: document.getElementById("new-addr-city").value.trim(),
            state: document.getElementById("new-addr-state").value.trim(),
            isDefault: document.getElementById("new-addr-default").checked
          };
          
          const updatedList = db.addAddress(newAddress);
          selectedAddressIndex = updatedList.length - 1; // auto select new address
          app.closeModal();
          recalcTotals(cartItems);
        });
      });
    });
  }
  
  // Coupon applied click
  const couponBtn = document.getElementById("checkout-coupon-btn");
  const couponInput = document.getElementById("checkout-coupon-input");
  const couponMsg = document.getElementById("checkout-coupon-msg");
  if (couponBtn) {
    couponBtn.addEventListener("click", () => {
      const code = couponInput.value.trim().toUpperCase();
      if (!code) {
        couponMsg.textContent = "Please enter a coupon code!";
        couponMsg.style.color = "var(--error)";
        return;
      }
      
      // Coupon database check
      if (code === 'KRAYANEW10') {
        appliedDiscount = Math.round(totals.itemTotal * 0.1); // 10%
        promoCodeText = code;
        couponMsg.textContent = `Success: Code KRAYANEW10 applied! 10% discount subtracted.`;
        couponMsg.style.color = "var(--success)";
      } else if (code === 'MEESHOLOVE') {
        appliedDiscount = 100; // Flat 100
        promoCodeText = code;
        couponMsg.textContent = `Success: Code MEESHOLOVE applied! Flat ₹100 discount subtracted.`;
        couponMsg.style.color = "var(--success)";
      } else {
        couponMsg.textContent = `Invalid: Code "${code}" is not valid or expired.`;
        couponMsg.style.color = "var(--error)";
        appliedDiscount = 0;
        promoCodeText = '';
      }
      recalcTotals(cartItems);
    });
  }
  
  // Payment Radio selections
  document.querySelectorAll("input[name='payment']").forEach(radio => {
    radio.addEventListener("change", (e) => {
      paymentMethod = e.target.value;
      recalcTotals(cartItems);
    });
  });
  
  // Reseller Order toggle check
  const resellerToggle = document.getElementById("checkout-reseller-toggle");
  const resellerPane = document.getElementById("checkout-reseller-pane");
  if (resellerToggle) {
    resellerToggle.addEventListener("change", (e) => {
      isResellerOrder = e.target.checked;
      resellerPane.style.display = isResellerOrder ? 'block' : 'none';
    });
  }
  
  // Reseller Final Customer price key up calculation
  const customerPriceInput = document.getElementById("checkout-reseller-final-price");
  const resellerLabel = document.getElementById("checkout-reseller-margin-label");
  if (customerPriceInput) {
    customerPriceInput.addEventListener("input", () => {
      const custVal = Number(customerPriceInput.value) || 0;
      const netMargin = Math.max(0, custVal - totals.finalAmount);
      resellerLabel.textContent = netMargin;
    });
  }
  
  // SuperCoins checkbox event toggle
  const coinsCheckbox = document.getElementById("checkout-coins-checkbox");
  if (coinsCheckbox) {
    coinsCheckbox.addEventListener("change", (e) => {
      redeemCoinsChecked = e.target.checked;
      recalcTotals(cartItems);
    });
  }
  
  // Place Order Submit click
  const placeOrderBtn = document.getElementById("checkout-place-order-btn");
  if (placeOrderBtn) {
    placeOrderBtn.addEventListener("click", () => {
      const addresses = db.getAddresses();
      if (addresses.length === 0) {
        alert("Please select or add a shipping address!");
        activeStep = 2;
        recalcTotals(cartItems);
        return;
      }
      
      const shippingAddress = addresses[selectedAddressIndex];
      let customMargin = 0;
      
      if (isResellerOrder) {
        const custVal = Number(customerPriceInput.value) || 0;
        if (custVal < totals.finalAmount) {
          alert(`Customer price cannot be lower than wholesale checkout price of ₹${totals.finalAmount}!`);
          return;
        }
        customMargin = custVal - totals.finalAmount;
      }
      
      const orderData = {
        items: cartItems,
        paymentMethod: paymentMethod === 'cod' ? 'Cash on Delivery' : paymentMethod.toUpperCase(),
        address: shippingAddress,
        totals: totals,
        resellerMargin: customMargin
      };
      
      // Save order in Database
      const confirmedOrder = db.createOrder(orderData);
      
      // Clear Cart
      db.clearCart();
      
      // Reset variables
      activeStep = 4;
      appliedDiscount = 0;
      promoCodeText = '';
      redeemCoinsChecked = false; // reset
      
      // Fire Confetti!
      fireCheckoutConfetti();
      
      // Render success screen inside main viewport container
      renderConfirmationView(confirmedOrder);
    });
  }
}

function renderConfirmationView(order) {
  const container = document.getElementById("app-viewport");
  if (!container) return;
  
  container.innerHTML = `
    <div class="container" style="padding: 60px 0; text-align: center; max-width: 600px;">
      <div style="background-color: var(--success-bg); color: var(--success); width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 24px auto; box-shadow: var(--shadow-sm);">
        <i data-lucide="check-circle" style="width: 48px; height: 48px; stroke-width: 2;"></i>
      </div>
      
      <h1 style="font-size: 28px; font-weight: 800; margin-bottom: 8px;">Order Confirmed!</h1>
      <p style="color: var(--text-muted); font-size: 15px; margin-bottom: 24px;">Thank you for shopping with Kraya. Your order has been registered successfully.</p>
      
      <div style="background-color: #fff; padding: 24px; border-radius: 12px; text-align: left; box-shadow: var(--shadow-sm); border: 1px solid var(--border-light); margin-bottom: 30px;">
        <div style="display: flex; justify-between; border-bottom: 1px solid var(--border-light); padding-bottom: 12px; margin-bottom: 16px;">
          <div>
            <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700; display:block;">Order ID</span>
            <strong style="font-size: 15px; color: var(--primary-color);">${order.orderId}</strong>
          </div>
          <div style="text-align: right;">
            <span style="font-size: 11px; color: var(--text-light); text-transform: uppercase; font-weight:700; display:block;">Estimated Delivery</span>
            <strong style="font-size: 14px;">In 3-4 Business Days</strong>
          </div>
        </div>
        
        <div style="font-size: 13px; line-height: 1.6;">
          <div style="margin-bottom: 8px;">Shipping To: <strong>${order.address.name}</strong></div>
          <div style="color: var(--text-muted);">${order.address.houseNo}, ${order.address.roadName}, ${order.address.city} - ${order.address.pincode}</div>
          <div style="margin-top: 12px; border-top: 1px dashed var(--border-light); padding-top: 12px; display:flex; justify-content:space-between; font-weight:700;">
            <span>Payment Method:</span>
            <span>${order.paymentMethod}</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-weight:800; font-size:16px; margin-top:8px;">
            <span>Total Paid Amount:</span>
            <span>₹${order.totals.finalAmount}</span>
          </div>
          ${order.totals.coinsRedeemed > 0 ? `
            <div style="display:flex; justify-content:space-between; color: var(--success); font-weight:600; margin-top:4px;">
              <span>SuperCoins Redeemed:</span>
              <span>-${order.totals.coinsRedeemed} Coins</span>
            </div>` : ''}
          ${order.resellerMargin > 0 ? `
            <div style="background-color: rgba(63, 81, 181, 0.05); color: var(--secondary-color); padding: 10px; border-radius: 6px; font-weight: 700; text-align: center; margin-top: 15px; border: 1px solid rgba(63, 81, 181, 0.15);">
              📈 Reseller Margin Earned: ₹${order.resellerMargin} (Will reflect in balance after shipment)
            </div>` : ''}
          <div style="background-color: var(--success-bg); color: var(--success); padding: 10px; border-radius: 6px; font-weight: 700; text-align: center; margin-top: 15px; border: 1px solid rgba(3, 166, 133, 0.2); display:flex; align-items:center; justify-content:center; gap:6px;">
            <i data-lucide="coins" style="width:18px; fill:gold; color:gold;"></i> SuperCoins Credited on Order: +${order.superCoinsEarned || 0} Coins!
          </div>
        </div>
      </div>
      
      <div class="d-flex gap-2" style="justify-content: center;">
        <button class="btn-large btn-cart-add" style="max-width: 220px;" onclick="window.location.hash='#catalog'">Continue Shopping</button>
        <button class="btn-large btn-buy-now" style="max-width: 220px;" onclick="window.location.hash='#profile?tab=orders'">Track Order</button>
      </div>
    </div>
  `;
  
  activeStep = 1; // reset for next flow
  lucide.createIcons();
}

function fireCheckoutConfetti() {
  if (typeof confetti === 'function') {
    confetti({
      particleCount: 150,
      spread: 80,
      origin: { y: 0.6 }
    });
  }
}
