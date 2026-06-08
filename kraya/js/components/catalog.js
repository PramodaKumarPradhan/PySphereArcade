// Kraya Catalog Component
import { db } from '../db.js';
import { state, navigateToRoute } from '../app.js';

let carouselTimer = null;
let activeSlideIndex = 0;

export function render(container, params) {
  // Parse parameters from route
  const categoryParam = params.category || '';
  const subcategoryParam = params.subcategory || '';
  const searchParam = params.q || '';
  
  // Update state filters
  state.filters.category = categoryParam;
  state.filters.subcategory = subcategoryParam;
  state.searchQuery = searchParam;
  
  const products = db.getProducts();
  const filteredProducts = filterAndSortProducts(products);
  
  let html = `
    <div class="container">
  `;
  
  // Render Carousel Banner only on main home shop or category main
  if (!searchParam && !subcategoryParam) {
    html += renderBannerCarousel();
  }
  
  // Render Value Props only if not deep searching
  if (!searchParam) {
    html += `
      <div class="value-props">
        <div class="prop-item">
          <div class="prop-icon"><i data-lucide="truck"></i></div>
          <div class="prop-text">
            <h4>Free Delivery</h4>
            <p>On all orders over ₹299</p>
          </div>
        </div>
        <div class="prop-item">
          <div class="prop-icon"><i data-lucide="hand-coins"></i></div>
          <div class="prop-text">
            <h4>Cash on Delivery</h4>
            <p>100% safe payment</p>
          </div>
        </div>
        <div class="prop-item">
          <div class="prop-icon"><i data-lucide="rotate-ccw"></i></div>
          <div class="prop-text">
            <h4>Easy Returns</h4>
            <p>7-day return policy</p>
          </div>
        </div>
      </div>
    `;
  }
  
  // Main Catalog Layout
  html += `
    <div class="catalog-layout">
      <!-- Left Filters panel -->
      <aside class="filters-panel">
        <div class="filters-title-main">
          <span>Filters</span>
          <button class="clear-filters-btn" id="catalog-clear-filters">Reset</button>
        </div>
        
        <!-- Category Filter -->
        <div class="filter-section">
          <h4 class="filter-section-title">Category</h4>
          <div class="filter-options">
            ${renderCategoryFilters(products)}
          </div>
        </div>
        
        <!-- Price Filter -->
        <div class="filter-section">
          <h4 class="filter-section-title">Price Range</h4>
          <div class="filter-options">
            <label class="filter-checkbox-label">
              <input type="radio" name="price-range" class="filter-price-radio" value="all" ${state.filters.priceMax === 5000 && state.filters.priceMin === 0 ? 'checked' : ''}>
              All Prices
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="price-range" class="filter-price-radio" value="under-499" ${state.filters.priceMax === 499 ? 'checked' : ''}>
              Under ₹499
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="price-range" class="filter-price-radio" value="500-999" ${state.filters.priceMin === 500 && state.filters.priceMax === 999 ? 'checked' : ''}>
              ₹500 - ₹999
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="price-range" class="filter-price-radio" value="1000-1999" ${state.filters.priceMin === 1000 && state.filters.priceMax === 1999 ? 'checked' : ''}>
              ₹1000 - ₹1999
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="price-range" class="filter-price-radio" value="above-2000" ${state.filters.priceMin === 2000 ? 'checked' : ''}>
              Over ₹2000
            </label>
          </div>
        </div>
        
        <!-- Rating Filter -->
        <div class="filter-section">
          <h4 class="filter-section-title">Customer Rating</h4>
          <div class="filter-options">
            <label class="filter-checkbox-label">
              <input type="radio" name="rating-filter" class="filter-rating-radio" value="0" ${state.filters.rating === 0 ? 'checked' : ''}>
              All Ratings
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="rating-filter" class="filter-rating-radio" value="4" ${state.filters.rating === 4 ? 'checked' : ''}>
              4.0 ★ & Above
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="rating-filter" class="filter-rating-radio" value="3" ${state.filters.rating === 3 ? 'checked' : ''}>
              3.0 ★ & Above
            </label>
          </div>
        </div>

        <!-- Sizes Filter -->
        <div class="filter-section">
          <h4 class="filter-section-title">Sizes</h4>
          <div class="filter-options" style="flex-direction: row; flex-wrap: wrap; gap: 8px;">
            ${['S', 'M', 'L', 'XL', 'Free Size'].map(sz => `
              <button class="size-option-btn filter-size-btn ${state.filters.sizes.includes(sz) ? 'selected' : ''}" data-size="${sz}">${sz}</button>
            `).join('')}
          </div>
        </div>
      </aside>
      
      <!-- Right Grid content -->
      <section class="catalog-content">
        <!-- Top Toolbar -->
        <div class="catalog-toolbar d-flex align-center justify-between">
          <div class="results-count">
            ${searchParam ? `Search results for "<strong>${searchParam}</strong>" : ` : ''}
            Showing <strong>${filteredProducts.length}</strong> items
          </div>
          
          <div class="sort-container">
            <span style="font-size: 14px; color: var(--text-muted);">Sort By:</span>
            <select class="sort-select" id="catalog-sort-select">
              <option value="relevance" ${state.sortBy === 'relevance' ? 'selected' : ''}>Relevance</option>
              <option value="priceAsc" ${state.sortBy === 'priceAsc' ? 'selected' : ''}>Price: Low to High</option>
              <option value="priceDesc" ${state.sortBy === 'priceDesc' ? 'selected' : ''}>Price: High to Low</option>
              <option value="ratingDesc" ${state.sortBy === 'ratingDesc' ? 'selected' : ''}>Customer Rating</option>
            </select>
          </div>
        </div>
        
        <!-- Grid Items -->
        <div class="product-grid" id="catalog-product-grid">
          ${renderProductGrid(filteredProducts)}
        </div>
      </section>
    </div>
  </div>
  `;
  
  container.innerHTML = html;
  
  // Initialize Carousel functionality
  if (!searchParam && !subcategoryParam) {
    initBannerCarousel();
  }
  
  // Wire up action filters events
  wireUpEvents(container, products);
}

