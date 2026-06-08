// Kraya Seller / Supplier Panel Component
import { db } from '../db.js';

let activeSellerTab = 'dashboard'; // dashboard, inventory, add_product

export function render(container, params) {
  const products = db.getProducts();
  const orders = db.getOrders();
  
  // Calculate stats
  const totalSales = orders.reduce((sum, o) => sum + o.totals.finalAmount, 0) + 24800; // seed default
  const totalOrders = orders.length + 42;
  const activeProducts = products.length;
  
  let html = `
    <div class="container">
      <div class="seller-layout">
        
        <!-- Sidebar vendor tabs -->
        <aside class="seller-sidebar">
          <div style="padding: 10px; border-bottom: 1px solid var(--border-light); margin-bottom: 15px; text-align: center;">
            <div style="background-color: rgba(63, 81, 181, 0.08); color: var(--secondary-color); width: 50px; height: 50px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; margin: 0 auto 10px auto;">
              KP
            </div>
            <h4 style="font-size: 14px; font-weight: 700;">Kraya Supplier Hub</h4>
            <span style="font-size: 10px; color: var(--success); font-weight: 700;">● Verified Vendor</span>
          </div>
          
          <button class="seller-menu-item ${activeSellerTab === 'dashboard' ? 'active' : ''}" data-seller-tab="dashboard">
            <i data-lucide="bar-chart-3"></i> Sales Dashboard
          </button>
          
          <button class="seller-menu-item ${activeSellerTab === 'inventory' ? 'active' : ''}" data-seller-tab="inventory">
            <i data-lucide="warehouse"></i> Product Inventory (${activeProducts})
          </button>
          
          <button class="seller-menu-item ${activeSellerTab === 'add_product' ? 'active' : ''}" data-seller-tab="add_product">
            <i data-lucide="plus-circle"></i> Add New Product
          </button>
        </aside>
        
        <!-- Main Vendor View viewport -->
        <section style="display:flex; flex-direction:column; gap:20px;">
          <div id="seller-tab-content">
            ${renderSellerTabContent(products, totalSales, totalOrders, activeProducts)}
          </div>
        </section>
        
      </div>
    </div>
  `;
  
  container.innerHTML = html;
  lucide.createIcons();
  
  wireUpSellerEvents(container);
}