// Banner Slide list
function renderBannerCarousel() {
  const slides = [
    {
      title: "Lowest Prices, Best Quality Fashion",
      desc: "Shop traditional sarees, kurtis, men's wear and kids sets starting from ₹199.",
      btnText: "Shop Sarees",
      hash: "#catalog?category=Women%20Ethnic",
      class: "banner-gradient-1"
    },
    {
      title: "Become a Smart Kraya Reseller",
      desc: "Share high quality designs on WhatsApp, set custom margins, and start earning weekly.",
      btnText: "Start Reselling",
      hash: "#catalog?category=Electronics",
      class: "banner-gradient-2"
    },
    {
      title: "Revamp Your Cozy Homes",
      desc: "Get cotton double bedsheets, organizers, and kitchen appliances at up to 70% off.",
      btnText: "Explore Home Shop",
      hash: "#catalog?category=Home%20%26%20Kitchen",
      class: "banner-gradient-3"
    }
  ];
  
  let html = `
    <div class="banner-carousel" id="catalog-banner-carousel">
      ${slides.map((s, idx) => `
        <div class="banner-slide ${s.class} ${idx === activeSlideIndex ? 'active' : ''}">
          <div class="banner-content">
            <h2 class="banner-title">${s.title}</h2>
            <p class="banner-desc">${s.desc}</p>
            <a href="${s.hash}" class="banner-btn">${s.btnText}</a>
          </div>
        </div>
      `).join('')}
      <button class="banner-prev" id="banner-prev-btn"><i data-lucide="chevron-left"></i></button>
      <button class="banner-next" id="banner-next-btn"><i data-lucide="chevron-right"></i></button>
    </div>
  `;
  
  return html;
}

function initBannerCarousel() {
  const carousel = document.getElementById("catalog-banner-carousel");
  if (!carousel) return;
  
  const slides = carousel.querySelectorAll(".banner-slide");
  const prevBtn = document.getElementById("banner-prev-btn");
  const nextBtn = document.getElementById("banner-next-btn");
  
  const showSlide = (index) => {
    slides.forEach(s => s.classList.remove("active"));
    activeSlideIndex = (index + slides.length) % slides.length;
    slides[activeSlideIndex].classList.add("active");
  };
  
  prevBtn.addEventListener("click", () => {
    showSlide(activeSlideIndex - 1);
    resetCarouselTimer();
  });
  
  nextBtn.addEventListener("click", () => {
    showSlide(activeSlideIndex + 1);
    resetCarouselTimer();
  });
  
  const startCarouselTimer = () => {
    carouselTimer = setInterval(() => {
      showSlide(activeSlideIndex + 1);
    }, 5000);
  };
  
  const resetCarouselTimer = () => {
    if (carouselTimer) {
      clearInterval(carouselTimer);
      startCarouselTimer();
    }
  };
  
  startCarouselTimer();
}

// Render dynamic category filter counts
function renderCategoryFilters(products) {
  const counts = {};
  products.forEach(p => {
    counts[p.category] = (counts[p.category] || 0) + 1;
  });
  
  let html = '';
  for (const [cat, count] of Object.entries(counts)) {
    const isSelected = state.filters.category === cat;
    html += `
      <label class="filter-checkbox-label">
        <input type="radio" name="category-filter" class="filter-category-radio" value="${cat}" ${isSelected ? 'checked' : ''}>
        ${cat} (${count})
      </label>
    `;
  }
  return html;
}

// Filter core calculation logic
function filterAndSortProducts(products) {
  let list = [...products];
  
  // Category filter
  if (state.filters.category) {
    list = list.filter(p => p.category === state.filters.category);
  }
  
  // Subcategory filter
  if (state.filters.subcategory) {
    list = list.filter(p => p.subcategory === state.filters.subcategory);
  }
  
  // Search query filter
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(p => 
      p.name.toLowerCase().includes(q) || 
      p.category.toLowerCase().includes(q) || 
      p.subcategory.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q)
    );
  }
  
  // Price range filters
  list = list.filter(p => p.price >= state.filters.priceMin && p.price <= state.filters.priceMax);
  
  // Rating filter
  if (state.filters.rating > 0) {
    list = list.filter(p => p.rating >= state.filters.rating);
  }
  
  // Sizes filter (displays items containing selected sizes)
  if (state.filters.sizes.length > 0) {
    list = list.filter(p => p.sizes.some(s => state.filters.sizes.includes(s)));
  }
  
  // Sorting calculation
  if (state.sortBy === 'priceAsc') {
    list.sort((a, b) => a.price - b.price);
  } else if (state.sortBy === 'priceDesc') {
    list.sort((a, b) => b.price - a.price);
  } else if (state.sortBy === 'ratingDesc') {
    list.sort((a, b) => b.rating - a.rating);
  }
  
  return list;
}