function renderSellerTabContent(products, totalSales, totalOrders, activeProducts) {
  if (activeSellerTab === 'dashboard') {
    return `
      <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">Supplier Sales Performance</h2>
      
      <!-- Metric Cards -->
      <div class="seller-dashboard-stats">
        <div class="stat-card">
          <div class="stat-icon pink"><i data-lucide="indian-rupee"></i></div>
          <div class="stat-info">
            <h3>₹${totalSales.toLocaleString('en-IN')}</h3>
            <p>Net Vendor Sales</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon blue"><i data-lucide="shopping-bag"></i></div>
          <div class="stat-info">
            <h3>${totalOrders}</h3>
            <p>Total Orders Received</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green"><i data-lucide="package"></i></div>
          <div class="stat-info">
            <h3>${activeProducts}</h3>
            <p>Active Listed Items</p>
          </div>
        </div>
      </div>
      
      <!-- Visual mock chart section styled nicely -->
      <div style="background-color: #fff; border-radius: 12px; border: 1px solid var(--border-light); padding: 24px; box-shadow: var(--shadow-sm); margin-bottom: 20px;">
        <h3 style="font-size:15px; font-weight:700; margin-bottom:20px;">Weekly Sales Distribution</h3>
        
        <div style="display: flex; height: 180px; align-items: flex-end; justify-content: space-between; gap:16px; padding-bottom: 10px; border-bottom: 2px solid var(--border-color);">
          <!-- Mon -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 35%; border-radius: 4px 4px 0 0; position:relative;" title="₹4,200">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹4.2k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Mon</span>
          </div>
          <!-- Tue -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 50%; border-radius: 4px 4px 0 0; position:relative;" title="₹6,800">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹6.8k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Tue</span>
          </div>
          <!-- Wed -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 80%; border-radius: 4px 4px 0 0; position:relative;" title="₹11,400">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹11.4k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Wed</span>
          </div>
          <!-- Thu -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 45%; border-radius: 4px 4px 0 0; position:relative;" title="₹5,900">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹5.9k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Thu</span>
          </div>
          <!-- Fri -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 75%; border-radius: 4px 4px 0 0; position:relative;" title="₹10,200">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹10.2k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Fri</span>
          </div>
          <!-- Sat -->
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; height:100%; justify-content:flex-end;">
            <div style="background: linear-gradient(to top, var(--primary-color), var(--accent-color)); width: 100%; height: 95%; border-radius: 4px 4px 0 0; position:relative;" title="₹14,900">
              <span style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); font-size:10px; font-weight:700;">₹14.9k</span>
            </div>
            <span style="font-size:11px; font-weight:700; color:var(--text-muted);">Sat</span>
          </div>
        </div>
      </div>
    `;
  }
  
  if (activeSellerTab === 'inventory') {
    return `
      <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">Supplier Inventory Catalog</h2>
      <div style="background-color:#fff; border-radius:12px; border:1px solid var(--border-light); padding:24px; box-shadow:var(--shadow-sm); display:flex; flex-direction:column; gap:16px;">
        ${products.map(p => {
          let imageHtml = '';
          if (p.image.startsWith('custom:')) {
            const gradientClass = `prod-image-gradient-${p.image.split(':')[1]}`;
            imageHtml = `<div class="cart-item-img procedural-placeholder ${gradientClass}" style="width:50px; height:50px; border-radius:6px; position:relative;"><i data-lucide="shirt" style="width:16px; height:16px; color:#fff;"></i></div>`;
          } else {
            imageHtml = `<img src="${p.image}" alt="${p.name}" style="width:50px; height:50px; object-fit:cover; border-radius:6px;">`;
          }
          
          return `
            <div class="d-flex justify-between align-center" style="border-bottom:1px solid var(--border-light); padding-bottom:12px; gap:12px;">
              <div class="d-flex align-center gap-2">
                ${imageHtml}
                <div>
                  <h4 style="font-size: 13px; font-weight: 700;">${p.name}</h4>
                  <div style="font-size: 11px; color: var(--text-muted); margin-top:2px;">Category: ${p.category} | Rating: ${p.rating} ★</div>
                </div>
              </div>
              <div class="d-flex align-center gap-3">
                <div style="text-align: right;">
                  <div style="font-weight:700; font-size:14px;">₹${p.price}</div>
                  <div style="font-size:11px; color:var(--text-light); text-decoration:line-through;">MRP: ₹${p.originalPrice}</div>
                </div>
                <button class="action-btn delete-seller-item" data-product-id="${p.id}" style="color:var(--error); padding: 8px;"><i data-lucide="trash-2" style="width:18px; height:18px;"></i></button>
              </div>
            </div>`;
        }).join('')}
      </div>`;
  }
  
  if (activeSellerTab === 'add_product') {
    return `
      <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 20px;">Upload New Product Catalog</h2>
      
      <div style="background-color:#fff; border-radius:12px; border:1px solid var(--border-light); padding:24px; box-shadow:var(--shadow-sm);">
        <form id="seller-add-product-form" style="display:flex; flex-direction:column; gap:16px;">
          
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Product Name / Title</label>
            <input type="text" class="form-control" id="add-prod-name" placeholder="e.g. Designer Embroidered Silk Lehenga" required>
          </div>
          
          <div class="d-flex gap-2">
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label class="form-label">Category</label>
              <select class="form-control" id="add-prod-category" required>
                <option value="Women Ethnic">Women Ethnic</option>
                <option value="Women Western">Women Western</option>
                <option value="Men">Men</option>
                <option value="Kids">Kids</option>
                <option value="Home & Kitchen">Home & Kitchen</option>
                <option value="Beauty & Health">Beauty & Health</option>
                <option value="Jewellery & Accessories">Jewellery & Accessories</option>
                <option value="Bags & Footwear">Bags & Footwear</option>
                <option value="Electronics">Electronics</option>
              </select>
            </div>
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label class="form-label">Subcategory / Item Type</label>
              <input type="text" class="form-control" id="add-prod-subcategory" placeholder="e.g. Sarees, Shirts, Bags" required>
            </div>
          </div>
          
          <div class="d-flex gap-2">
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label class="form-label">Wholesale Price (Your Earnings)</label>
              <input type="number" class="form-control" id="add-prod-price" placeholder="450" required>
            </div>
            <div class="form-group" style="flex:1; margin-bottom:0;">
              <label class="form-label">Original Maximum retail price (MRP)</label>
              <input type="number" class="form-control" id="add-prod-mrp" placeholder="999" required>
            </div>
          </div>

          <div class="form-group" style="margin-bottom: 0;">
            <label class="form-label">Sizes Available (Select all that apply)</label>
            <div style="display:flex; gap:16px;">
              <label class="d-flex align-center gap-1" style="font-size:13px; cursor:pointer;"><input type="checkbox" name="add-prod-sizes" value="S" style="width:16px; height:16px;"> S</label>
              <label class="d-flex align-center gap-1" style="font-size:13px; cursor:pointer;"><input type="checkbox" name="add-prod-sizes" value="M" style="width:16px; height:16px;"> M</label>
              <label class="d-flex align-center gap-1" style="font-size:13px; cursor:pointer;"><input type="checkbox" name="add-prod-sizes" value="L" style="width:16px; height:16px;"> L</label>
              <label class="d-flex align-center gap-1" style="font-size:13px; cursor:pointer;"><input type="checkbox" name="add-prod-sizes" value="XL" style="width:16px; height:16px;"> XL</label>
              <label class="d-flex align-center gap-1" style="font-size:13px; cursor:pointer;"><input type="checkbox" name="add-prod-sizes" value="Free Size" style="width:16px; height:16px;" checked> Free Size</label>
            </div>
          </div>

          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Product Detailed Description</label>
            <textarea class="form-control" id="add-prod-desc" rows="4" placeholder="Describe fabric quality, wash directions, stitching details, etc." required></textarea>
          </div>
          
          <div class="form-group" style="margin-bottom:0;">
            <label class="form-label">Catalog Cover Asset Styling</label>
            <div style="background-color:var(--bg-main); padding:16px; border-radius:8px; border:1px solid var(--border-color); display:flex; align-items:center; gap:12px;">
              <div style="background: linear-gradient(135deg, #8a2be2, #f43397); width:50px; height:50px; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#fff;"><i data-lucide="sparkles"></i></div>
              <div>
                <strong style="font-size:13px; display:block;">Smart Visual Gradient Cover</strong>
                <p style="font-size:11px; color:var(--text-muted); margin-top:2px;">Our engine automatically creates an aesthetic gradient card theme for newly launched catalogs.</p>
              </div>
            </div>
          </div>
          
          <button type="submit" class="btn-large btn-buy-now" style="font-size:15px; margin-top:10px; width:220px; align-self:flex-start;">Publish Product</button>
        </form>
      </div>`;
  }
  return '';
}

function wireUpSellerEvents(container) {
  // Sidebar tab switcher triggers
  container.querySelectorAll("[data-seller-tab]").forEach(btn => {
    btn.addEventListener("click", () => {
      container.querySelectorAll("[data-seller-tab]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeSellerTab = btn.dataset.sellerTab;
      
      const content = document.getElementById("seller-tab-content");
      if (content) {
        const prod = db.getProducts();
        const orders = db.getOrders();
        const sales = orders.reduce((sum, o) => sum + o.totals.finalAmount, 0) + 24800;
        
        content.innerHTML = renderSellerTabContent(prod, sales, orders.length + 42, prod.length);
        lucide.createIcons();
        wireUpTabSpecificEvents(content);
      }
    });
  });
  
  const content = document.getElementById("seller-tab-content");
  if (content) {
    wireUpTabSpecificEvents(content);
  }
}

function wireUpTabSpecificEvents(content) {
  // Inventory product delete click
  content.querySelectorAll(".delete-seller-item").forEach(btn => {
    btn.addEventListener("click", () => {
      if (confirm("Are you sure you want to delete this product listing from the global Kraya database?")) {
        const prodId = Number(btn.dataset.productId);
        db.deleteProduct(prodId);
        
        // Refresh tab
        const products = db.getProducts();
        const orders = db.getOrders();
        const sales = orders.reduce((sum, o) => sum + o.totals.finalAmount, 0) + 24800;
        
        content.innerHTML = renderSellerTabContent(products, sales, orders.length + 42, products.length);
        lucide.createIcons();
        wireUpTabSpecificEvents(content);
      }
    });
  });
  
  // Submit add product form
  const addForm = document.getElementById("seller-add-product-form");
  if (addForm) {
    addForm.addEventListener("submit", (e) => {
      e.preventDefault();
      
      const sizesArray = [];
      document.querySelectorAll("input[name='add-prod-sizes']:checked").forEach(cb => {
        sizesArray.push(cb.value);
      });
      
      if (sizesArray.length === 0) {
        alert("Please select at least one available size!");
        return;
      }
      
      const name = document.getElementById("add-prod-name").value.trim();
      const category = document.getElementById("add-prod-category").value;
      const subcategory = document.getElementById("add-prod-subcategory").value.trim();
      const price = Number(document.getElementById("add-prod-price").value);
      const mrp = Number(document.getElementById("add-prod-mrp").value);
      const desc = document.getElementById("add-prod-desc").value.trim();
      
      if (price > mrp) {
        alert("Wholesale price cannot exceed the original MRP!");
        return;
      }
      
      const discount = Math.round(((mrp - price) / mrp) * 100);
      
      const newProduct = {
        name: name,
        description: desc,
        price: price,
        originalPrice: mrp,
        discount: discount,
        image: "custom:gradient_added",
        images: ["custom:gradient_added"],
        category: category,
        subcategory: subcategory,
        sizes: sizesArray,
        freeDelivery: true,
        codAvailable: true,
        seller: {
          name: "Kraya Supplier Hub",
          rating: 4.5,
          followers: 120,
          productCount: 1
        },
        details: {
          "Fabric/Material": "Premium selected blend",
          "Color": "Multicolor",
          "Pattern": "Modern design",
          "Brand": "Supplier Verified"
        }
      };
      
      // Save product
      db.addProduct(newProduct);
      alert("Product published successfully! It is now active in the main shopping catalog.");
      
      // Navigate to inventory list
      activeSellerTab = 'inventory';
      window.location.reload();
    });
  }
}