// Render product card grid list
function renderProductGrid(products) {
  if (products.length === 0) {
    return `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-light); display: flex; flex-direction: column; align-items: center; gap: 12px;">
        <i data-lucide="info" style="width: 48px; height: 48px; stroke-width: 1.5;"></i>
        <p style="font-size: 16px; font-weight: 600;">No Products Match Your Filter Selections</p>
        <p style="font-size: 13px;">Try clearing filters or search queries to discover products.</p>
      </div>`;
  }
  
  return products.map(p => {
    const isLiked = db.isInWishlist(p.id);
    
    // Check if the image path is a procedural styling code
    let imageElement = '';
    if (p.image.startsWith('custom:')) {
      const gradientClass = `prod-image-gradient-${p.image.split(':')[1]}`;
      imageElement = `
        <div class="product-card-img procedural-placeholder ${gradientClass}">
          <i data-lucide="shirt" style="width: 36px; height: 36px; stroke-width: 1.2;"></i>
        </div>`;
    } else {
      imageElement = `<img src="${p.image}" alt="${p.name}" class="product-card-img">`;
    }
    
    return `
      <div class="product-card" data-product-id="${p.id}">
        <!-- Image Box -->
        <div class="card-img-container" onclick="window.location.hash = '#product/${p.id}'">
          ${imageElement}
          ${p.category.includes('Ethnic') || p.category.includes('Electronics') ? `
            <div class="card-badge-container">
              <span class="reseller-badge">Weekly Earn</span>
            </div>
          ` : ''}
        </div>
        
        <!-- Wishlist Button -->
        <button class="wishlist-icon-btn ${isLiked ? 'liked' : ''}" data-product-id="${p.id}">
          <i data-lucide="heart" style="width: 18px; height: 18px; fill: ${isLiked ? 'currentColor' : 'none'};"></i>
        </button>
        
        <!-- Information Box -->
        <div class="card-info" onclick="window.location.hash = '#product/${p.id}'">
          <h3 class="product-card-title">${p.name}</h3>
          
          <div class="price-row">
            <span class="card-price">₹${p.price}</span>
            ${p.originalPrice > p.price ? `
              <span class="card-orig-price">₹${p.originalPrice}</span>
              <span class="card-discount">${p.discount}% off</span>
            ` : ''}
          </div>
          
          <div class="card-delivery-badge">
            ${p.freeDelivery ? 'Free Delivery' : 'Delivery ₹40'}
          </div>
          
          <div class="card-rating-row">
            <span class="rating-pill">${p.rating} <i data-lucide="star" style="width: 10px; height: 10px; fill: currentColor;"></i></span>
            <span class="reviews-cnt">${p.reviewsCount} Reviews</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Dynamic Filter Action Event Listeners
function wireUpEvents(container, allProducts) {
  const refilterCatalog = () => {
    const list = filterAndSortProducts(allProducts);
    const grid = document.getElementById("catalog-product-grid");
    if (grid) {
      grid.innerHTML = renderProductGrid(list);
      lucide.createIcons();
    }
    
    // Update count labels
    const countLabel = container.querySelector(".results-count strong");
    if (countLabel) {
      countLabel.textContent = list.length;
    }
  };
  
  // Category Radio Selection
  container.querySelectorAll(".filter-category-radio").forEach(radio => {
    radio.addEventListener("change", (e) => {
      state.filters.category = e.target.value;
      state.filters.subcategory = ''; // Reset sub
      // Maintain link sync by redirecting
      navigateToRoute(`#catalog?category=${encodeURIComponent(e.target.value)}`);
    });
  });
  
  // Price Range Radios Selection
  container.querySelectorAll(".filter-price-radio").forEach(radio => {
    radio.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val === 'all') {
        state.filters.priceMin = 0;
        state.filters.priceMax = 5000;
      } else if (val === 'under-499') {
        state.filters.priceMin = 0;
        state.filters.priceMax = 499;
      } else if (val === '500-999') {
        state.filters.priceMin = 500;
        state.filters.priceMax = 999;
      } else if (val === '1000-1999') {
        state.filters.priceMin = 1000;
        state.filters.priceMax = 1999;
      } else if (val === 'above-2000') {
        state.filters.priceMin = 2000;
        state.filters.priceMax = 5000;
      }
      refilterCatalog();
    });
  });
  
  // Customer Rating Radios Selection
  container.querySelectorAll(".filter-rating-radio").forEach(radio => {
    radio.addEventListener("change", (e) => {
      state.filters.rating = Number(e.target.value);
      refilterCatalog();
    });
  });
  
  // Size Button Filters Multi-Selection
  container.querySelectorAll(".filter-size-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const sz = btn.dataset.size;
      const index = state.filters.sizes.indexOf(sz);
      if (index !== -1) {
        state.filters.sizes.splice(index, 1);
        btn.classList.remove("selected");
      } else {
        state.filters.sizes.push(sz);
        btn.classList.add("selected");
      }
      refilterCatalog();
    });
  });
  
  // Sort selection dropdown change
  const sortSelect = document.getElementById("catalog-sort-select");
  if (sortSelect) {
    sortSelect.addEventListener("change", (e) => {
      state.sortBy = e.target.value;
      refilterCatalog();
    });
  }
  
  // Clear filters
  const resetBtn = document.getElementById("catalog-clear-filters");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      state.filters.category = '';
      state.filters.subcategory = '';
      state.filters.priceMin = 0;
      state.filters.priceMax = 5000;
      state.filters.rating = 0;
      state.filters.sizes = [];
      state.searchQuery = '';
      state.sortBy = 'relevance';
      navigateToRoute('#catalog');
    });
  }
  
  // Card wishlist click toggle
  container.querySelectorAll(".wishlist-icon-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation(); // Stop navigation click through card
      const prodId = btn.dataset.productId;
      const added = db.toggleWishlist(prodId);
      
      btn.classList.toggle("liked", added);
      const icon = btn.querySelector("i");
      if (icon) {
        icon.style.fill = added ? 'currentColor' : 'none';
      }
    });
  });
}
